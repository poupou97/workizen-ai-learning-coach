// OCR local bằng Apple Vision — KHÔNG gọi LLM.
//
// Vì sao Vision chứ không phải tesseract: (a) tesseract trên máy này thiếu gói
// tiếng Việt; (b) Vision LÀ engine sẽ chạy trên iOS trong sản phẩm, nên số đo
// chất lượng ở đây chuyển thẳng sang production thay vì phải đo lại.
//
// Xuất JSON từng DÒNG kèm bbox + confidence. Bbox là thứ cho phép suy ra cấu
// trúc (tiêu đề, số bài, số trang) bằng luật hình học — không cần LLM.
//
// Dùng: swift ocr_pdf.swift <pdf> <trang đầu> <trang cuối> <thư mục ra>

import Foundation
import PDFKit
import Vision
import CoreGraphics
import CryptoKit

let args = CommandLine.arguments
guard args.count >= 5, let first = Int(args[2]), let last = Int(args[3]) else {
    FileHandle.standardError.write("dùng: ocr_pdf <pdf> <first> <last> <outdir>\n".data(using: .utf8)!)
    exit(2)
}
let pdfPath = args[1], outDir = args[4]
guard let doc = PDFDocument(url: URL(fileURLWithPath: pdfPath)) else {
    FileHandle.standardError.write("không mở được PDF\n".data(using: .utf8)!); exit(1)
}
try? FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)

let scale: CGFloat = 3.0   // 100ppi×3. Thử 6× cho kết quả Y HỆT — nguồn 100ppi, phóng to không thêm thông tin.

for pageNo in first...min(last, doc.pageCount) {
    guard let page = doc.page(at: pageNo - 1) else { continue }
    let rect = page.bounds(for: .mediaBox)
    let w = Int(rect.width * scale), h = Int(rect.height * scale)

    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
        bytesPerRow: 0, space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { continue }
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: ctx)
    guard let cg = ctx.makeImage() else { continue }

    // Hash NỘI DUNG ẢNH ⇒ cache đúng theo §7: source không đổi thì không OCR lại.
    var hasher = SHA256()
    if let dp = cg.dataProvider, let d = dp.data { hasher.update(data: d as Data) }
    let hash = hasher.finalize().map { String(format: "%02x", $0) }.joined().prefix(16)

    let outPath = "\(outDir)/p\(String(format: "%03d", pageNo)).json"
    if let existing = try? Data(contentsOf: URL(fileURLWithPath: outPath)),
       let obj = try? JSONSerialization.jsonObject(with: existing) as? [String: Any],
       obj["source_hash"] as? String == String(hash) {
        print("p\(pageNo) CACHED"); continue
    }

    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.recognitionLanguages = ["vi-VT", "en-US"]
    req.usesLanguageCorrection = true
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])

    var lines: [[String: Any]] = []
    for obs in (req.results ?? []) {
        guard let c = obs.topCandidates(1).first else { continue }
        let b = obs.boundingBox   // gốc toạ độ dưới-trái, đã chuẩn hoá 0..1
        lines.append([
            "text": c.string,
            "conf": Double(c.confidence),
            "x": Double(b.minX), "y": Double(1 - b.maxY),
            "w": Double(b.width), "h": Double(b.height),
        ])
    }
    // sắp theo thứ tự đọc: trên→dưới, trái→phải
    lines.sort {
        let y0 = $0["y"] as! Double, y1 = $1["y"] as! Double
        return abs(y0 - y1) > 0.012 ? y0 < y1 : ($0["x"] as! Double) < ($1["x"] as! Double)
    }
    let payload: [String: Any] = [
        "pdf_page": pageNo, "source_hash": String(hash),
        "extraction_method": "apple-vision-accurate-vi",
        "line_count": lines.count, "lines": lines,
    ]
    try? JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted, .sortedKeys])
        .write(to: URL(fileURLWithPath: outPath))
    let avg = lines.isEmpty ? 0 : lines.map { $0["conf"] as! Double }.reduce(0,+) / Double(lines.count)
    print("p\(pageNo) OCR \(lines.count) dòng · conf tb \(String(format: "%.2f", avg))")
}

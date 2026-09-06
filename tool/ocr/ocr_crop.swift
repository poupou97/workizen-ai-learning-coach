// Apple Vision on a REGION of a page, not on the whole page — KHÔNG gọi LLM.
//
// Vì sao tồn tại: `tool/ocr/ocr_pdf.swift` OCR cả trang một lần, ở scale 3.0, với
// `usesLanguageCorrection = true` và ngôn ngữ vi-VT. Đó là quan sát duy nhất mà toàn bộ
// pipeline có. Round 5 đo được: 274/336 khối chứa phân số không sửa được vì **OCR chưa
// bao giờ đọc chữ số đó**. Câu hỏi round 6 là: nếu đưa cho Vision đúng vùng in đó, một
// mình, ở scale lớn hơn, và TẮT sửa lỗi ngôn ngữ — nó có đọc ra chữ số không?
//
// Đây là MỘT QUAN SÁT KHÁC, không phải chân lý. Kết quả của nó là RepairCandidate và
// phải đi qua các validator tất định của `tool/corpus/mathfix/validate.py`.
//
// Ghi chú quan trọng về độ phân giải: mọi trang SGK trong corpus là **ảnh quét 100 ppi**
// nhúng trong PDF (đo: 1094×1536 px trên khổ 787.68×1105.92 pt). Phóng to KHÔNG thêm
// thông tin pixel. Cái mà crop thay đổi là (a) ngữ cảnh — Vision không còn thấy văn xuôi
// quanh biểu thức để "sửa" theo ngôn ngữ, (b) tỉ lệ chữ trên khung ảnh, (c) tham số nhận
// dạng. Ba thứ đó là giả thuyết được đo, không phải "ảnh nét hơn".
//
// Dùng:  ocr_crop <jobs.json> <out.json>
//
// jobs.json:
// {
//   "defaults": {"scale": 6.0, "languageCorrection": false, "languages": ["en-US"],
//                "level": "accurate", "minTextHeight": 0.0, "pad": 0.01, "invert": false},
//   "jobs": [{"id": "...", "pdf": "/abs/path.pdf", "page": 22,
//             "bbox": [x0, y0, x1, y1]}]        // chuẩn hoá 0..1, y tính từ TRÊN xuống
// }
//
// out.json: {"results": [{"id", "crop_px":[w,h], "crop_pt":[w,h], "lines":[{text,conf,x,y,w,h}]}]}
// Toạ độ dòng chuẩn hoá theo CROP, y tính từ trên xuống — cùng quy ước với ocr_pdf.swift.

import Foundation
import PDFKit
import Vision
import CoreGraphics

let args = CommandLine.arguments
guard args.count >= 3 else {
    FileHandle.standardError.write("dùng: ocr_crop <jobs.json> <out.json>\n".data(using: .utf8)!)
    exit(2)
}

guard let jobData = FileManager.default.contents(atPath: args[1]),
      let root = (try? JSONSerialization.jsonObject(with: jobData)) as? [String: Any],
      let jobs = root["jobs"] as? [[String: Any]] else {
    FileHandle.standardError.write("không đọc được jobs.json\n".data(using: .utf8)!)
    exit(1)
}
let defaults = (root["defaults"] as? [String: Any]) ?? [:]

func num(_ job: [String: Any], _ key: String, _ fallback: Double) -> Double {
    if let v = job[key] as? Double { return v }
    if let v = job[key] as? Int { return Double(v) }
    if let v = defaults[key] as? Double { return v }
    if let v = defaults[key] as? Int { return Double(v) }
    return fallback
}
func flag(_ job: [String: Any], _ key: String, _ fallback: Bool) -> Bool {
    if let v = job[key] as? Bool { return v }
    if let v = defaults[key] as? Bool { return v }
    return fallback
}
func str(_ job: [String: Any], _ key: String, _ fallback: String) -> String {
    if let v = job[key] as? String { return v }
    if let v = defaults[key] as? String { return v }
    return fallback
}
func strs(_ job: [String: Any], _ key: String, _ fallback: [String]) -> [String] {
    if let v = job[key] as? [String] { return v }
    if let v = defaults[key] as? [String] { return v }
    return fallback
}

// Mở mỗi PDF một lần: 62 729 trang trong corpus, mở lại từng job là lãng phí thuần.
var docs: [String: PDFDocument] = [:]
func document(_ path: String) -> PDFDocument? {
    if let d = docs[path] { return d }
    guard let d = PDFDocument(url: URL(fileURLWithPath: path)) else { return nil }
    docs[path] = d
    return d
}

var results: [[String: Any]] = []

for job in jobs {
    let id = (job["id"] as? String) ?? "?"
    guard let pdf = (job["pdf"] as? String) ?? (defaults["pdf"] as? String),
          let pageNo = job["page"] as? Int,
          let bbox = job["bbox"] as? [Double], bbox.count == 4,
          let doc = document(pdf), let page = doc.page(at: pageNo - 1) else {
        results.append(["id": id, "error": "bad job"]); continue
    }

    let rect = page.bounds(for: .mediaBox)
    let pad = num(job, "pad", 0.01)
    let scale = CGFloat(num(job, "scale", 6.0))

    // bbox chuẩn hoá, y từ trên xuống → điểm PDF, gốc dưới-trái.
    var x0 = max(0.0, bbox[0] - pad), x1 = min(1.0, bbox[2] + pad)
    var yTop = max(0.0, bbox[1] - pad), yBot = min(1.0, bbox[3] + pad)
    if x1 <= x0 { x1 = min(1.0, x0 + 0.002) }
    if yBot <= yTop { yBot = min(1.0, yTop + 0.002) }
    let cropX = CGFloat(x0) * rect.width
    let cropY = rect.height - CGFloat(yBot) * rect.height     // cạnh dưới, gốc dưới-trái
    let cropW = CGFloat(x1 - x0) * rect.width
    let cropH = CGFloat(yBot - yTop) * rect.height

    let w = max(8, Int((cropW * scale).rounded(.up)))
    let h = max(8, Int((cropH * scale).rounded(.up)))
    guard w * h <= 60_000_000, let ctx = CGContext(
        data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else {
        results.append(["id": id, "error": "context"]); continue
    }
    ctx.interpolationQuality = .high
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale)
    ctx.translateBy(x: -cropX, y: -cropY)
    page.draw(with: .mediaBox, to: ctx)
    guard let cg = ctx.makeImage() else {
        results.append(["id": id, "error": "image"]); continue
    }

    let req = VNRecognizeTextRequest()
    req.recognitionLevel = (str(job, "level", "accurate") == "fast") ? .fast : .accurate
    let langs = strs(job, "languages", ["en-US"])
    if langs.isEmpty {
        if #available(macOS 13.0, *) { req.automaticallyDetectsLanguage = true }
    } else {
        req.recognitionLanguages = langs
    }
    req.usesLanguageCorrection = flag(job, "languageCorrection", false)
    req.minimumTextHeight = Float(num(job, "minTextHeight", 0.0))
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])

    var lines: [[String: Any]] = []
    for obs in (req.results ?? []) {
        // topCandidates(n) — mọi ứng viên đều là QUAN SÁT, không phải chân lý; số 3 để
        // `recrop.py` có thể đo «chữ số đúng có nằm trong tập ứng viên không» tách khỏi
        // «Vision có xếp nó hạng nhất không».
        let cands = obs.topCandidates(3)
        guard let c = cands.first else { continue }
        let b = obs.boundingBox
        lines.append([
            "text": c.string,
            "conf": Double(c.confidence),
            "alts": cands.dropFirst().map { ["text": $0.string, "conf": Double($0.confidence)] },
            "x": Double(b.minX), "y": Double(1 - b.maxY),
            "w": Double(b.width), "h": Double(b.height),
        ])
    }
    lines.sort {
        let y0 = $0["y"] as! Double, y1 = $1["y"] as! Double
        return abs(y0 - y1) > 0.08 ? y0 < y1 : ($0["x"] as! Double) < ($1["x"] as! Double)
    }
    results.append([
        "id": id, "crop_px": [w, h], "crop_pt": [Double(cropW), Double(cropH)],
        "bbox_used": [x0, yTop, x1, yBot],
        "scale": Double(scale), "languageCorrection": flag(job, "languageCorrection", false),
        "languages": langs, "level": str(job, "level", "accurate"),
        "engine": "apple-vision-crop-v1",
        "line_count": lines.count, "lines": lines,
    ])
}

let payload: [String: Any] = ["result_count": results.count, "results": results]
let out = try! JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted, .sortedKeys])
try! out.write(to: URL(fileURLWithPath: args[2]))
print("ocr_crop: \(results.count) results -> \(args[2])")

# CI — «Học cùng SAM» (WAL-163)

## Cổng là gì

Một job duy nhất trên `ubuntu-latest`: `flutter analyze` (ngưỡng mặc định) +
`flutter test` (toàn bộ suite). Chạy khi push `main` và trên mọi Pull Request.
Không build APK, không ký, không deploy, không secrets.

## Vì sao hẹp thế mà vẫn đáng có

Suite này không chỉ kiểm hàm — nó chở **luật bất biến của sản phẩm**, loại luật
vỡ mà app vẫn chạy bình thường nên không ai thấy:

| Luật | Test giữ nó |
|---|---|
| Không %/điểm/XP/streak trong UI của trẻ | quét chuỗi trong `lib/features/**` |
| Không SDK quảng cáo/analytics | quét `pubspec.yaml` |
| PAYMENT ≠ LEARNING TRUTH | cấm chữ subscription/premium/tier trong `lib/core/{student,adaptive,curriculum,tutor,pedagogy}` |
| Không bịa trích dẫn SGK | `CITATION_FABRICATION` trong `validateTutorOutput` |
| UNKNOWN ≠ SAI | claim-gate của `ConceptSummary`/`explainConcept` |

Trước CI, các luật này chỉ được giữ bằng «nhớ chạy `flutter test` trước khi
merge». Giờ vỡ là đỏ.

## Corpus và asset

`pubspec.yaml` khai báo `assets/pack/`, nhưng nội dung pack (SGK đã xử lý,
`lesson-index-*.json`, `sam-stories.db`, PNG bản đồ) **không bao giờ vào repo**
(WAL-43). Checkout sạch vẫn có `assets/pack/.gitignore` được track nên thư mục
tồn tại và `flutter pub get` không gãy. Test nào cần asset thật thì tự
`markTestSkipped` — runner không có corpus là **đúng thiết kế**.

Hệ quả phải nhớ: CI xanh **không** chứng minh phần phụ thuộc corpus còn chạy.
Phần đó chỉ chứng minh được bằng máy thật (xem walk device trong Jira).

## Phiên bản Flutter

Pin cứng trong `ci.yml`:

```
FLUTTER_VERSION: "3.48.0-0.3.pre"
FLUTTER_CHANNEL: "main"
```

`pubspec.yaml` yêu cầu `sdk: ^3.13.0-201.0.dev`. Đừng hạ về `stable` cho
«ổn định hơn» — stable có thể mang Dart cũ hơn và `flutter pub get` gãy ngay.
Khi nâng toolchain ở máy, sửa pin này cùng lúc.

## Khi CI đỏ

Sửa code, đừng nới ngưỡng. Không thêm `--no-fatal-warnings`, không `continue-on-error`,
không skip test cho qua cổng. Nếu một test sai chứ không phải code sai, sửa test
và nói rõ vì sao trong commit — CI free không phải lý do để hạ chuẩn kiểm chứng.

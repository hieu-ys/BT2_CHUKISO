BÀI TẬP VỀ NHÀ – MÔN: AN TOÀN VÀ BẢO MẬT THÔNG TIN
Chủ đề: Chữ ký số trong file PDF
Giảng viên: Đỗ Duy Cốp
Thời điểm giao: 2025-10-24 11:45
Đối tượng áp dụng: Toàn bộ sv lớp học phần 58KTPM
Hạn nộp: Sv upload tất cả lên github trước 2025-10-31 23:59:59
--
I. MÔ TẢ CHUNG
Sinh viên thực hiện báo cáo và thực hành: phân tích và hiện thực việc nhúng, xác
thực chữ ký số trong file PDF.
Phải nêu rõ chuẩn tham chiếu (PDF 1.7 / PDF 2.0, PAdES/ETSI) và sử dụng công cụ
thực thi (ví dụ iText7, OpenSSL, PyPDF, pdf-lib).

II. CÁC YÊU CẦU CỤ THỂ
1) Cấu trúc PDF liên quan chữ ký (Nghiên cứu)
- Mô tả ngắn gọn: Catalog, Pages tree, Page object, Resources, Content streams,
XObject, AcroForm, Signature field (widget), Signature dictionary (/Sig),
/ByteRange, /Contents, incremental updates, và DSS (theo PAdES).
- Liệt kê object refs quan trọng và giải thích vai trò của từng object trong
lưu/truy xuất chữ ký.
- Đầu ra: 1 trang tóm tắt + sơ đồ object (ví dụ: Catalog → Pages → Page → /Contents
; Catalog → /AcroForm → SigField → SigDict).
2) Thời gian ký được lưu ở đâu?
- Nêu tất cả vị trí có thể lưu thông tin thời gian:
+ /M trong Signature dictionary (dạng text, không có giá trị pháp lý).
+ Timestamp token (RFC 3161) trong PKCS#7 (attribute timeStampToken).
+ Document timestamp object (PAdES).
+ DSS (Document Security Store) nếu có lưu timestamp và dữ liệu xác minh.
- Giải thích khác biệt giữa thông tin thời gian /M và timestamp RFC3161.
3) Các bước tạo và lưu chữ ký trong PDF (đã có private RSA)
- Viết script/code thực hiện tuần tự:
1. Chuẩn bị file PDF gốc.
2. Tạo Signature field (AcroForm), reserve vùng /Contents (8192 bytes).
3. Xác định /ByteRange (loại trừ vùng /Contents khỏi hash).
4. Tính hash (SHA-256/512) trên vùng ByteRange.
5. Tạo PKCS#7/CMS detached hoặc CAdES:
- Include messageDigest, signingTime, contentType.
- Include certificate chain.
- (Tùy chọn) thêm RFC3161 timestamp token.
6. Chèn blob DER PKCS#7 vào /Contents (hex/binary) đúng offset.
7. Ghi incremental update.
8. (LTV) Cập nhật DSS với Certs, OCSPs, CRLs, VRI.
- Phải nêu rõ: hash alg, RSA padding, key size, vị trí lưu trong PKCS#7.
- Đầu ra: mã nguồn, file PDF gốc, file PDF đã ký.4) Các bước xác thực chữ ký trên PDF đã ký
- Các bước kiểm tra:
1. Đọc Signature dictionary: /Contents, /ByteRange.
2. Tách PKCS#7, kiểm tra định dạng.
3. Tính hash và so sánh messageDigest.
4. Verify signature bằng public key trong cert.
5. Kiểm tra chain → root trusted CA.
6. Kiểm tra OCSP/CRL.
7. Kiểm tra timestamp token.
8. Kiểm tra incremental update (phát hiện sửa đổi).
- Nộp kèm script verify + log kiểm thử.

-----------------------------------------------------------------------------------------------
1. Các công cụ sử dung: <br>
- Visual Studio code<br>
- Python<br>
- OpenSSL<br>
2. Quy trình thực hiện kí chữ kí số và xác thực chữ kí số:<br>
  - Tải xuống và cài đặt Git Bash ( đã bao gồm cả OpenSSL):<br>
  <img width="744" height="448" alt="image" src="https://github.com/user-attachments/assets/590d4986-eda0-4a38-a379-7e4c5ddfa3cc" /><br>

- Tạo 1 tệp chứa dự án chữ kí số: <br>

<img width="871" height="180" alt="image" src="https://github.com/user-attachments/assets/c7f573a9-aeec-4b2b-a6a3-4c97f96ecc7d" /><br>

- Chuẩn bị trước 1 file PDF có nội dung đầy đủ và cấu trúc chuẩn ISO 32000-2:<br>
  <img width="1243" height="746" alt="image" src="https://github.com/user-attachments/assets/07f84dcc-4695-4636-8f61-f8eced851e2d" /><br>

- Mở Visual Studio code, open folder dự án vừa tạo, chuyển file PDF gốc vào đó:<br>
  <img width="348" height="421" alt="image" src="https://github.com/user-attachments/assets/881b3224-30c0-4542-bdec-d2b16f3c8a52" /><br>

- Sử dụng Git Bash ở Terminal của Visual Studio code:<br>
  <img width="651" height="641" alt="image" src="https://github.com/user-attachments/assets/f2f15919-f33f-4e5e-8ecc-471cc250b6f3" /><br>
- Gõ lệnh trong git bash: python -m venv .venv để tạo môi trường, ta được 1 tệp:<br>
  <img width="329" height="281" alt="image" src="https://github.com/user-attachments/assets/2b1d09bf-72bd-40db-a119-083fba4394f8" /><br>

 - Gõ lệnh: source .venv/Scripts/activate để khởi chạy môi trường, đường đẫn sẽ có dạng .venv:<br>
    <img width="591" height="87" alt="image" src="https://github.com/user-attachments/assets/f2d568da-feb5-440a-a3eb-365f4e58fcf2" /><br>

- Cài đặt các thư viện Python cần thiết:<br>

  <img width="1036" height="825" alt="image" src="https://github.com/user-attachments/assets/17541516-dba1-4cdc-918a-d97fa8e979fa" /><br>

- Dùng OpenSSL ( Git Bash) gõ lệnh để tạo key và chứng thư thử nghiệm:<br>

  <img width="1332" height="595" alt="image" src="https://github.com/user-attachments/assets/8c7f766c-e34e-4b9b-8517-a1a7cb13a8d1" /><br>

- Sau khi đã có key và chứng thư thử nghiệm, có thể tạo file script để tạo chữ kí vào file PDF gốc:<br>
+ Chuẩn bị 2 file python:<br>
  <img width="363" height="424" alt="image" src="https://github.com/user-attachments/assets/94e34a81-9b14-448f-b998-30914b375e08" /><br>
+ Khởi chạy file python kí để tự động kí vào file PDF gốc và sinh ra bản đã kí:<br>
  <img width="1594" height="790" alt="image" src="https://github.com/user-attachments/assets/8eb8b50c-d741-4378-b112-05d8eb3b49dd" /><br>
+ File PDF đã kí:<br>
  <img width="1277" height="998" alt="image" src="https://github.com/user-attachments/assets/2d5a11db-ba0a-45cc-9a41-a0683520dc66" /><br>
+ Khởi chạy file verify để kiểm tra xác thực chữ kí trên bản PDF đã kí:<br>
<img width="781" height="437" alt="image" src="https://github.com/user-attachments/assets/60c855b8-ccbc-47ae-b6c1-4e0b8ad1b6d1" /><br>
+ Kết quả được lưu tại log.txt:<br>
  <img width="903" height="409" alt="image" src="https://github.com/user-attachments/assets/104e5043-0011-4503-a482-bcd947376710" /><br>

- Kiểm tra và phát hiện sửa đổi:<br>
  + copy file pdf đã kí và chỉnh sửa thêm 1 vài kí tự vào file và lưu tên tampered.pdf, thực hiện kiểm tra file đó:<br>
 
    <img width="1295" height="679" alt="image" src="https://github.com/user-attachments/assets/609380bc-cb80-46e2-84fa-65a1b73cd134" /><br>

  + Chạy kiểm tra file sửa đổi xem có đạt yêu cầu xác thực không: <br>
  <img width="726" height="436" alt="image" src="https://github.com/user-attachments/assets/016e25ba-30aa-499f-b440-6a8833b0dfb6" /><br>

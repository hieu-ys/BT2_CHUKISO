from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import ValidationContext
# --- ĐÂY LÀ HÀM XÁC THỰC CHÍNH XÁC ---
from pyhanko.sign.validation import collect_validation_info
import asyncio
import sys

# --- LOG KIỂM THỬ ---
log = []
log.append("--- BẮT ĐẦU KIỂM THỬ CHỮ KÝ (Code đã sửa cho v0.31.0) ---")

file_to_check = 'tampered.pdf'
log.append(f"File: {file_to_check}")

try:
    # allow hybrid xref handling when reading the PDF
    r = PdfFileReader(open(file_to_check, 'rb'), strict=False)
    sig = r.embedded_signatures[0]
    log.append(f"Tìm thấy chữ ký trong field: '{sig.field_name}'")

    # --- BƯỚC 1 & 2: Đã đọc ---
    log.append("BƯỚC 1 & 2: Đã đọc Signature Dictionary và tách PKCS#7")

    # --- BƯỚC 5: Thiết lập Trust ---
    vc = ValidationContext(trust_roots=[sig.signer_cert])
    log.append(f"BƯỚC 5: Thiết lập Trust Root -> tin tưởng cert '{sig.signer_cert.subject.human_friendly}'")

    # --- BƯỚC 3-8: Thực hiện xác thực (Dùng collect_validation_info) ---
    log.append("BƯỚC 3-8: Bắt đầu quá trình xác thực mật mã...")
    
    # Validate the PDF signature fully (returns a PdfSignatureStatus)
    from pyhanko.sign.validation.pdf_embedded import async_validate_pdf_signature

    try:
        pdf_status = asyncio.run(async_validate_pdf_signature(sig, signer_validation_context=vc))
    except Exception as e:
        raise

    # pdf_status is a PdfSignatureStatus with summary/valid/intact attributes
    status = pdf_status
    
    log.append("\n--- KẾT QUẢ XÁC THỰC (LOG) ---")
    # status.summary is a callable that returns a short string
    try:
        summary_str = status.summary()
    except Exception:
        summary_str = str(status)
    log.append(f"Tổng quan (Summary): {summary_str}")
    # If the integrity check failed, consider the signature invalid for application-level checks.
    # pyHanko may report the PKCS#7 signature structure as cryptographically valid
    # (status.valid) even if the document digest does not match the messageDigest
    # in the signed attributes (status.intact == False). For most use-cases we want
    # to treat such cases as a failure, so compute display_valid accordingly.
    display_valid = bool(status.valid)
    if not bool(status.intact):
        display_valid = False
        log.append("(LƯU Ý) Kiểm tra toàn vẹn thất bại -> áp dụng: coi chữ ký là không hợp lệ")
    log.append(f"Chữ ký hợp lệ (Valid): {display_valid}")
    log.append(f"Tính toàn vẹn (Integrity): {status.intact}")
    # prefer status.md_algorithm if available, otherwise fall back to signature object
    hash_alg = getattr(status, 'md_algorithm', None) or getattr(sig, 'md_algorithm', None)
    log.append(f"Hash Algorithm: {hash_alg}")
    sig_mech = getattr(status, 'pkcs7_signature_mechanism', None) or getattr(sig, 'signing_mechanism', None)
    log.append(f"Padding/Signature Algorithm: {sig_mech}")

    if not status.valid:
        log.append(f"\nLỖI CHI TIẾT: {summary_str}")

except IndexError:
    log.append(f"LỖI: Không tìm thấy chữ ký nào trong file '{file_to_check}'")
except FileNotFoundError:
    log.append(f"LỖI: Không tìm thấy file '{file_to_check}'.")
except Exception as e:
    log.append(f"LỖI KHÔNG XÁC ĐỊNH: {e}")

# In Log kiểm thử ra màn hình
print("\n".join(log))

# Nộp kèm (lưu) log ra file theo yêu cầu
with open('verification_log.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(log))

print(f"\nĐã lưu log chi tiết vào file 'verification_log.txt'")
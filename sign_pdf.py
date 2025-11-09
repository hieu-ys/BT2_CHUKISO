import os
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec, append_signature_field

# --- ĐÂY LÀ ĐƯỜNG DẪN IMPORT CHÍNH XÁC CHO v0.31.0 ---
from pyhanko.sign.signers import Signer, PdfSigner
from pyhanko.sign.signers.pdf_signer import PdfSignatureMetadata
from pyhanko.sign.signers.pdf_cms import CAdESSignedAttrSpec
try:
    from pyhanko.sign.ltv import add_ltv_to_pdf
    HAVE_LTV = True
except Exception:
    HAVE_LTV = False

from pyhanko_certvalidator import ValidationContext

print("--- BẮT ĐẦU KÝ PDF (Code đã sửa cho v0.31.0) ---")

# --- Thiết lập Signer (đọc key và cert) ---
try:
    # pyHanko build in this environment exposes helper loaders in pdf_cms
    from pyhanko.sign.signers.pdf_cms import (
        load_cert_from_pemder,
        load_private_key_from_pemder,
        SimpleCertificateStore,
    )
    from pyhanko.sign.signers import SimpleSigner

    # loader functions accept filenames in this pyHanko build
    cert = load_cert_from_pemder('certificate.pem')
    key = load_private_key_from_pemder('private_key.pem', passphrase=None)

    # create a simple certificate store and register the signing cert
    cert_store = SimpleCertificateStore.from_certs([cert])

    signer = SimpleSigner(cert, key, cert_registry=cert_store)
    print("Đã tải key và certificate.")
except FileNotFoundError as e:
    print(f"LỖI: Không tìm thấy file key/cert.")
    print(e)
    exit()
except Exception as e:
    print(f"LỖI: Không thể khởi tạo signer: {e}")
    exit()

# --- BƯỚC 1: Chuẩn bị file PDF gốc ---
print("BƯỚC 1: Mở 'original.pdf'...")
try:
    # allow hybrid xref handling if the source PDF uses hybrid sections
    w = IncrementalPdfFileWriter(open('original.pdf', 'rb'), strict=False)
except FileNotFoundError:
    print("LỖI: Không tìm thấy 'original.pdf'.")
    exit()

# --- BƯỚC 2: Tạo Signature field ---
print("BƯỚC 2: Tạo Signature Field 'Signature1' ở trang 1...")
signature_field = SigFieldSpec(
    sig_field_name='Signature1',
    box=(50, 700, 250, 750),
    on_page=0
)
append_signature_field(w, signature_field)


# --- BƯỚC 3-7: Ký tài liệu (Logic mới) ---
print("BƯỚC 3-7: Đang thực hiện ký...")

# Nếu không có helper LTV, cố gắng nhúng thông tin xác thực khi ký
validation_ctx = None
if not HAVE_LTV:
    try:
        validation_ctx = ValidationContext(
            trust_roots=[signer.signing_cert],
            allow_fetching=True
        )
    except Exception:
        validation_ctx = None

# Sử dụng cấu hình mặc định; nếu LTV không có, yêu cầu nhúng thông tin xác thực
signature_meta = PdfSignatureMetadata(
    field_name='Signature1',
    md_algorithm='sha256',
    name='Phạm Trung Hiếu',
    embed_validation_info=(not HAVE_LTV),
    validation_context=validation_ctx if validation_ctx is not None else None,
    # request CAdES signed attributes (messageDigest, signingTime, contentType)
    cades_signed_attr_spec=CAdESSignedAttrSpec(timestamp_content=False),
    # accept any key usage (avoid rejection if cert lacks non_repudiation)
    signer_key_usage=set(),
)

pdf_signer = PdfSigner(
    signature_meta,
    signer,
    new_field_spec=signature_field,
)

try:
    with open('signed.pdf', 'wb') as out_file:
        pdf_signer.sign_pdf(
            w,
            output=out_file,
            bytes_reserved=8192,
        )
    print("ĐÃ KÝ THÀNH CÔNG -> file 'signed.pdf'")
except Exception as e:
    print(f"LỖI KHI KÝ: {e}")
    exit()


# --- BƯỚC 8 (LTV): Cập nhật DSS ---
print("--- BƯỚC 8 (LTV): Đang thử thêm thông tin LTV...")
if not HAVE_LTV:
    print("LTV không khả dụng trong bản pyHanko hiện tại; bỏ qua bước thêm LTV.")
else:
    try:
        vc = ValidationContext(
            trust_roots=[signer.signing_cert],
            allow_fetching=True
        )
        
        with open('signed.pdf', 'rb') as f_in:
            w_ltv = IncrementalPdfFileWriter(f_in)
            with open('signed_ltv.pdf', 'wb') as f_out:
                add_ltv_to_pdf(
                    w_ltv,
                    output=f_out,
                    validation_context=vc
                )
        print("ĐÃ THÊM LTV THÀNH CÔNG -> file 'signed_ltv.pdf'")

    except Exception as e:
        print(f"LƯU Ý: Không thể thêm LTV.")
        print(f"  (Lý do: {e})")

print("--- HOÀN TẤT KÝ ---")
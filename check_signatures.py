import asyncio
import sys
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation.pdf_embedded import async_validate_pdf_signature
from pyhanko.sign.validation import ValidationContext


def check_file(file_path):
    print(f"\nChecking: {file_path}")
    try:
        r = PdfFileReader(open(file_path, 'rb'), strict=False)
    except Exception as e:
        print(f"  Could not open PDF: {e}")
        return
    sigs = r.embedded_signatures
    if not sigs:
        print("  No embedded signatures found.")
        return
    sig = sigs[0]
    print(f"  Signature field: {sig.field_name}")
    try:
        vc = ValidationContext(trust_roots=[sig.signer_cert])
    except Exception:
        vc = None
    try:
        status = asyncio.run(async_validate_pdf_signature(sig, signer_validation_context=vc))
    except Exception as e:
        print(f"  Validation raised an exception: {e}")
        return
    try:
        print(f"  Summary: {status.summary()}")
    except Exception:
        print(f"  Summary: {status}")
    print(f"  Valid: {status.valid}")
    print(f"  Intact: {status.intact}")
    print(f"  md_algorithm: {getattr(status, 'md_algorithm', None)}")
    print(f"  pkcs7_signature_mechanism: {getattr(status, 'pkcs7_signature_mechanism', None)}")


if __name__ == '__main__':
    files = sys.argv[1:] or ['signed.pdf', 'tampered.pdf']
    for f in files:
        check_file(f)

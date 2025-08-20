from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import base64, os
from dotenv import load_dotenv
import re

load_dotenv()

key_b64 = os.environ.get('AES_KEY')

if not key_b64:
    raise ValueError("Missing AES_SECRET_KEY environment variable!")

key = base64.b64decode(key_b64)

def is_base64(s):
    try:
        s_bytes = s.encode()
        return base64.b64encode(base64.b64decode(s_bytes)) == s_bytes
    except Exception:
        return False

def encrypt(plaintext):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode()

# def decrypt(ciphertext):
#     ciphertext = base64.b64decode(ciphertext)
#     iv = ciphertext[:16]
#     actual_ciphertext = ciphertext[16:]

#     cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
#     decryptor = cipher.decryptor()

#     decrypted_padded = decryptor.update(actual_ciphertext) + decryptor.finalize()
#     unpadder = padding.PKCS7(128).unpadder()
#     decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()

#     return decrypted_data.decode()

def decrypt(ciphertext):
    if not ciphertext:
        return ''  # Return empty string if input is None or blank

    try:
        # Ensure proper base64 padding
        if isinstance(ciphertext, bytes):
            ciphertext = ciphertext.decode()

        padded = ciphertext + '=' * (-len(ciphertext) % 4)  # fix padding
        decoded = base64.b64decode(padded)

        iv = decoded[:16]
        actual_ciphertext = decoded[16:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()

        decrypted_padded = decryptor.update(actual_ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()

        return decrypted_data.decode()

    except Exception as e:
        # Log or return a clear error marker for debugging
        print(f"[Decryption error]: {e}")
        return "[Decryption Error]"


def mask_email(email):
    if '@' not in email:
        return ''
    name, domain = email.split('@')
    masked_name = name[0] + '****' + name[-1] if len(name) > 2 else '****'
    return f"{masked_name}@{domain}"

def mask_phone(phone):
    return phone[:-3] + '***' if len(phone) > 3 else '***'

################# new code for masking pan and aadhar in hrms #############################

# def mask_pan(pan):
#     """Mask PAN keeping first 5 and last 1 visible"""
#     if not pan or len(pan) < 6:
#         return '***'
#     return f"{pan[:5]}***{pan[-1]}"

# def mask_aadhaar(aadhaar):
#     """Mask Aadhaar keeping last 4 digits visible"""
#     if not aadhaar or len(aadhaar) < 4:
#         return 'XXXX'
#     return f"XXXX-XXXX-{aadhaar[-4:]}"

def encrypt_bytes(file_bytes):
    """Encrypt binary file bytes."""
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # PKCS7 padding for binary
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_bytes) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode()


def decrypt_bytes(ciphertext_b64):
    """Decrypt binary file bytes."""
    if isinstance(ciphertext_b64, bytes):
        ciphertext_b64 = ciphertext_b64.decode()

    padded = ciphertext_b64 + '=' * (-len(ciphertext_b64) % 4)
    decoded = base64.b64decode(padded)

    iv = decoded[:16]
    actual_ciphertext = decoded[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    decrypted_padded = decryptor.update(actual_ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(decrypted_padded) + unpadder.finalize()


def mask_aadhaar_in_text(text):
    return re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", lambda m: "XXXX XXXX " + m.group(0)[-4:], text)

def mask_pan_in_text(text):
    return re.sub(r"\b[A-Z]{5}\d{4}[A-Z]\b", lambda m: m.group(0)[:2] + "XXXXX" + m.group(0)[-1], text)
import hmac
import hashlib

def verify_github_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC-SHA256.
    """
    if not secret:
        return True
    if not signature_header:
        return False
    
    # Header format: sha256=signature_hex
    if signature_header.startswith("sha256="):
        signature = signature_header.split("sha256=")[-1]
    else:
        signature = signature_header
        
    expected_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

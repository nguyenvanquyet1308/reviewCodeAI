from app.core.security import verify_github_signature
import hmac
import hashlib

def test_verify_github_signature_valid():
    """
    Verify that correct signature returns True.
    """
    secret = "test_webhook_secret"
    payload = b'{"event": "pull_request", "action": "opened"}'
    
    # Generate expected signature
    signature = "sha256=" + hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    assert verify_github_signature(payload, signature, secret) is True

def test_verify_github_signature_invalid():
    """
    Verify that incorrect signature returns False.
    """
    secret = "test_webhook_secret"
    payload = b'{"event": "pull_request", "action": "opened"}'
    signature = "sha256=wrong_signature_here"
    
    assert verify_github_signature(payload, signature, secret) is False

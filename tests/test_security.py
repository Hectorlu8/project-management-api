from app.security import hash_password, verify_password, decode_access_token, create_access_token
from datetime import timedelta
import pytest
import jwt

def test_hash_password_returns_different_hash_each_time():
    hash1 = hash_password("mypassword123")
    hash2 = hash_password("mypassword123")
    assert hash1 != hash2

def test_verify_password_returns_true_for_correct_password():
    password = "mypassword123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) == True

def test_verify_password_returns_false_for_incorrect_password():
    password = "mypassword123"
    hashed = hash_password(password)
    assert verify_password("wrongpassword", hashed) == False    

def test_decode_access_token_raises_on_expired_token():
    expired_token = create_access_token({"sub": "someone@example.com"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired_token)  
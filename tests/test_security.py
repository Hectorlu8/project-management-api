from app.security import hash_password, verify_password, decode_access_token, create_access_token
from app.main import get_current_user
from app import models
from datetime import timedelta
from unittest.mock import MagicMock
from fastapi import HTTPException
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

def test_get_current_user_returns_user_when_found():
    fake_user = models.User(id=1, username="alice", email="alice@example.com", hashed_password="notreallyahash")

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = fake_user

    token = create_access_token({"sub": "alice@example.com"})

    user = get_current_user(token=token, db=mock_db)

    assert user is fake_user
    mock_db.query.assert_called_once_with(models.User)
    
def test_get_current_user_raises_401_when_user_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    token = create_access_token({"sub": "alice@example.com"})

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token, db=mock_db)
    assert exc_info.value.status_code == 401
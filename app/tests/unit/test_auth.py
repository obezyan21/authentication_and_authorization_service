from datetime import datetime, timezone

import pytest
from unittest.mock import MagicMock, patch

from app.core.security import get_password_hash, verify_password, create_access_token, verify_token


def test_password_hash():
    password = "pass123"
    wrong_password = "abcde123"

    hashed_password = get_password_hash(password)

    assert password != hashed_password
    assert verify_password(password, hashed_password) == True
    assert verify_password(wrong_password, hashed_password) == False

def test_token_create_and_verify():
    data = {"id": 1}
    result = create_access_token(data)

    assert isinstance(result, str)
    assert len(result.split(".")) == 3

    decoded = verify_token(result)

    assert decoded["id"] == 1
    assert "exp" in decoded
    assert "iat" in decoded

    exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    iat_time = datetime.fromtimestamp(decoded["iat"], tz=timezone.utc)

    assert (exp_time - iat_time).seconds == 30*60

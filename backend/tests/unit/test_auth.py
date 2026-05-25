"""Unit tests for auth module: JWT, password, 2FA."""
from __future__ import annotations

import pytest
from auth.password import hash_password, verify_password, generate_otp
from auth.two_factor import generate_totp_secret, verify_totp, generate_backup_codes
from auth.jwt import create_access_token, create_refresh_token, create_email_verify_token
import uuid


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "SecurePass123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("CorrectPass123!")
        assert not verify_password("WrongPass123!", hashed)

    def test_hashes_are_unique(self):
        password = "SamePass123!"
        assert hash_password(password) != hash_password(password)


class TestOTPGeneration:
    def test_otp_is_6_digits(self):
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()

    def test_otp_uniqueness(self):
        otps = {generate_otp() for _ in range(100)}
        assert len(otps) > 1  # Should generate different OTPs


class TestTOTP:
    def test_totp_verification(self):
        secret = generate_totp_secret()
        import pyotp
        totp = pyotp.TOTP(secret)
        current_code = totp.now()
        assert verify_totp(secret, current_code)

    def test_invalid_totp(self):
        secret = generate_totp_secret()
        assert not verify_totp(secret, "000000")

    def test_backup_codes_generation(self):
        codes = generate_backup_codes(10)
        assert len(codes) == 10
        assert all(len(c) == 8 for c in codes)


class TestJWT:
    def test_create_access_token(self):
        user_id = uuid.uuid4()
        token, jti = create_access_token(user_id, "student")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        raw, hashed = create_refresh_token()
        assert len(raw) > 32
        import hashlib
        assert hashed == hashlib.sha256(raw.encode()).hexdigest()

    def test_email_verify_token(self):
        user_id = uuid.uuid4()
        token = create_email_verify_token(user_id)
        assert isinstance(token, str)

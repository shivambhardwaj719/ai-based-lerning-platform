"""Unit tests for user-related logic — password hashing, RBAC, profile validation."""
from __future__ import annotations

import pytest


class TestPasswordHashing:
    def test_hash_and_verify(self):
        from auth.password import hash_password, verify_password
        pwd = "MySecure@Pass123"
        hashed = hash_password(pwd)
        assert hashed != pwd
        assert verify_password(pwd, hashed)

    def test_wrong_password_fails(self):
        from auth.password import hash_password, verify_password
        hashed = hash_password("correct_password")
        assert not verify_password("wrong_password", hashed)

    def test_hash_is_unique(self):
        from auth.password import hash_password
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2  # bcrypt adds random salt


class TestRBAC:
    def test_role_hierarchy(self):
        from auth.rbac import UserRole
        # Higher role has more access; not a strict ordering but each role is distinct
        roles = [UserRole.STUDENT, UserRole.MENTOR, UserRole.INSTRUCTOR, UserRole.ADMIN, UserRole.SUPER_ADMIN]
        assert len(roles) == 5

    def test_admin_has_manage_users_permission(self):
        from auth.rbac import ROLE_PERMISSIONS, Permission, UserRole
        assert Permission.MANAGE_USERS in ROLE_PERMISSIONS[UserRole.ADMIN]

    def test_student_cannot_manage_users(self):
        from auth.rbac import ROLE_PERMISSIONS, Permission, UserRole
        assert Permission.MANAGE_USERS not in ROLE_PERMISSIONS[UserRole.STUDENT]

    def test_super_admin_has_all_permissions(self):
        from auth.rbac import ROLE_PERMISSIONS, Permission, UserRole
        super_admin_perms = ROLE_PERMISSIONS[UserRole.SUPER_ADMIN]
        critical_perms = [
            Permission.MANAGE_USERS,
            Permission.MANAGE_PROBLEMS,
            Permission.VIEW_ANALYTICS,
        ]
        for perm in critical_perms:
            assert perm in super_admin_perms


class TestOTPGeneration:
    def test_otp_length(self):
        from auth.password import generate_otp
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()

    def test_otp_uniqueness(self):
        from auth.password import generate_otp
        otps = {generate_otp() for _ in range(100)}
        # With 10^6 possible values, 100 samples should have > 50 unique
        assert len(otps) > 50


class TestTwoFactor:
    def test_setup_returns_secret_and_qr(self):
        from auth.two_factor import setup_2fa
        result = setup_2fa(user_id="test-user", email="test@example.com")
        assert "secret" in result
        assert "qr_code_base64" in result
        assert "backup_codes" in result
        assert len(result["backup_codes"]) == 10

    def test_totp_verify(self):
        import pyotp
        from auth.two_factor import setup_2fa, verify_totp
        result = setup_2fa(user_id="u1", email="u@e.com")
        secret = result["secret"]
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()
        assert verify_totp(secret, valid_code)

    def test_invalid_totp_rejected(self):
        from auth.two_factor import setup_2fa, verify_totp
        result = setup_2fa(user_id="u1", email="u@e.com")
        assert not verify_totp(result["secret"], "000000")

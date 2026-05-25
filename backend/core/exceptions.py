from __future__ import annotations

from fastapi import HTTPException, status


class PlatformException(Exception):
    """Base class for all platform exceptions."""
    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


# ── Auth Exceptions ───────────────────────────────────────────────────────────
class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication required") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail,
                         headers={"WWW-Authenticate": "Bearer"})

class InvalidCredentialsError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

class TokenExpiredError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

class InvalidTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

class AccountLockedError(HTTPException):
    def __init__(self, minutes: int = 15) -> None:
        super().__init__(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked. Try again in {minutes} minutes.",
        )

class EmailNotVerifiedError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

class TwoFactorRequiredError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="2FA verification required")

class InsufficientPermissionsError(HTTPException):
    def __init__(self, required_role: str | None = None) -> None:
        detail = "Insufficient permissions"
        if required_role:
            detail += f". Required role: {required_role}"
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# ── Resource Exceptions ───────────────────────────────────────────────────────
class NotFoundError(HTTPException):
    def __init__(self, resource: str = "Resource", id_: str | None = None) -> None:
        detail = f"{resource} not found"
        if id_:
            detail += f": {id_}"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class AlreadyExistsError(HTTPException):
    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=f"{resource} already exists")

class ValidationError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


# ── Business Logic Exceptions ─────────────────────────────────────────────────
class RateLimitExceededError(HTTPException):
    def __init__(self, retry_after: int = 60) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )

class ContestNotActiveError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Contest is not active")

class SubmissionLimitExceededError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                         detail="Submission limit exceeded")

class CodeExecutionError(PlatformException):
    pass

class PaymentError(HTTPException):
    def __init__(self, detail: str = "Payment processing failed") -> None:
        super().__init__(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail)

class AIServiceError(PlatformException):
    pass

class StorageError(PlatformException):
    pass

class ServiceUnavailableError(HTTPException):
    def __init__(self, service: str = "Service") -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service} is temporarily unavailable",
        )

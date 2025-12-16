from datetime import date

import pytest
from pydantic import ValidationError

from app.models.user import Gender
from app.schemas.auth import LoginRequest, SignupRequest


class TestSignupRequest:
    def test_signup_request_valid(self):
        request = SignupRequest(
            email="test@example.com",
            password="password123",
            nickname="testuser",
            gender=Gender.MALE,
            birth_date=date(1990, 1, 1),
        )
        assert request.email == "test@example.com"
        assert request.password == "password123"
        assert request.nickname == "testuser"
        assert request.gender == Gender.MALE
        assert request.birth_date == date(1990, 1, 1)

    def test_signup_request_invalid_email(self):
        with pytest.raises(ValidationError):
            SignupRequest(
                email="invalid-email",
                password="password123",
                nickname="testuser",
                gender=Gender.MALE,
                birth_date=date(1990, 1, 1),
            )

    def test_signup_request_short_password(self):
        with pytest.raises(ValidationError):
            SignupRequest(
                email="test@example.com",
                password="short",
                nickname="testuser",
                gender=Gender.MALE,
                birth_date=date(1990, 1, 1),
            )


class TestLoginRequest:
    def test_login_request_valid(self):
        request = LoginRequest(
            email="test@example.com",
            password="password123",
        )
        assert request.email == "test@example.com"
        assert request.password == "password123"

    def test_login_request_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(
                email="invalid-email",
                password="password123",
            )

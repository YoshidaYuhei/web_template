class TestSignupEndpoint:
    """POST /api/v1/auth/signup/password"""

    async def test_signup_returns_201_with_account_and_token(self, client):
        """正常にサインアップできること"""
        response = await client.post(
            "/auth/signup/password",
            json={"email": "user@example.com", "password": "mypassword1"},
        )

        assert response.status_code == 201
        data = response.json()

        assert data["account"]["email"] == "user@example.com"
        assert data["account"]["is_active"] is True
        assert "id" in data["account"]

        assert "access_token" in data["token"]
        assert "refresh_token" in data["token"]
        assert data["token"]["token_type"] == "bearer"

    async def test_signup_returns_409_for_duplicate_email(self, client):
        """重複メールアドレスの場合 409 が返却されること"""
        await client.post(
            "/auth/signup/password",
            json={"email": "dup@example.com", "password": "mypassword1"},
        )

        response = await client.post(
            "/auth/signup/password",
            json={"email": "dup@example.com", "password": "mypassword1"},
        )

        assert response.status_code == 409

    async def test_signup_returns_422_for_short_password(self, client):
        """パスワードが短すぎる場合 422 が返却されること"""
        response = await client.post(
            "/auth/signup/password",
            json={"email": "user@example.com", "password": "short"},
        )

        assert response.status_code == 422

    async def test_signup_returns_422_for_invalid_email(self, client):
        """メールアドレスの形式が不正な場合 422 が返却されること"""
        response = await client.post(
            "/auth/signup/password",
            json={"email": "invalid", "password": "mypassword1"},
        )

        assert response.status_code == 422

    async def test_signup_returns_422_for_empty_password(self, client):
        """パスワードが空の場合 422 が返却されること"""
        response = await client.post(
            "/auth/signup/password",
            json={"email": "user@example.com", "password": ""},
        )

        assert response.status_code == 422

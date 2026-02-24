class TestLoginEndpoint:
    """POST /auth/login/password"""

    async def test_login_returns_200_with_account_and_token(self, client):
        """正常にログインできること"""
        # まずサインアップ
        await client.post(
            "/auth/signup/password",
            json={"email": "user@example.com", "password": "mypassword1"},
        )

        response = await client.post(
            "/auth/login/password",
            json={"email": "user@example.com", "password": "mypassword1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["account"]["email"] == "user@example.com"
        assert data["account"]["is_active"] is True
        assert "access_token" in data["token"]
        assert "refresh_token" in data["token"]
        assert data["token"]["token_type"] == "bearer"

    async def test_login_returns_401_for_wrong_password(self, client):
        """パスワードが不正な場合 401 が返却されること"""
        await client.post(
            "/auth/signup/password",
            json={"email": "user@example.com", "password": "mypassword1"},
        )

        response = await client.post(
            "/auth/login/password",
            json={"email": "user@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401

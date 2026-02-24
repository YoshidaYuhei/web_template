class TestRefreshEndpoint:
    """POST /auth/refresh"""

    async def test_refresh_returns_200_with_new_tokens(self, client):
        """正常にトークンリフレッシュできること"""
        signup_response = await client.post(
            "/auth/signup/password",
            json={"email": "user@example.com", "password": "mypassword1"},
        )
        refresh_token = signup_response.json()["token"]["refresh_token"]

        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["refresh_token"] != refresh_token

    async def test_refresh_returns_401_for_invalid_token(self, client):
        """無効なトークンの場合 401 が返却されること"""
        response = await client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )

        assert response.status_code == 401

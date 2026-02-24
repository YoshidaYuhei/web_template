class TestLogoutEndpoint:
    """POST /auth/logout"""

    async def test_logout_returns_204(self, client):
        """正常にログアウトできること"""
        signup_response = await client.post(
            "/auth/signup/password",
            json={"email": "user@example.com", "password": "mypassword1"},
        )
        token_data = signup_response.json()["token"]

        response = await client.post(
            "/auth/logout",
            json={"refresh_token": token_data["refresh_token"]},
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )

        assert response.status_code == 204

    async def test_logout_returns_401_without_auth(self, client):
        """認証なしの場合 401/403 が返却されること"""
        response = await client.post(
            "/auth/logout",
            json={"refresh_token": "some-token"},
        )

        assert response.status_code in (401, 403)

from app.core.security import create_access_token


class TestGetCurrentUser:
    """get_current_user 依存のテスト"""

    async def test_valid_token_returns_account(self, client):
        """有効なアクセストークンでアカウント情報が取得できること"""
        # サインアップしてトークンを取得
        signup_response = await client.post(
            "/auth/signup/password",
            json={"email": "user@example.com", "password": "mypassword1"},
        )
        token_data = signup_response.json()["token"]

        # 認証が必要なエンドポイント (logout) でテスト
        response = await client.post(
            "/auth/logout",
            json={"refresh_token": token_data["refresh_token"]},
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )

        assert response.status_code == 204

    async def test_invalid_token_returns_401(self, client):
        """無効なアクセストークンで401が返却されること"""
        response = await client.post(
            "/auth/logout",
            json={"refresh_token": "some-token"},
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401

    async def test_token_with_nonexistent_account_returns_401(self, client):
        """存在しないアカウントIDのトークンで401が返却されること"""
        token = create_access_token(data={"sub": "99999"})
        response = await client.post(
            "/auth/logout",
            json={"refresh_token": "some-token"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401

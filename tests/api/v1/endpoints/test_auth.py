import pytest
from httpx import AsyncClient


class TestSignup:
    @pytest.mark.asyncio
    async def test_signup_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "nickname": "newuser",
                "gender": "male",
                "birth_date": "1990-01-01",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, authenticated_client: AsyncClient):
        """ファクトリで作成したユーザーでログイン"""
        response = await authenticated_client.post(
            "/api/v1/auth/login",
            json={
                "email": authenticated_client.account.email,
                "password": "password123",  # AccountFactoryのデフォルトパスワード
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_credentials(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401


class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_success(self, authenticated_client: AsyncClient):
        """ファクトリで作成したユーザーでログアウト"""
        response = await authenticated_client.post(
            "/api/v1/auth/logout",
            headers=authenticated_client.auth_headers,
        )
        assert response.status_code == 204


class TestRefresh:
    @pytest.mark.asyncio
    async def test_refresh_success(self, authenticated_client: AsyncClient):
        """ファクトリで作成したユーザーのリフレッシュトークンを使用"""
        response = await authenticated_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": authenticated_client.refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )
        assert response.status_code == 401

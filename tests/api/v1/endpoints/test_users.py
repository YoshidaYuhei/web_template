import pytest
from httpx import AsyncClient


class TestGetUser:
    @pytest.mark.asyncio
    async def test_get_user_success(self, authenticated_client: AsyncClient):
        """ファクトリで作成したユーザー情報を取得"""
        user_id = authenticated_client.user.id
        response = await authenticated_client.get(
            f"/api/v1/users/{user_id}",
            headers=authenticated_client.auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nickname"] == authenticated_client.user.nickname
        assert data["gender"] == authenticated_client.user.gender.value

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, authenticated_client: AsyncClient):
        """存在しないユーザーIDで404を返す"""
        response = await authenticated_client.get(
            "/api/v1/users/nonexistent-id",
            headers=authenticated_client.auth_headers,
        )
        assert response.status_code == 404

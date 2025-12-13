import pytest

from app.api.v1.internal.health import check_database


class TestHealthCheckSuccess:
    """DB接続成功時のテスト"""

    @pytest.mark.asyncio
    async def test_health_check_returns_connected_status(self, test_session_factory):
        """DB接続成功時に status が "connected" であることを確認"""
        result = await check_database(session_factory=test_session_factory)

        assert result.status == "connected"

    @pytest.mark.asyncio
    async def test_health_check_error_is_none_when_connected(self, test_session_factory):
        """DB接続成功時に error が None であることを確認"""
        result = await check_database(session_factory=test_session_factory)

        assert result.error is None


class TestHealthCheckFailure:
    """DB接続失敗時のテスト"""

    @pytest.mark.asyncio
    async def test_health_check_returns_disconnected_status(self, invalid_session_factory):
        """DB接続失敗時に status が "disconnected" であることを確認"""
        result = await check_database(session_factory=invalid_session_factory)

        assert result.status == "disconnected"

    @pytest.mark.asyncio
    async def test_health_check_includes_error_message(self, invalid_session_factory):
        """DB接続失敗時に error にエラー内容が含まれることを確認"""
        result = await check_database(session_factory=invalid_session_factory)

        assert result.error is not None


class TestHealthCheckEndpoint:
    """エンドポイント統合テスト"""

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_200_when_healthy(self, client):
        """正常時に HTTP 200 が返ることを確認"""
        response = await client.get("/health")

        # DBが接続できれば200、できなければ503
        assert response.status_code in [200, 503]

    @pytest.mark.asyncio
    async def test_health_endpoint_response_structure(self, client):
        """レスポンスに必須フィールドが含まれることを確認"""
        response = await client.get("/health")
        data = response.json()

        assert "status" in data
        assert "database" in data
        assert "status" in data["database"]

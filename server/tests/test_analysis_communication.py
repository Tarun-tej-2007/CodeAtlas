"""Integration tests verifying communication, serialization, and error mapping between CodeAtlas Server and Analysis Engine."""

import pytest
import uuid
import httpx
from unittest.mock import AsyncMock, patch
from fastapi import status

from app.core.exceptions import (
    AnalysisEngineConnectionError,
    AnalysisEngineTimeoutError,
    AnalysisEngineRequestError,
)
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisStatus
from app.services.analysis_engine import AnalysisEngineClient
from app.services.analysis import AnalysisService


# ==========================================
# Client-Level Tests (Direct Mocking)
# ==========================================

@pytest.mark.anyio
async def test_client_health_check_success() -> None:
    client = AnalysisEngineClient()
    mock_resp = httpx.Response(200, json={"status": "running"})
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        is_healthy = await client.health_check()
        assert is_healthy is True
        mock_get.assert_called_once_with(f"{client.base_url}/")


@pytest.mark.anyio
async def test_client_health_check_failure() -> None:
    client = AnalysisEngineClient()
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.ConnectError("Connection refused")
        is_healthy = await client.health_check()
        assert is_healthy is False


@pytest.mark.anyio
async def test_client_submit_success() -> None:
    client = AnalysisEngineClient()
    proj_id = uuid.uuid4()
    job_id = uuid.uuid4()
    req = AnalysisRequest(repository_url="https://github.com/test/repo", project_id=proj_id)
    
    mock_resp = httpx.Response(
        200,
        json={
            "job_id": str(job_id),
            "status": "accepted",
            "message": "Analysis request received",
            "project_id": str(proj_id),
            "repository_url": "https://github.com/test/repo"
        }
    )
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        response = await client.submit_analysis(req, request_id="correlation-req-id")
        
        assert response.job_id == job_id
        assert response.status == AnalysisStatus.ACCEPTED
        assert response.message == "Analysis request received"
        assert response.project_id == proj_id
        assert response.repository_url == "https://github.com/test/repo"
        
        # Verify request serialization: it was serialized via model_dump()
        mock_post.assert_called_once_with(
            f"{client.base_url}/api/v1/analyze",
            json={
                "repository_url": "https://github.com/test/repo",
                "project_id": str(proj_id)
            },
            headers={"X-Request-ID": "correlation-req-id"}
        )


@pytest.mark.anyio
async def test_client_submit_timeout() -> None:
    client = AnalysisEngineClient()
    req = AnalysisRequest(repository_url="https://github.com/test/repo", project_id=uuid.uuid4())
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("ReadTimeout")
        with pytest.raises(AnalysisEngineTimeoutError):
            await client.submit_analysis(req)


@pytest.mark.anyio
async def test_client_submit_connection_failure() -> None:
    client = AnalysisEngineClient()
    req = AnalysisRequest(repository_url="https://github.com/test/repo", project_id=uuid.uuid4())
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.ConnectError("Unreachable host")
        with pytest.raises(AnalysisEngineConnectionError):
            await client.submit_analysis(req)


@pytest.mark.anyio
async def test_timeout_configuration() -> None:
    # Verify default timeout matches Settings configuration
    from app.core.config import settings
    client1 = AnalysisEngineClient()
    assert client1.timeout == settings.ANALYSIS_ENGINE_TIMEOUT

    # Verify custom override
    client2 = AnalysisEngineClient(timeout=42.0)
    assert client2.timeout == 42.0


# ==========================================
# Route-Level Tests (API Endpoints & Mapping)
# ==========================================

def test_api_submit_success(client) -> None:
    # 1. Register and get token
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "Password123!"}
    )
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create project
    proj_response = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": "Analysis Project", "description": "Analyzing code", "visibility": "private"}
    )
    proj_data = proj_response.json()
    proj_id = proj_data["id"]
    
    mock_project = MagicMockProject(
        id=uuid.UUID(proj_id),
        name="Analysis Project",
        repositories=[MagicMockRepository(clone_url="https://github.com/org/repo")]
    )
    
    job_uuid = uuid.uuid4()
    mock_submit_response = AnalysisResponse(
        job_id=job_uuid,
        status=AnalysisStatus.ACCEPTED,
        message="Analysis request received",
        project_id=uuid.UUID(proj_id),
        repository_url="https://github.com/org/repo"
    )
    
    with patch("app.services.project.ProjectService.get_project_with_access") as mock_get_project:
        mock_get_project.return_value = mock_project
        with patch("app.services.analysis_engine.AnalysisEngineClient.submit_analysis", new_callable=AsyncMock) as mock_submit:
            mock_submit.return_value = mock_submit_response
            
            response = client.post(
                f"/api/v1/projects/{proj_id}/analyze",
                headers={**headers, "X-Request-ID": "external-req-id"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["job_id"] == str(job_uuid)
            assert data["status"] == "accepted"
            assert data["repository_url"] == "https://github.com/org/repo"
            mock_submit.assert_called_once()
            # Verify request ID was propagated from request headers
            _, kwargs = mock_submit.call_args
            assert kwargs.get("request_id") == "external-req-id"


def test_api_submit_timeout_mapping(client) -> None:
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser2", "email": "test2@example.com", "password": "Password123!"}
    )
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_project = MagicMockProject(
        id=uuid.uuid4(),
        name="Timeout Project",
        repositories=[MagicMockRepository(clone_url="https://github.com/org/repo")]
    )
    
    with patch("app.services.project.ProjectService.get_project_with_access") as mock_get_project:
        mock_get_project.return_value = mock_project
        with patch("app.services.analysis_engine.AnalysisEngineClient.submit_analysis", new_callable=AsyncMock) as mock_submit:
            mock_submit.side_effect = AnalysisEngineTimeoutError("Gateway Timeout")
            
            response = client.post(f"/api/v1/projects/{mock_project.id}/analyze", headers=headers)
            assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
            
            # Verify standardized error format
            error_data = response.json()
            assert "error" in error_data
            assert error_data["error"]["code"] == "GATEWAY_TIMEOUT"
            assert "timeout" in error_data["error"]["message"].lower()


def test_api_submit_connection_failure_mapping(client) -> None:
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"username": "testuser3", "email": "test3@example.com", "password": "Password123!"}
    )
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_project = MagicMockProject(
        id=uuid.uuid4(),
        name="Conn Project",
        repositories=[MagicMockRepository(clone_url="https://github.com/org/repo")]
    )
    
    with patch("app.services.project.ProjectService.get_project_with_access") as mock_get_project:
        mock_get_project.return_value = mock_project
        with patch("app.services.analysis_engine.AnalysisEngineClient.submit_analysis", new_callable=AsyncMock) as mock_submit:
            mock_submit.side_effect = AnalysisEngineConnectionError("Service Unavailable")
            
            response = client.post(f"/api/v1/projects/{mock_project.id}/analyze", headers=headers)
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            
            # Verify standardized error format
            error_data = response.json()
            assert "error" in error_data
            assert error_data["error"]["code"] == "SERVICE_UNAVAILABLE"


def test_version_endpoint_server(client) -> None:
    response = client.get("/api/v1/version")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["service"] == "CodeAtlas Server"
    assert data["version"] == "0.10.5"
    assert data["build"] == "development"


# Helper Stub Classes for DB Mocking
class MagicMockRepository:
    def __init__(self, clone_url: str):
        self.clone_url = clone_url

class MagicMockProject:
    def __init__(self, id: uuid.UUID, name: str, repositories: list):
        self.id = id
        self.name = name
        self.repositories = repositories

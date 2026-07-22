"""Analysis engine client module for communicating with the Analysis Engine."""

import httpx
from app.core.config import settings
from app.core.exceptions import (
    AnalysisEngineConnectionError,
    AnalysisEngineTimeoutError,
    AnalysisEngineRequestError,
    AnalysisEngineError,
)
from app.schemas.analysis import AnalysisRequest, AnalysisResponse


class AnalysisEngineClient:
    """HTTP client wrapper for communicating with the CodeAtlas Analysis Engine."""

    def __init__(self, base_url: str = None, timeout: float = None) -> None:
        self.base_url = base_url or settings.ANALYSIS_ENGINE_URL
        self.timeout = timeout if timeout is not None else settings.ANALYSIS_ENGINE_TIMEOUT

    async def health_check(self) -> bool:
        """Checks the health status of the Analysis Engine.

        Returns:
            True if healthy, False otherwise.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/")
                if response.status_code == 200:
                    data = response.json()
                    return data.get("status") == "running"
                return False
            except (httpx.ConnectError, httpx.ConnectTimeout):
                return False
            except httpx.TimeoutException:
                return False
            except Exception:
                return False

    async def submit_analysis(self, request: AnalysisRequest, request_id: str = None) -> AnalysisResponse:
        """Submits a repository analysis request to the Analysis Engine.

        Args:
            request: The AnalysisRequest schema.
            request_id: Optional correlation X-Request-ID to pass.

        Returns:
            The AnalysisResponse from the Analysis Engine.

        Raises:
            AnalysisEngineConnectionError: On connection failures.
            AnalysisEngineTimeoutError: On requests timeout.
            AnalysisEngineRequestError: On 4xx errors.
            AnalysisEngineError: On unexpected 5xx or general failures.
        """
        url = f"{self.base_url}/api/v1/analyze"
        headers = {}
        if request_id:
            headers["X-Request-ID"] = request_id

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=request.model_dump(mode="json"), headers=headers)
            except (httpx.ConnectError, httpx.NetworkError) as err:
                raise AnalysisEngineConnectionError(f"Failed to connect to Analysis Engine: {err}") from err
            except httpx.TimeoutException as err:
                raise AnalysisEngineTimeoutError(f"Request to Analysis Engine timed out: {err}") from err
            except Exception as err:
                raise AnalysisEngineError(f"Unexpected communication error: {err}") from err

            if response.status_code == 422:
                raise AnalysisEngineRequestError(f"Invalid request parameters: {response.text}")
            elif 400 <= response.status_code < 500:
                raise AnalysisEngineRequestError(f"Analysis Engine request error ({response.status_code}): {response.text}")
            elif response.status_code >= 500:
                raise AnalysisEngineError(f"Analysis Engine server error ({response.status_code}): {response.text}")

            try:
                data = response.json()
                return AnalysisResponse(**data)
            except Exception as err:
                raise AnalysisEngineError(f"Failed to parse response from Analysis Engine: {err}") from err

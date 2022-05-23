import json
import uuid
from typing import Union
import httpx
from ..types.errors import RequestError, RequestTimeout


class HttpRequest:
    def __init__(self, api_base, get_auth_token: callable):
        """
        - get_auth_token, function.
            three parameters: http_method: str, url: str, bodystring: str
        """
        self.api_base = api_base
        self.get_auth_token = get_auth_token
        self.session = httpx.Client()

    def get(self, path, query_params: dict = None, request_id=None):
        if query_params:
            params_string = "&".join(f"{k}={v}" for k, v in query_params.items())
            path = f"{path}?{params_string}"

        url = self.api_base + path
        headers = {"Content-Type": "application/json"}

        auth_token = self.get_auth_token("GET", path, "")
        if auth_token:
            headers["Authorization"] = "Bearer " + auth_token

        request_id = request_id if request_id else str(uuid.uuid4())
        headers["X-Request-Id"] = request_id

        try:
            r = self.session.get(url, headers=headers, timeout=15)
        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.WriteTimeout) as e:
            raise RequestTimeout(None, str(e))
        except Exception as e:
            raise RequestError(1, str(e))

        try:
            body_json = r.json()
        except Exception:
            body_json = {}

        if r.status_code != 200:
            error = body_json.get("error", {})
            status_code = error.get("code", r.status_code)
            message = error.get("description", r.reason_phrase)
            raise RequestError(status_code, message)

        if "error" in body_json:
            error = body_json.get("error", {})
            status_code = error.get("code", r.status_code)
            message = error.get("description", r.reason_phrase)
            raise RequestError(status_code, message)

        return body_json

    def post(
        self, path, body: Union[dict, list], query_params: dict = None, request_id=None
    ):
        if query_params:
            params_string = "&".join(f"{k}={v}" for k, v in query_params.items())
            path = f"{path}?{params_string}"

        url = self.api_base + path
        headers = {"Content-Type": "application/json"}
        bodystring = json.dumps(body)
        auth_token = self.get_auth_token("POST", path, bodystring)
        if auth_token:
            headers["Authorization"] = "Bearer " + auth_token

        request_id = request_id if request_id else str(uuid.uuid4())
        headers["X-Request-Id"] = request_id

        try:
            r = self.session.post(url, headers=headers, data=bodystring, timeout=15)
        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.WriteTimeout) as e:
            raise RequestTimeout(None, str(e))
        except Exception as e:
            raise RequestError(1, str(e))

        try:
            body_json = r.json()
        except Exception:
            body_json = {}

        if r.status_code != 200:
            error = body_json.get("error", {})
            status_code = error.get("code", r.status_code)
            message = error.get("description", r.reason_phrase)
            raise RequestError(status_code, message)

        if "error" in body_json:
            error = body_json.get("error", {})
            status_code = error.get("code", r.status_code)
            message = error.get("description", r.reason_phrase)
            raise RequestError(status_code, message)

        return body_json

        """
        error response JSON have the key "error",
        else have any data or empty JSON on success.
        #
        example of error response:
        {
            "error": {
                "status": 202,
                "code": 20118,
                "description": "Invalid PIN format.",
            }
        }
        """

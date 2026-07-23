"""Small, dependency-free HTTP helper for the disease-atlas fetchers.

Design goals (see AGENTS.md rule 5):
  * Standard library only (urllib) so scripts run anywhere without `pip install`.
  * Respect HTTP(S)_PROXY environment variables.
  * VERIFY TLS. Never disable certificate verification. When running behind an
    intercepting proxy that presents its own CA (e.g. the agent proxy whose bundle
    lives at /root/.ccr/ca-bundle.crt), trust that CA *in addition* to the system
    roots — do not turn verification off.
  * Read any API keys from the environment; never hardcode secrets.
"""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "disease-atlas/0.1 (+https://github.com/sujaym767/disease-atlas)"

# Candidate CA bundles to trust *in addition* to the system store. This lets the
# fetchers work through a TLS-intercepting proxy without weakening verification.
_CA_BUNDLE_ENV_VARS = ("DISEASE_ATLAS_CA_BUNDLE", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE")
_CA_BUNDLE_PATHS = ("/root/.ccr/ca-bundle.crt",)


class FetchError(RuntimeError):
    """Raised when a request ultimately fails after retries."""


def _ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()  # verifies by default
    for var in _CA_BUNDLE_ENV_VARS:
        path = os.environ.get(var)
        if path and os.path.exists(path):
            try:
                ctx.load_verify_locations(cafile=path)
            except Exception:
                pass
    for path in _CA_BUNDLE_PATHS:
        if os.path.exists(path):
            try:
                ctx.load_verify_locations(cafile=path)
            except Exception:
                pass
    return ctx


_OPENER = urllib.request.build_opener(
    urllib.request.ProxyHandler(),  # picks up HTTP(S)_PROXY from the environment
    urllib.request.HTTPSHandler(context=_ssl_context()),
)


def _request(url: str, *, method: str, data: bytes | None, headers: dict, timeout: float):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    return _OPENER.open(req, timeout=timeout)


def request_json(
    url: str,
    *,
    method: str = "GET",
    params: dict | None = None,
    json_body: dict | None = None,
    headers: dict | None = None,
    timeout: float = 45.0,
    retries: int = 3,
    backoff: float = 2.0,
):
    """Perform an HTTP request and return parsed JSON.

    Retries transient failures (network errors, HTTP 429/5xx) with exponential
    backoff. Raises FetchError on final failure so callers can degrade gracefully.
    """
    if params:
        sep = "&" if ("?" in url) else "?"
        url = url + sep + urllib.parse.urlencode(params, doseq=True)

    body = None
    hdrs = dict(headers or {})
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with _request(url, method=method, data=body, headers=hdrs, timeout=timeout) as resp:
                raw = resp.read()
            return json.loads(raw.decode("utf-8")) if raw else None
        except urllib.error.HTTPError as e:
            # Retry rate-limit / server errors; fail fast on other 4xx.
            if e.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                last_err = e
                time.sleep(backoff * (2 ** attempt))
                continue
            detail = ""
            try:
                detail = e.read().decode("utf-8", "replace")[:500]
            except Exception:
                pass
            raise FetchError(f"HTTP {e.code} for {url}: {detail}") from e
        except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise FetchError(f"Network error for {url}: {e}") from e
        except json.JSONDecodeError as e:
            raise FetchError(f"Non-JSON response from {url}: {e}") from e
    raise FetchError(f"Request failed for {url}: {last_err}")


def get_json(url: str, params: dict | None = None, **kw):
    return request_json(url, method="GET", params=params, **kw)


def post_json(url: str, json_body: dict, **kw):
    return request_json(url, method="POST", json_body=json_body, **kw)

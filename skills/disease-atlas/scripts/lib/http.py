"""Small, dependency-free HTTP helper for the disease-atlas fetchers.

Design goals (see AGENTS.md rule 5):
  * No third-party Python packages. Uses the system `curl` when available and falls
    back to the standard library (urllib). curl is preferred because several public
    biomedical hosts (notably ClinicalTrials.gov, behind Akamai) fingerprint and 403
    the Python TLS client while accepting curl — using curl makes the fetchers robust.
  * Respect HTTP(S)_PROXY environment variables (both curl and urllib do so).
  * VERIFY TLS. Never disable certificate verification. When running behind an
    intercepting proxy that presents its own CA (e.g. the agent proxy whose bundle
    lives at /root/.ccr/ca-bundle.crt), trust that CA *in addition* to the system
    roots — curl reads it from the standard CA env vars; urllib loads it explicitly.
  * Read any API keys from the environment; never hardcode secrets.
"""

from __future__ import annotations

import json
import os
import shutil
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "disease-atlas/0.1 (+https://github.com/sujaym767/disease-atlas)"

# CA bundles to trust *in addition* to the system store (for TLS-intercepting proxies).
_CA_BUNDLE_ENV_VARS = ("DISEASE_ATLAS_CA_BUNDLE", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE")
_CA_BUNDLE_PATHS = ("/root/.ccr/ca-bundle.crt",)

_HAVE_CURL = shutil.which("curl") is not None
_RETRY_CODES = (429, 500, 502, 503, 504)


class FetchError(RuntimeError):
    """Raised when a request ultimately fails after retries."""


class _Transient(Exception):
    """Internal: a network-level failure worth retrying / falling back on."""


# --------------------------------------------------------------------------- CA / TLS
def _ca_bundle() -> str | None:
    for var in _CA_BUNDLE_ENV_VARS:
        p = os.environ.get(var)
        if p and os.path.exists(p):
            return p
    for p in _CA_BUNDLE_PATHS:
        if os.path.exists(p):
            return p
    return None


def _ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()  # verifies by default
    ca = _ca_bundle()
    if ca:
        try:
            ctx.load_verify_locations(cafile=ca)
        except Exception:
            pass
    return ctx


_OPENER = urllib.request.build_opener(
    urllib.request.ProxyHandler(),  # picks up HTTP(S)_PROXY from the environment
    urllib.request.HTTPSHandler(context=_ssl_context()),
)


# --------------------------------------------------------------------------- transports
def _curl_fetch(url, method, body, headers, timeout):
    """Return (status_code:int, body:bytes) via system curl. Raise _Transient on connect failure."""
    fd, tmp = tempfile.mkstemp(prefix="atlas-curl-")
    os.close(fd)
    try:
        cmd = ["curl", "-sS", "--compressed", "-m", str(int(timeout)),
               "-o", tmp, "-w", "%{http_code}", "-X", method,
               "-H", f"User-Agent: {USER_AGENT}", "-H", "Accept: application/json"]
        for k, v in (headers or {}).items():
            cmd += ["-H", f"{k}: {v}"]
        ca = _ca_bundle()
        if ca and not os.environ.get("CURL_CA_BUNDLE"):
            cmd += ["--cacert", ca]
        if body is not None:
            cmd += ["--data-binary", "@-"]
        cmd.append(url)
        proc = subprocess.run(cmd, input=body, capture_output=True, timeout=timeout + 10)
        code = int((proc.stdout or b"0").decode("ascii", "ignore").strip() or 0)
        if code == 0:
            raise _Transient(f"curl failed ({proc.returncode}): {proc.stderr.decode('utf-8','replace')[:200]}")
        with open(tmp, "rb") as f:
            return code, f.read()
    except subprocess.TimeoutExpired as e:
        raise _Transient(f"curl timeout for {url}") from e
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def _urllib_fetch(url, method, body, headers, timeout):
    """Return (status_code:int, body:bytes) via urllib. Raise _Transient on network failure."""
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:  # a real HTTP status — let the caller decide
        try:
            return e.code, e.read()
        except Exception:
            return e.code, b""
    except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
        raise _Transient(f"network error for {url}: {e}") from e


def _fetch_once(url, method, body, headers, timeout):
    return (_curl_fetch if _HAVE_CURL else _urllib_fetch)(url, method, body, headers, timeout)


# --------------------------------------------------------------------------- public API
def request_json(url, *, method="GET", params=None, json_body=None, headers=None,
                 timeout=45.0, retries=3, backoff=2.0):
    """Perform an HTTP request and return parsed JSON.

    Retries transient failures (network errors, HTTP 429/5xx) with exponential backoff.
    Raises FetchError on final failure so callers can degrade gracefully.
    """
    if params:
        sep = "&" if ("?" in url) else "?"
        url = url + sep + urllib.parse.urlencode(params, doseq=True)

    body = None
    hdrs = dict(headers or {})
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")

    last = None
    for attempt in range(retries):
        try:
            code, raw = _fetch_once(url, method, body, hdrs, timeout)
        except _Transient as e:
            last = e
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            raise FetchError(str(e)) from e

        if code in _RETRY_CODES and attempt < retries - 1:
            last = FetchError(f"HTTP {code} for {url}")
            time.sleep(backoff * (2 ** attempt))
            continue
        if code >= 400:
            detail = (raw or b"").decode("utf-8", "replace")[:400]
            raise FetchError(f"HTTP {code} for {url}: {detail}")
        try:
            return json.loads(raw.decode("utf-8")) if raw else None
        except json.JSONDecodeError as e:
            raise FetchError(f"non-JSON response from {url}: {e}") from e
    raise FetchError(f"request failed for {url}: {last}")


def get_json(url, params=None, **kw):
    return request_json(url, method="GET", params=params, **kw)


def post_json(url, json_body, **kw):
    return request_json(url, method="POST", json_body=json_body, **kw)

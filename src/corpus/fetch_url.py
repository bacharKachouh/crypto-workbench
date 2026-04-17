"""Fetch a single URL into corpus/fetched/ with provenance.

Policy contract:

- The caller (the `crypto-intake` skill) is responsible for obtaining
  per-fetch user consent *before* invoking this module. This module
  does not prompt; it just fetches.
- The caller passes the `allowed=True` ceiling and the per-fetch
  `consent=True` signal explicitly; both are required.
- Only `http` and `https` URLs are accepted. No redirects to `file://`
  or `ftp://`. Response size is capped to prevent runaway downloads.
"""

from __future__ import annotations

import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


MODULE = "corpus.fetch_url"

MAX_BYTES = 50 * 1024 * 1024  # 50 MiB
TIMEOUT_SEC = 30
USER_AGENT = "crypto-workbench/1.0 (+local)"


class FetchError(RuntimeError):
    """Raised when a fetch cannot proceed — policy, protocol, or network."""


def _safe_filename_from_url(url: str, content_type: str) -> str:
    """Derive a filename from the URL path + content type."""
    parsed = urlparse(url)
    leaf = Path(parsed.path).name or "fetched"
    if "." in leaf:
        return leaf
    ext = _ext_for_content_type(content_type)
    return f"{leaf}{ext}"


def _ext_for_content_type(content_type: str) -> str:
    ct = (content_type or "").split(";")[0].strip().lower()
    return {
        "application/pdf": ".pdf",
        "text/plain": ".txt",
        "text/markdown": ".md",
        "text/html": ".html",
        "application/json": ".json",
        "application/xml": ".xml",
        "application/octet-stream": ".bin",
    }.get(ct, ".bin")


def fetch_url(
    url: str,
    workbench_root: Path | str,
    *,
    policy_allowed: bool,
    per_fetch_consent: bool,
    reason: str = "",
    max_bytes: int = MAX_BYTES,
    timeout_sec: int = TIMEOUT_SEC,
) -> dict[str, Any]:
    """Fetch `url` into `<workbench_root>/corpus/fetched/` and return provenance.

    Raises FetchError if either consent flag is False, the URL scheme is
    not http(s), the response exceeds `max_bytes`, or the network fails.
    """
    if not policy_allowed:
        raise FetchError(
            "Search policy does not allow online fetches. "
            "Ask the user to set search_policy.online_search_allowed = true "
            "in .cryptoworkbench/workbench/config.yaml, or run offline."
        )
    if not per_fetch_consent:
        raise FetchError(
            "Per-fetch consent was not granted. The plugin must ask the user "
            "before every fetch; `policy_allowed=True` is a ceiling, not "
            "silent consent."
        )

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise FetchError(
            f"Refusing to fetch scheme {parsed.scheme!r}: only http/https are allowed."
        )

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as response:
            content_type = response.headers.get("Content-Type", "")
            # Read with an upper bound to avoid runaway downloads.
            body = response.read(max_bytes + 1)
    except urllib.error.URLError as exc:
        raise FetchError(f"Could not fetch {url}: {exc}") from exc

    if len(body) > max_bytes:
        raise FetchError(
            f"Response exceeded {max_bytes} bytes; refusing to save. "
            "Ask the user to download manually if the resource is intended."
        )

    fetched_dir = Path(workbench_root) / "corpus" / "fetched"
    fetched_dir.mkdir(parents=True, exist_ok=True)

    filename = _safe_filename_from_url(url, content_type)
    out_path = fetched_dir / filename

    # If a file with the same name already exists, add a short content hash
    # to disambiguate rather than overwriting.
    if out_path.exists():
        digest_short = hashlib.sha256(body).hexdigest()[:8]
        stem = out_path.stem
        out_path = fetched_dir / f"{stem}.{digest_short}{out_path.suffix}"

    out_path.write_bytes(body)

    provenance = {
        "url": url,
        "path": str(out_path),
        "content_type": content_type,
        "size_bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "reason": reason,
        "fetcher": MODULE,
    }
    return provenance


def run(**context: Any) -> dict[str, Any]:
    """Workflow entry: fetch a URL given context kwargs.

    Required context: url, workbench_root, policy_allowed, per_fetch_consent.
    """
    try:
        provenance = fetch_url(
            url=context["url"],
            workbench_root=context.get("workbench_root", ".cryptoworkbench"),
            policy_allowed=bool(context.get("policy_allowed", False)),
            per_fetch_consent=bool(context.get("per_fetch_consent", False)),
            reason=context.get("reason", ""),
        )
        return {"module": MODULE, "status": "fetched", "provenance": provenance}
    except FetchError as exc:
        return {"module": MODULE, "status": "refused", "reason": str(exc)}

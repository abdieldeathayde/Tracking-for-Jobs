import re
from urllib.parse import urlparse, urlunparse


def validate_http_url(url: str) -> str:
    cleaned_url = (url or "").strip()
    parsed = urlparse(cleaned_url)

    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Informe uma URL válida.")

    return cleaned_url


def normalize_url_key(url: str) -> tuple[str, str]:
    parsed_url = urlparse((url or "").strip())
    hostname = parsed_url.netloc.casefold()
    path = parsed_url.path.rstrip("/").casefold()

    if hostname.endswith("linkedin.com"):
        hostname = "linkedin.com"
        job_id = re.search(r"/jobs/view/(?:.*-)?(\d+)$", path)
        if job_id:
            path = f"/jobs/view/{job_id.group(1)}"

    return hostname, path


def canonical_linkedin_url(url: str) -> str:
    cleaned_url = (url or "").strip()
    parsed = urlparse(cleaned_url)
    hostname = parsed.netloc.casefold()

    if hostname.endswith("linkedin.com"):
        job_id = re.search(r"/jobs/view/(?:.*-)?(\d+)/?$", parsed.path.casefold())
        if job_id:
            clean_path = f"/jobs/view/{job_id.group(1)}/"
            return urlunparse(("https", "www.linkedin.com", clean_path, "", "", ""))

    return cleaned_url


def detect_platform(url: str) -> str:
    hostname = urlparse((url or "").strip()).netloc.casefold()

    if hostname.endswith("linkedin.com"):
        return "LinkedIn"
    if hostname.endswith("gupy.io"):
        return "Gupy"
    if hostname.endswith("indeed.com"):
        return "Indeed"
    return "Outra"
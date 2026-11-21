import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
PACKAGE_DIR = Path(__file__).resolve().parent

# Prioriza .env na raiz do workspace; usa jobapply/.env como fallback.
load_dotenv(ROOT_DIR / ".env")
load_dotenv(PACKAGE_DIR / ".env")

DATA_DIR = ROOT_DIR / "data"
CV_DIR = DATA_DIR / "curriculo"
LOG_DIR = ROOT_DIR / "logs"

EXCEL_PATH = DATA_DIR / "vagas.xlsx"

CV_INFRA_PATH = ROOT_DIR / os.getenv(
    "CV_INFRA_PATH",
    "data/curriculo/Abdiel_CV_Infraestrutura.pdf"
)

CV_DEV_PATH = ROOT_DIR / os.getenv(
    "CV_DEV_PATH",
    "data/curriculo/Abdiel_CV_Desenvolvimento.pdf"
)

VALID_BROWSERS = {"edge", "chrome", "firefox"}


def _parse_browser(raw_value: str) -> str:
    browser = raw_value.strip().lower()
    if browser not in VALID_BROWSERS:
        raise ValueError(
            f"BROWSER inválido: '{raw_value}'. "
            f"Use um de: {', '.join(sorted(VALID_BROWSERS))}."
        )
    return browser


def _parse_positive_int(name: str, raw_value: str) -> int:
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValueError(f"{name} deve ser um número inteiro válido.") from error

    if value <= 0:
        raise ValueError(f"{name} deve ser maior que zero.")
    return value


def _parse_non_negative_float(name: str, raw_value: str) -> float:
    try:
        value = float(raw_value)
    except ValueError as error:
        raise ValueError(f"{name} deve ser um número válido.") from error

    if value < 0:
        raise ValueError(f"{name} não pode ser negativo.")
    return value


BROWSER = _parse_browser(os.getenv("BROWSER", "edge"))

HEADLESS = os.getenv("HEADLESS", "false").strip().lower() == "true"

WAIT_SECONDS = _parse_positive_int(
    "WAIT_SECONDS",
    os.getenv("WAIT_SECONDS", "15")
)

REQUEST_DELAY_MIN = _parse_non_negative_float(
    "REQUEST_DELAY_MIN",
    os.getenv("REQUEST_DELAY_MIN", "2.0")
)

REQUEST_DELAY_MAX = _parse_non_negative_float(
    "REQUEST_DELAY_MAX",
    os.getenv("REQUEST_DELAY_MAX", "5.0")
)

if REQUEST_DELAY_MAX < REQUEST_DELAY_MIN:
    REQUEST_DELAY_MAX = REQUEST_DELAY_MIN

_raw_profile_dir = os.getenv("BROWSER_PROFILE_DIR", "").strip()
BROWSER_PROFILE_DIR = Path(_raw_profile_dir) if _raw_profile_dir else None

PLATFORMS = {
    "linkedin": (
        "https://www.linkedin.com/jobs/search/"
        "?keywords={query}&location={location}"
    ),
    "gupy": "https://portal.gupy.io/",
    "indeed": (
        "https://br.indeed.com/jobs"
        "?q={query}&l={location}"
    ),
}
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent

load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ROOT_DIR / "data"
CV_DIR = DATA_DIR / "curriculo"
LOG_DIR = ROOT_DIR / "vagas.xlsx"

EXCEL_PATH = DATA_DIR / "vagas.xlsx"

CV_INFRA_PATH = ROOT_DIR / os.getenv(
    "CV_INFRA_PATH",
    "data/curriculo/Abdiel_CV_Infraestrutura.pdf"
)

CV_DEV_PATH = ROOT_DIR / os.getenv(
    "CV_DEV_PATH",
    "data/curriculo/Abdiel_CV_desenvolvimento.pdf"
)

BROWSER = os.getenv("BROWSER", "edge").lower()

HEADLESS = (
    os.getenv("HEADLESS", "false").lower() == "true"
)

WAIT_SECONDS = int(
    os.getenv("WAIT_SECONDS", "15")
)

PLATFORMS = {
    "linkedin": (
        "https://www.linkedin.com/jobs/search/"
        "?keywords={query}&Location={location}"
    ),

    "gupy": "https://portal.gupy.io/",

    "indeed": (
        "https://br.indeed.com/jobs"
        "?q={query}&l={location}"
    )
}

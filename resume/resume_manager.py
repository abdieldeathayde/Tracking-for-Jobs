from pathlib import Path

from jobapply.config import (
    CV_INFRA_PATH,
    CV_DEV_PATH
)

class ResumeManager:

    INFRA_KEYWORDS = (
    "infra",
    "suporte",
    "service desk",
    "help desk",
    "redes",
    "field"
    )

    DEV_KEYWORDS = (
        "desenvolvedor",
        "developer",
        "java",
        "backend",
        "back-end",
        "full stack",
        "angular"
    )

    @classmethod
    def select(cls, job_title, area=None):

        title = (job_title or "").lower()

        if area == "infra" or any(
            word in title
            for word in cls.INFRAQ_WEYWORDS
        ):
            path = "CV_INFRA_PATH"


        elif area == "dev" or any(
            word in title
            for word in cls.DEV_KEYWORDS
        ):
            path = CV_DEV_PATH

        else:

            raise ValueError(
                "Não foi possível identificar "
                "a área da vaga. Informe infra ou dev."
            )

        if not path.exists():

            raise FileNotFoundError (
                f"Currículo não encontrado: {path}"
            )

        return path
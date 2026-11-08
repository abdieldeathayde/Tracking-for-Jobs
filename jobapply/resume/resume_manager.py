import unicodedata
from pathlib import Path

from jobapply.config import (
    CV_INFRA_PATH,
    CV_DEV_PATH
)

class ResumeManager:

    INFRA_KEYWORDS = (
        "infra",
        "suporte",
        "analista de ti",
        "analista de suporte",
        "service desk",
        "help desk",
        "redes",
        "field",
        "ciberseguranca",
        "cybersecurity",
        "cyber security",
        "seguranca da informacao",
        "information security",
        "seguranca",
        "security",
        "soc"
    )

    DEV_KEYWORDS = (
        "desenvolvedor",
        "desenvolvimento",
        "developer",
        "programador",
        "programacao",
        "engenheiro de software",
        "software engineer",
        "java",
        "backend",
        "back-end",
        "frontend",
        "front-end",
        "full stack",
        "fullstack",
        "angular",
        "python"
    )

    @classmethod
    def select(cls, job_title, area=None):

        if area not in (None, "infra", "dev"):
            raise ValueError(
                "A área deve ser 'infra' ou 'dev'."
            )

        normalized_title = unicodedata.normalize(
            "NFKD",
            job_title or ""
        )
        title = "".join(
            character
            for character in normalized_title
            if not unicodedata.combining(character)
        ).casefold()

        if area == "infra" or (
            area is None and (
                any(
                    keyword in title
                    for keyword in cls.INFRA_KEYWORDS
                    if keyword != "soc"
                )
                or " soc " in f" {title} "
            )
        ):
            path = CV_INFRA_PATH

        elif area == "dev" or (
            area is None and any(
                keyword in title
                for keyword in cls.DEV_KEYWORDS
            )
        ):
            path = CV_DEV_PATH

        else:

            raise ValueError(
                "Não foi possível identificar "
                "a área da vaga pelo cargo. Informe "
                "'infra' ou 'dev' manualmente."
            )

        if not path.exists():

            raise FileNotFoundError(
                f"Currículo não encontrado: {path}"
            )

        return path
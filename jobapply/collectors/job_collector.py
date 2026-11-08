from datetime import datetime
from urllib.parse import urlparse

class JobCollector:

    @staticmethod
    def build_record(
        company,
        title,
        url,
        modality = "Não informado",
        location = "Não informado",
        platform = "Outra"
    ):
        company = company.strip()
        title = title.strip()
        url = url.strip()
        parsed_url = urlparse(url)

        if not company:
            raise ValueError("Informe o nome da empresa.")

        if not title:
            raise ValueError("Informe o cargo da vaga.")

        if (
            parsed_url.scheme not in ("http", "https")
            or not parsed_url.netloc
        ):
            raise ValueError(
                "Informe uma URL válida."
            )

        return {

            "company": company,
            "title": title,
            "modality": modality,
            "location": location,
            "platform": platform,
            "salary": "Não informado",
            "requirements": "",
            "compatibility": "",
            "url": url,
            "found_date": datetime.now().date().isoformat(),
            "application_status": "Não iniciada",
            "curriculum": "",

            "notes": (
                "Dados inseridos pelo usuário. "
                "Confirmar na página oficial."
            )
        }

from datetime import datetime

from jobapply.utils.urls import validate_http_url


class JobCollector:

    @staticmethod
    def build_record(
        company,
        title,
        url,
        modality="Não informado",
        location="Não informado",
        platform="Outra",
    ):
        company = company.strip()
        title = title.strip()
        url = validate_http_url(url)

        if not company:
            raise ValueError("Informe o nome da empresa.")

        if not title:
            raise ValueError("Informe o cargo da vaga.")

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
            ),
        }
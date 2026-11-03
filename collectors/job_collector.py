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
        parsed_url = urlparse(url)


        if (
            parsed_url.scheme not in ("http", "https")
            or not parsed_url.netloc
        ):
            raise.ValueError(
                "Informe uma URL válida."
            )

        return {

            "company": company.strip(),
            "title": title.strip(),
            "modality": modality,
            "location": location,
            "platform": platform,
            "salary": "Não informado",
            "requirements": "",
            "compability": "",
            "url": url.strip(),
            "found_date": datetime.now().date().isoformat()
            "application_status": "Não iniciada",
            "curriculum": "",

            "notes": (
                "Dados inseridos pelo usuário. "
                "Confirmar na página oficiel."
            )
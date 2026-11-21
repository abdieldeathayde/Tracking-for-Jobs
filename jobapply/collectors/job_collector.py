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
<<<<<<< HEAD:jobapply/collectors/job_collector.py
        url = url.strip()
        parsed_url = urlparse(url)

        if not company:
            raise ValueError("Informe o nome da empresa.")

        if not title:
            raise ValueError("Informe o cargo da vaga.")
=======
        url = validate_http_url(url)

        if not company:
            raise ValueError("Informe o nome da empresa.")
>>>>>>> trabalho-local:collectors/job_collector.py

        if not title:
            raise ValueError("Informe o cargo da vaga.")

        return {
<<<<<<< HEAD:jobapply/collectors/job_collector.py

=======
>>>>>>> trabalho-local:collectors/job_collector.py
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
<<<<<<< HEAD:jobapply/collectors/job_collector.py
            )
        }
=======
            ),
        }
>>>>>>> trabalho-local:collectors/job_collector.py

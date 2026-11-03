import re
from urllib.parse import urlencode, urlparse

from selenium.webdriver.common.by import By

from jobapply.collectors.job_collector import JobCollector


class LinkedInCollector:

    CARD_SELECTOR = ".job-search-card"
    WORKPLACE_TYPES = {
        "Presencial": "1",
        "Remoto": "2",
        "Híbrido": "3"
    }

    @classmethod
    def search_url(cls, query, location, modalities):
        parameters = {
            "keywords": query,
            "location": location
        }

        workplace_types = [
            cls.WORKPLACE_TYPES[modality]
            for modality in modalities
        ]
        if workplace_types:
            parameters["f_WT"] = ",".join(workplace_types)

        return (
            "https://www.linkedin.com/jobs/search/?"
            f"{urlencode(parameters)}"
        )

    @staticmethod
    def _element_text(card, selector):
        elements = card.find_elements(
            By.CSS_SELECTOR,
            selector
        )
        if not elements:
            return ""
        return elements[0].text.strip()

    @classmethod
    def collect(cls, driver, query, search_location):
        records = []
        cards = driver.find_elements(
            By.CSS_SELECTOR,
            cls.CARD_SELECTOR
        )

        for card in cards:
            link = card.find_element(
                By.CSS_SELECTOR,
                "a.base-card__full-link"
            )
            url = link.get_attribute("href")
            title = (
                link.get_attribute("aria-label")
                or link.text
            ).strip()
            company = cls._element_text(
                card,
                "a.hidden-nested-link"
            )
            location = cls._element_text(
                card,
                ".job-search-card__location"
            )

            if not title or not url:
                continue

            record = JobCollector.build_record(
                company=company or "Não informado",
                title=title,
                url=url,
                modality=cls._modality(card.text),
                location=location or search_location,
                platform="LinkedIn"
            )
            record["notes"] = (
                f"Encontrada na busca do LinkedIn: {query}"
            )
            records.append(record)

        return records

    @staticmethod
    def _modality(text):
        normalized_text = text.casefold()

        if "remote" in normalized_text or "remoto" in normalized_text:
            return "Remoto"
        if "hybrid" in normalized_text or "híbrido" in normalized_text:
            return "Híbrido"
        if "on-site" in normalized_text or "presencial" in normalized_text:
            return "Presencial"
        return "Não informado"

    @staticmethod
    def unique_records(records):
        unique = {}

        for record in records:
            unique.setdefault(
                LinkedInCollector._url_key(record["url"]),
                record
            )

        return list(unique.values())

    @staticmethod
    def _url_key(url):
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc.casefold()
        path = parsed_url.path.rstrip("/").casefold()

        if hostname.endswith("linkedin.com"):
            hostname = "linkedin.com"
            job_id = re.search(r"/jobs/view/(?:.*-)?(\d+)$", path)
            if job_id:
                path = f"/jobs/view/{job_id.group(1)}"

        return hostname, path

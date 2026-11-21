from urllib.parse import urlencode

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By

from jobapply.collectors.job_collector import JobCollector
from jobapply.utils.logger import get_logger
from jobapply.utils.urls import canonical_linkedin_url, normalize_url_key

logger = get_logger()


class LinkedInCollector:

    CARD_SELECTOR = ".job-search-card"
    WORKPLACE_TYPES = {
        "Presencial": "1",
        "Remoto": "2",
        "Híbrido": "3",
    }

    @classmethod
    def search_url(cls, query, location, modalities, easy_apply=False):
        parameters = {
            "keywords": query,
            "location": location,
        }

        workplace_types = [
            cls.WORKPLACE_TYPES[modality]
            for modality in modalities
        ]
        if workplace_types:
            parameters["f_WT"] = ",".join(workplace_types)

        if easy_apply:
            parameters["f_AL"] = "true"

        return (
            "https://www.linkedin.com/jobs/search/?"
            f"{urlencode(parameters)}"
        )

    @staticmethod
    def is_authwall(driver) -> bool:
        current_url = (getattr(driver, "current_url", "") or "").casefold()
        return any(
            marker in current_url
            for marker in (
                "linkedin.com/authwall",
                "linkedin.com/login",
                "linkedin.com/checkpoint",
            )
        )

    @staticmethod
    def _element_text(card, selector):
        elements = card.find_elements(By.CSS_SELECTOR, selector)
        if not elements:
            return ""
        return elements[0].text.strip()

    @classmethod
    def collect(cls, driver, query, search_location):
        records = []
        cards = driver.find_elements(By.CSS_SELECTOR, cls.CARD_SELECTOR)

        for card in cards:
            try:
                link = card.find_element(
                    By.CSS_SELECTOR,
                    "a.base-card__full-link",
                )
                raw_url = link.get_attribute("href")
                title = (
                    link.get_attribute("aria-label")
                    or link.text
                    or ""
                ).strip()
                company = cls._element_text(card, "a.hidden-nested-link")
                location = cls._element_text(
                    card,
                    ".job-search-card__location",
                )
                card_text = card.text or ""
            except (NoSuchElementException, StaleElementReferenceException) as error:
                logger.warning("Card ignorado durante coleta no LinkedIn: %s", error)
                continue

            if not title or not raw_url:
                continue

            clean_url = canonical_linkedin_url(raw_url)
            record = JobCollector.build_record(
                company=company or "Não informado",
                title=title,
                url=clean_url,
                modality=cls._modality(card_text),
                location=location or search_location,
                platform="LinkedIn",
            )
            record["notes"] = f"Encontrada na busca do LinkedIn: {query}"
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
                normalize_url_key(record["url"]),
                record,
            )

        return list(unique.values())
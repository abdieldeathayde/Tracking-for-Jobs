from urllib.parse import parse_qs, urlparse

from jobapply.collectors.linkedin_collector import LinkedInCollector


class FakeElement:
    def __init__(self, text="", attributes=None, children=None):
        self.text = text
        self.attributes = attributes or {}
        self.children = children or {}

    def get_attribute(self, name):
        return self.attributes.get(name)

    def find_elements(self, by, selector):
        return self.children.get(selector, [])

    def find_element(self, by, selector):
        return self.find_elements(by, selector)[0]


class FakeDriver:
    def __init__(self, cards):
        self.cards = cards

    def find_elements(self, by, selector):
        if selector == LinkedInCollector.CARD_SELECTOR:
            return self.cards
        return []


def test_search_url_encodes_query_location_and_workplace_filters():
    url = LinkedInCollector.search_url(
        "Fullstack developer",
        "Blumenau SC",
        ["Remoto", "Híbrido", "Presencial"]
    )
    parameters = parse_qs(urlparse(url).query)

    assert parameters["keywords"] == ["Fullstack developer"]
    assert parameters["location"] == ["Blumenau SC"]
    assert parameters["f_WT"] == ["2,3,1"]


def test_collect_extracts_linkedin_job_card():
    link = FakeElement(
        text="Desenvolvedor Java Pleno",
        attributes={
            "href": "https://www.linkedin.com/jobs/view/123/",
            "aria-label": "Desenvolvedor Java Pleno"
        }
    )
    card = FakeElement(
        text="Desenvolvedor Java Pleno\nBionexo\nHíbrido",
        children={
            "a.base-card__full-link": [link],
            "a.hidden-nested-link": [FakeElement(text="Bionexo")],
            ".job-search-card__location": [
                FakeElement(text="Blumenau, Santa Catarina, Brazil")
            ]
        }
    )

    records = LinkedInCollector.collect(
        FakeDriver([card]),
        "Java Developer",
        "Blumenau SC"
    )

    assert records == [{
        "company": "Bionexo",
        "title": "Desenvolvedor Java Pleno",
        "modality": "Híbrido",
        "location": "Blumenau, Santa Catarina, Brazil",
        "platform": "LinkedIn",
        "salary": "Não informado",
        "requirements": "",
        "compability": "",
        "url": "https://www.linkedin.com/jobs/view/123/",
        "found_date": records[0]["found_date"],
        "application_status": "Não iniciada",
        "curriculum": "",
        "notes": "Encontrada na busca do LinkedIn: Java Developer"
    }]


def test_unique_records_ignores_tracking_query_parameters():
    records = [
        {
            "url": "https://www.linkedin.com/jobs/view/java-developer-123/"
            "?trackingId=first"
        },
        {
            "url": "https://br.linkedin.com/jobs/view/123/"
            "?trackingId=second"
        },
        {"url": "https://www.linkedin.com/jobs/view/456/"}
    ]

    assert LinkedInCollector.unique_records(records) == [
        records[0],
        records[2]
    ]

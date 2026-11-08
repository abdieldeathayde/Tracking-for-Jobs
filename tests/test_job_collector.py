import pytest

from jobapply.collectors.job_collector import JobCollector


def test_build_record():

    record = JobCollector.build_record(
        company="Empresa Exemplo",
        title="Analista de Infraestrutura",
        url="https://example.com/vaga"
    )

    assert record["company"] == "Empresa Exemplo"

    assert record["title"] == "Analista de Infraestrutura"

    assert record["application_status"] == "Não iniciada"


def test_invalid_url():

    with pytest.raises(ValueError):

        JobCollector.build_record(
            company="Empresa",
            title="Analista",
            url="url-invalida"
        )


def test_build_record_strips_whitespace_from_fields():
    record = JobCollector.build_record(
        company=" Empresa Exemplo ",
        title=" Analista ",
        url=" https://example.com/vaga "
    )

    assert record["company"] == "Empresa Exemplo"
    assert record["title"] == "Analista"
    assert record["url"] == "https://example.com/vaga"


@pytest.mark.parametrize(
    ("company", "title", "expected_message"),
    [
        (" ", "Analista", "Informe o nome da empresa"),
        ("Empresa", " ", "Informe o cargo da vaga"),
    ]
)
def test_build_record_requires_company_and_title(
    company,
    title,
    expected_message
):
    with pytest.raises(ValueError, match=expected_message):
        JobCollector.build_record(
            company=company,
            title=title,
            url="https://example.com/vaga"
        )
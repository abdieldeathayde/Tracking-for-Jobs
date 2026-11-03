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
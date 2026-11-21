from jobapply.reporting.pdf_report import generate_applications_pdf


def sample_jobs():
    return [
        {
            "ID": 1,
            "Empresa": "Empresa A",
            "Cargo": "Desenvolvedor Python",
            "Modalidade": "Remoto",
            "Localidade": "Blumenau, SC",
            "Salário": "Não informado",
            "Requisitos": "Python, APIs",
            "Compatibilidade (%)": "",
            "Link da vaga": "https://example.com/jobs/1",
            "Plataforma": "LinkedIn",
            "Data encontrada": "2026-11-20",
            "Data da candidatura": "2026-11-21",
            "Status da candidatura": "Enviada",
            "Situação da vaga": "Aberta",
            "Currículo utilizado": "cv-dev.pdf",
            "Observações": "Candidatura enviada",
        },
        {
            "ID": 2,
            "Empresa": "Empresa B",
            "Cargo": "Analista de Suporte",
            "Modalidade": "Híbrido",
            "Localidade": "Gaspar, SC",
            "Salário": "Não informado",
            "Requisitos": "",
            "Compatibilidade (%)": "",
            "Link da vaga": "https://example.com/jobs/2",
            "Plataforma": "Gupy",
            "Data encontrada": "2026-11-20",
            "Data da candidatura": "",
            "Status da candidatura": "Não iniciada",
            "Situação da vaga": "Aberta / não verificada",
            "Currículo utilizado": "",
            "Observações": "",
        },
        {
            "ID": 3,
            "Empresa": "Empresa C",
            "Cargo": "Analista de TI Júnior",
            "Modalidade": "Presencial",
            "Localidade": "Blumenau, SC",
            "Salário": "Não informado",
            "Requisitos": "",
            "Compatibilidade (%)": "",
            "Link da vaga": "https://example.com/jobs/3",
            "Plataforma": "LinkedIn",
            "Data encontrada": "2026-11-19",
            "Data da candidatura": "2026-11-20",
            "Status da candidatura": "Em análise",
            "Situação da vaga": "Aberta",
            "Currículo utilizado": "cv-infra.pdf",
            "Observações": "Aguardando retorno",
        },
    ]


def test_generate_applications_pdf_creates_file(tmp_path):
    output = tmp_path / "report.pdf"

    result = generate_applications_pdf(sample_jobs(), output)

    assert result["total"] == 3
    assert output.exists()
    assert output.stat().st_size > 0
    assert output.read_bytes().startswith(b"%PDF")


def test_generate_applications_pdf_applied_only_filters_not_started(tmp_path):
    output = tmp_path / "applied.pdf"

    result = generate_applications_pdf(sample_jobs(), output, applied_only=True)

    assert result["total"] == 2
    assert result["applied_only"] is True
    assert output.exists()


def test_generate_applications_pdf_filters_by_status(tmp_path):
    output = tmp_path / "sent.pdf"

    result = generate_applications_pdf(
        sample_jobs(),
        output,
        statuses=["Enviada"],
    )

    assert result["total"] == 1
    assert result["statuses"] == ["Enviada"]
    assert output.exists()


def test_generate_applications_pdf_handles_empty_result(tmp_path):
    output = tmp_path / "empty.pdf"

    result = generate_applications_pdf([], output, applied_only=True)

    assert result["total"] == 0
    assert output.exists()
    assert output.read_bytes().startswith(b"%PDF")

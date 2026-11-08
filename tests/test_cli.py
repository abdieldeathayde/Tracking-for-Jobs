import sys

import main as cli
from jobapply.spreadsheet.excel_manager import ExcelManager


def test_list_command_filters_jobs_by_status(
    tmp_path,
    monkeypatch,
    capsys
):
    workbook_path = tmp_path / "jobs.xlsx"
    manager = ExcelManager(workbook_path)
    manager.add_jobs([
        {
            "company": "Empresa A",
            "title": "Desenvolvedor",
            "url": "https://example.com/jobs/1"
        },
        {
            "company": "Empresa B",
            "title": "Analista",
            "url": "https://example.com/jobs/2"
        }
    ])
    manager.update_application_status(2, "Em análise")

    monkeypatch.setattr(cli, "EXCEL_PATH", workbook_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "list", "--status", "Em análise"]
    )

    cli.main()

    output = capsys.readouterr().out
    assert "Analista" in output
    assert "Desenvolvedor" not in output


def test_summary_command_displays_status_counts(
    tmp_path,
    monkeypatch,
    capsys
):
    workbook_path = tmp_path / "jobs.xlsx"
    manager = ExcelManager(workbook_path)
    manager.add_job({
        "title": "Desenvolvedor",
        "url": "https://example.com/jobs/1"
    })

    monkeypatch.setattr(cli, "EXCEL_PATH", workbook_path)
    monkeypatch.setattr(sys, "argv", ["main.py", "summary"])

    cli.main()

    output = capsys.readouterr().out
    assert "Total de vagas: 1" in output
    assert "Não iniciada" in output

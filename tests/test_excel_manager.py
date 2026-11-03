import pytest
from openpyxl import load_workbook

from jobapply.spreadsheet.excel_manager import ExcelManager


def test_add_jobs_skips_duplicate_job_urls(tmp_path):
    manager = ExcelManager(tmp_path / "jobs.xlsx")
    first = {
        "company": "Empresa A",
        "title": "Java Developer",
        "url": (
            "https://www.linkedin.com/jobs/view/java-developer-123/"
            "?trackingId=first"
        ),
        "platform": "LinkedIn"
    }
    duplicate = {
        **first,
        "url": (
            "https://br.linkedin.com/jobs/view/123/"
            "?trackingId=second"
        )
    }

    assert manager.add_jobs([first, duplicate]) == 1
    assert manager.add_jobs([first]) == 0

    workbook = load_workbook(manager.path)
    worksheet = workbook["Vagas"]
    assert worksheet.max_row == 2
    assert worksheet["C2"].value == "Java Developer"


def test_list_jobs_and_update_application_status(tmp_path):
    manager = ExcelManager(tmp_path / "jobs.xlsx")
    manager.add_jobs([
        {
            "company": "Empresa A",
            "title": "Java Developer",
            "url": "https://example.com/jobs/1",
            "platform": "LinkedIn"
        },
        {
            "company": "Empresa B",
            "title": "Analista de Suporte",
            "url": "https://example.com/jobs/2",
            "platform": "LinkedIn"
        }
    ])

    assert manager.update_application_status(2, "Em análise")

    all_jobs = manager.list_jobs()
    filtered_jobs = manager.list_jobs(status="Em análise")

    assert [job["ID"] for job in all_jobs] == [1, 2]
    assert [job["Cargo"] for job in filtered_jobs] == [
        "Analista de Suporte"
    ]
    assert not manager.update_application_status(99, "Enviada")


def test_update_application_status_rejects_unknown_status(tmp_path):
    manager = ExcelManager(tmp_path / "jobs.xlsx")

    with pytest.raises(ValueError, match="Status inválido"):
        manager.update_application_status(1, "Enviado")


def test_new_job_id_follows_highest_existing_id_after_deletion(tmp_path):
    manager = ExcelManager(tmp_path / "jobs.xlsx")
    manager.add_jobs([
        {
            "title": "Job 1",
            "url": "https://example.com/jobs/1"
        },
        {
            "title": "Job 2",
            "url": "https://example.com/jobs/2"
        },
        {
            "title": "Job 3",
            "url": "https://example.com/jobs/3"
        }
    ])

    workbook = load_workbook(manager.path)
    worksheet = workbook["Vagas"]
    worksheet.delete_rows(3)
    workbook.save(manager.path)
    workbook.close()

    manager.add_job({
        "title": "Job 4",
        "url": "https://example.com/jobs/4"
    })

    assert [job["ID"] for job in manager.list_jobs()] == [1, 3, 4]

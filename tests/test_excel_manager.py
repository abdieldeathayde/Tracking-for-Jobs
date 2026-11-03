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

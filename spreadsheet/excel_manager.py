from datetime import date
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

from jobapply.utils.urls import normalize_url_key


HEADERS = [
    "ID",
    "Empresa",
    "Cargo",
    "Modalidade",
    "Localidade",
    "Salário",
    "Requisitos",
    "Compatibilidade (%)",
    "Link da vaga",
    "Plataforma",
    "Data encontrada",
    "Data da candidatura",
    "Status da candidatura",
    "Situação da vaga",
    "Currículo utilizado",
    "Observações",
]

APPLICATION_STATUSES = [
    "Não iniciada",
    "Em progresso",
    "Enviada",
    "Em análise",
    "Entrevista",
    "Congelada",
    "Desclassificado",
    "Aprovado",
    "Recusada",
    "Encerrada",
]

_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


class ExcelManager:

    def __init__(self, path):
        self.path = Path(path)

    @staticmethod
    def _sanitize_text(value):
        if not isinstance(value, str):
            return value
        if value.startswith(_FORMULA_PREFIXES):
            return f"'{value}"
        return value

    def ensure_workbook(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if self.path.exists():
            return

        workbook = Workbook()
        ws = workbook.active
        ws.title = "Vagas"
        ws.append(HEADERS)
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = "A1:P1"

        widths = [
            9, 24, 30, 16, 24, 18,
            42, 18, 48, 16, 16, 20,
            23, 24, 38, 48,
        ]

        for index, width in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(index)].width = width

        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="17365D")
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )

        ws.row_dimensions[1].height = 32

        status_validation = DataValidation(
            type="list",
            formula1=(
                '"Não iniciada,Em progresso,Enviada,'
                'Em análise,Entrevista,Congelada,'
                'Desclassificado,Aprovado,'
                'Recusada,Encerrada"'
            ),
            allow_blank=True,
        )
        ws.add_data_validation(status_validation)
        status_validation.add("M2:M10000")

        job_validation = DataValidation(
            type="list",
            formula1=(
                '"Aberta / não verificada,'
                'Aberta,Fechada,Congelada,'
                'Não confirmada"'
            ),
            allow_blank=True,
        )
        ws.add_data_validation(job_validation)
        job_validation.add("N2:N10000")

        modality_validation = DataValidation(
            type="list",
            formula1='"Remoto,Híbrido,Presencial,Não informado"',
            allow_blank=True,
        )
        ws.add_data_validation(modality_validation)
        modality_validation.add("D2:D10000")

        colors = {
            "Aprovado": "C6EFCE",
            "Desclassificado": "FFC7CE",
            "Congelada": "FFEB9C",
            "Em progresso": "DDEBF7",
        }
        for status, color in colors.items():
            rule = FormulaRule(
                formula=[f'$M2="{status}"'],
                fill=PatternFill("solid", fgColor=color),
            )
            ws.conditional_formatting.add("M2:M10000", rule)

        table = Table(displayName="TabelaVagas", ref="A1:P1")
        table.tableStyleInfo = TableStyleInfo(
            name="TableStyleMedium2",
            showRowStripes=True,
            showColumnStripes=False,
        )
        ws.add_table(table)

        dashboard = workbook.create_sheet("Dashboard")
        dashboard["A1"] = "JOB APPLY AUTOMATION - DASHBOARD"
        dashboard["A1"].font = Font(size=15, bold=True, color="17365D")

        metrics = [
            ("Total de vagas", "=COUNTA(Vagas!C:C)-1"),
            (
                "Candidaturas enviadas",
                '=COUNTIF(Vagas!M:M,"Enviada")'
                '+COUNTIF(Vagas!M:M,"Em análise")'
                '+COUNTIF(Vagas!M:M,"Entrevista")'
                '+COUNTIF(Vagas!M:M,"Aprovado")'
                '+COUNTIF(Vagas!M:M,"Desclassificado")',
            ),
            ("Em progresso", '=COUNTIF(Vagas!M:M,"Em progresso")'),
            ("Congeladas", '=COUNTIF(Vagas!M:M,"Congelada")'),
            ("Aprovadas", '=COUNTIF(Vagas!M:M,"Aprovado")'),
            ("Desclassificadas", '=COUNTIF(Vagas!M:M,"Desclassificado")'),
        ]

        for row, (label, formula) in enumerate(metrics, start=3):
            dashboard.cell(row, 1, label).font = Font(bold=True)
            dashboard.cell(row, 2, formula)

        dashboard.column_dimensions["A"].width = 30
        dashboard.column_dimensions["B"].width = 22
        dashboard.freeze_panes = "A3"

        workbook.save(self.path)

    def add_job(self, record):
        return self.add_jobs([record])

    def add_jobs(self, records):
        records = list(records)
        if not records:
            return 0

        self.ensure_workbook()
        workbook = load_workbook(self.path)

        try:
            ws = workbook["Vagas"]
            existing_urls = {
                normalize_url_key(row[8])
                for row in ws.iter_rows(min_row=2, values_only=True)
                if row[8]
            }
            added = 0
            existing_ids = [
                row[0]
                for row in ws.iter_rows(min_row=2, max_col=1, values_only=True)
                if isinstance(row[0], int)
            ]
            next_id = max(existing_ids, default=0) + 1

            for record in records:
                url = record.get("url", "")
                url_key = normalize_url_key(url)
                if url_key in existing_urls:
                    continue

                values = [
                    next_id,
                    self._sanitize_text(record.get("company", "")),
                    self._sanitize_text(record.get("title", "")),
                    self._sanitize_text(record.get("modality", "Não informado")),
                    self._sanitize_text(record.get("location", "Não informado")),
                    self._sanitize_text(record.get("salary", "Não informado")),
                    self._sanitize_text(record.get("requirements", "")),
                    self._sanitize_text(record.get("compatibility", "")),
                    url,
                    self._sanitize_text(record.get("platform", "Outra")),
                    record.get("found_date", ""),
                    record.get("application_date", ""),
                    record.get("application_status", "Não iniciada"),
                    record.get("job_status", "Aberta / não verificada"),
                    self._sanitize_text(record.get("curriculum", "")),
                    self._sanitize_text(record.get("notes", "")),
                ]

                ws.append(values)
                existing_urls.add(url_key)
                added += 1
                next_id += 1

                for cell in ws[ws.max_row]:
                    cell.alignment = Alignment(vertical="top", wrap_text=True)

            ws.tables["TabelaVagas"].ref = f"A1:P{ws.max_row}"
            workbook.save(self.path)
            return added
        finally:
            workbook.close()

    def register_assisted_application(self, record):
        """Adiciona a vaga como 'Em progresso' ou atualiza uma existente."""
        if self.add_job(record):
            return "added"

        self.ensure_workbook()
        workbook = load_workbook(self.path)
        target_key = normalize_url_key(record.get("url", ""))

        try:
            worksheet = workbook["Vagas"]
            for row in worksheet.iter_rows(min_row=2, min_col=1, max_col=16):
                cell_url = row[8].value or ""
                if normalize_url_key(cell_url) == target_key:
                    current_status = row[12].value
                    if current_status in (None, "", "Não iniciada"):
                        row[12].value = "Em progresso"
                    curriculum = record.get("curriculum", "")
                    if curriculum and not str(row[14].value or "").strip():
                        row[14].value = self._sanitize_text(curriculum)
                    workbook.save(self.path)
                    return "updated"
        finally:
            workbook.close()

        return "unchanged"

    def list_jobs(self, status=None):
        self.ensure_workbook()
        workbook = load_workbook(self.path, read_only=True, data_only=True)

        try:
            worksheet = workbook["Vagas"]
            rows = worksheet.iter_rows(min_row=2, values_only=True)
            jobs = [
                dict(zip(HEADERS, row))
                for row in rows
                if any(value is not None for value in row)
            ]
        finally:
            workbook.close()

        if status is not None:
            jobs = [
                job for job in jobs
                if job["Status da candidatura"] == status
            ]

        return jobs

    def get_summary(self):
        jobs = self.list_jobs()
        by_status = {status: 0 for status in APPLICATION_STATUSES}

        for job in jobs:
            status = job["Status da candidatura"] or "Não informado"
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total": len(jobs),
            "by_status": by_status,
        }

    def update_application_status(self, job_id, status):
        if status not in APPLICATION_STATUSES:
            raise ValueError(f"Status inválido: {status}")

        self.ensure_workbook()
        workbook = load_workbook(self.path)

        try:
            worksheet = workbook["Vagas"]
            for row in worksheet.iter_rows(min_row=2, min_col=1, max_col=13):
                if row[0].value == job_id:
                    row[12].value = status
                    if status == "Enviada" and not str(row[11].value or "").strip():
                        row[11].value = date.today().isoformat()
                    workbook.save(self.path)
                    return True
        finally:
            workbook.close()

        return False
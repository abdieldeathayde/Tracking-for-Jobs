from pathlib import Path
import re
from urllib.parse import urlparse

from openpyxl import Workbook, load_workbook

from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment
)

from openpyxl.worksheet.table import (
    Table,
    TableStyleInfo
)

from openpyxl.worksheet.datavalidation import (
    DataValidation
)

from openpyxl.formatting.rule import FormulaRule


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
    "Observações"
]


class ExcelManager:

    def __init__(self, path):

        self.path = Path(path)

    def ensure_workbook(self):

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

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
            23, 24, 38, 48
        ]

        for index, width in enumerate(widths, 1):

            ws.column_dimensions[
                chr(64 + index)
            ].width = width

        for cell in ws[1]:

            cell.font = Font(
                bold=True,
                color="FFFFFF"
            )

            cell.fill = PatternFill(
                "solid",
                fgColor="17365D"
            )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True
            )

        ws.row_dimensions[1].height = 32

        # Validação dos status

        status_validation = DataValidation(
            type="list",
            formula1=(
                '"Não iniciada,Em progresso,Enviada,'
                'Em análise,Entrevista,Congelada,'
                'Desclassificado,Aprovado,'
                'Recusada,Encerrada"'
            ),
            allow_blank=True
        )

        ws.add_data_validation(
            status_validation
        )

        status_validation.add("M2:M1000")

        # Situação da vaga

        job_validation = DataValidation(
            type="list",
            formula1=(
                '"Aberta / não verificada,'
                'Aberta,Fechada,Congelada,'
                'Não confirmada"'
            ),
            allow_blank=True
        )

        ws.add_data_validation(job_validation)

        job_validation.add("N2:N1000")

        # Modalidade

        modality_validation = DataValidation(
            type="list",
            formula1=(
                '"Remoto,Híbrido,Presencial,'
                'Não informado"'
            ),
            allow_blank=True
        )

        ws.add_data_validation(
            modality_validation
        )

        modality_validation.add("D2:D1000")

        # Cores por status

        colors = {
            "Aprovado": "C6EFCE",
            "Desclassificado": "FFC7CE",
            "Congelada": "FFEB9C",
            "Em progresso": "DDEBF7"
        }

        for status, color in colors.items():

            rule = FormulaRule(
                formula=[f'$M2="{status}"'],
                fill=PatternFill(
                    "solid",
                    fgColor=color
                )
            )

            ws.conditional_formatting.add(
                "M2:M1000",
                rule
            )

        table = Table(
            displayName="TabelaVagas",
            ref="A1:P1"
        )

        table.tableStyleInfo = TableStyleInfo(
            name="TableStyleMedium2",
            showRowStripes=True,
            showColumnStripes=False
        )

        ws.add_table(table)

        # Dashboard

        dashboard = workbook.create_sheet(
            "Dashboard"
        )

        dashboard["A1"] = (
            "JOB APPLY AUTOMATION - DASHBOARD"
        )

        dashboard["A1"].font = Font(
            size=15,
            bold=True,
            color="17365D"
        )

        metrics = [

            (
                "Total de vagas",
                '=COUNTA(Vagas!C:C)-1'
            ),

            (
                "Candidaturas enviadas",
                '=COUNTIF(Vagas!M:M,"Enviada")'
                '+COUNTIF(Vagas!M:M,"Em análise")'
                '+COUNTIF(Vagas!M:M,"Entrevista")'
                '+COUNTIF(Vagas!M:M,"Aprovado")'
                '+COUNTIF(Vagas!M:M,"Desclassificado")'
            ),

            (
                "Em progresso",
                '=COUNTIF(Vagas!M:M,"Em progresso")'
            ),

            (
                "Congeladas",
                '=COUNTIF(Vagas!M:M,"Congelada")'
            ),

            (
                "Aprovadas",
                '=COUNTIF(Vagas!M:M,"Aprovado")'
            ),

            (
                "Desclassificadas",
                '=COUNTIF(Vagas!M:M,"Desclassificado")'
            )
        ]

        for row, (label, formula) in enumerate(
            metrics,
            start=3
        ):

            dashboard.cell(
                row,
                1,
                label
            ).font = Font(bold=True)

            dashboard.cell(
                row,
                2,
                formula
            )

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

        workbook = load_workbook(
            self.path
        )

        ws = workbook["Vagas"]
        existing_urls = {
            self._url_key(row[8])
            for row in ws.iter_rows(
                min_row=2,
                values_only=True
            )
            if row[8]
        }
        added = 0

        for record in records:
            url = record.get("url", "")
            url_key = self._url_key(url)
            if url_key in existing_urls:
                continue

            values = [

                ws.max_row,

                record.get("company", ""),

                record.get("title", ""),

                record.get(
                    "modality",
                    "Não informado"
                ),

                record.get(
                    "location",
                    "Não informado"
                ),

                record.get(
                    "salary",
                    "Não informado"
                ),

                record.get("requirements", ""),

                record.get("compatibility", ""),

                url,

                record.get("platform", "Outra"),

                record.get("found_date", ""),

                record.get("application_date", ""),

                record.get(
                    "application_status",
                    "Não iniciada"
                ),

                record.get(
                    "job_status",
                    "Aberta / não verificada"
                ),

                record.get("curriculum", ""),

                record.get("notes", "")
            ]

            ws.append(values)
            existing_urls.add(url_key)
            added += 1

            for cell in ws[ws.max_row]:

                cell.alignment = Alignment(
                    vertical="top",
                    wrap_text=True
                )

        ws.tables["TabelaVagas"].ref = (
            f"A1:P{ws.max_row}"
        )

        workbook.save(self.path)
        return added

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

        return (
            hostname,
            path
        )
from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from jobapply.spreadsheet.excel_manager import APPLICATION_STATUSES


DEFAULT_REPORT_TITLE = "Relatório de candidaturas"


def _safe_text(value):
    if value is None:
        return ""
    text = str(value).strip()
    return text


class ApplicationsPDF(FPDF):
    def __init__(self, title=DEFAULT_REPORT_TITLE):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.report_title = title
        self._font_family = "Helvetica"
        self._configure_fonts()
        self.set_auto_page_break(auto=True, margin=15)

    def _configure_fonts(self):
        # Tenta usar fonte Unicode do Windows para suportar acentos; fallback para Helvetica.
        for font_name, regular, bold in (
            ("Arial", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
            ("DejaVu", r"C:\Windows\Fonts\DejaVuSans.ttf", r"C:\Windows\Fonts\DejaVuSans-Bold.ttf"),
        ):
            try:
                if Path(regular).exists():
                    self.add_font(font_name, "", regular)
                    if Path(bold).exists():
                        self.add_font(font_name, "B", bold)
                    else:
                        self.add_font(font_name, "B", regular)
                    self._font_family = font_name
                    return
            except Exception:
                continue
        self._font_family = "Helvetica"

    def header(self):
        self.set_font(self._font_family, "B", 14)
        self.cell(0, 10, self.report_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font(self._font_family, "", 9)
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cell(0, 6, f"Gerado em: {generated_at}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font(self._font_family, "", 8)
        self.cell(0, 8, f"Página {self.page_no()}", align="C")


def _filter_jobs(jobs, statuses=None, applied_only=False):
    selected = list(jobs)
    if statuses:
        allowed = set(statuses)
        selected = [job for job in selected if _safe_text(job.get("Status da candidatura")) in allowed]
    if applied_only:
        selected = [
            job for job in selected
            if _safe_text(job.get("Status da candidatura")) != "Não iniciada"
        ]
    return selected


def _status_summary(jobs):
    counts = {status: 0 for status in APPLICATION_STATUSES}
    for job in jobs:
        status = _safe_text(job.get("Status da candidatura")) or "Não informado"
        counts[status] = counts.get(status, 0) + 1
    return counts


def generate_applications_pdf(jobs, output_path, title=DEFAULT_REPORT_TITLE, statuses=None, applied_only=False):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    filtered_jobs = _filter_jobs(jobs, statuses=statuses, applied_only=applied_only)
    pdf = ApplicationsPDF(title=title)
    pdf.add_page()

    pdf.set_font(pdf._font_family, "B", 10)
    pdf.cell(
        0,
        7,
        f"Total de candidaturas no relatório: {len(filtered_jobs)}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_font(pdf._font_family, "", 9)

    summary = _status_summary(filtered_jobs)
    summary_parts = [f"{status}: {count}" for status, count in summary.items() if count > 0]
    if summary_parts:
        pdf.multi_cell(0, 5, "Resumo por status: " + " | ".join(summary_parts))
    pdf.ln(2)

    if not filtered_jobs:
        pdf.set_font(pdf._font_family, "", 10)
        pdf.multi_cell(0, 6, "Nenhuma candidatura encontrada para os filtros informados.")
        pdf.output(str(output_path))
        return {
            "output_path": output_path,
            "total": 0,
            "statuses": statuses or [],
            "applied_only": applied_only,
        }

    label_width = 35
    value_width = pdf.w - pdf.l_margin - pdf.r_margin - label_width

    for index, job in enumerate(filtered_jobs, start=1):
        if pdf.get_y() > 250:
            pdf.add_page()

        heading = f"{index}. {_safe_text(job.get('Cargo')) or 'Cargo não informado'} - {_safe_text(job.get('Empresa')) or 'Empresa não informada'}"
        pdf.set_font(pdf._font_family, "B", 10)
        pdf.multi_cell(0, 6, heading)
        pdf.set_font(pdf._font_family, "", 9)

        fields = [
            ("ID", job.get("ID", "")),
            ("Status", job.get("Status da candidatura", "")),
            ("Plataforma", job.get("Plataforma", "")),
            ("Modalidade", job.get("Modalidade", "")),
            ("Localidade", job.get("Localidade", "")),
            ("Data encontrada", job.get("Data encontrada", "")),
            ("Data candidatura", job.get("Data da candidatura", "")),
            ("Situação da vaga", job.get("Situação da vaga", "")),
            ("Currículo", job.get("Currículo utilizado", "")),
            ("Link", job.get("Link da vaga", "")),
            ("Observações", job.get("Observações", "")),
        ]

        for label, value in fields:
            value_text = _safe_text(value)
            if not value_text:
                continue
            x = pdf.get_x()
            y = pdf.get_y()
            pdf.set_font(pdf._font_family, "B", 9)
            pdf.multi_cell(label_width, 5, f"{label}:", border=0)
            next_y = pdf.get_y()
            pdf.set_xy(x + label_width, y)
            pdf.set_font(pdf._font_family, "", 9)
            pdf.multi_cell(value_width, 5, value_text, border=0)
            if pdf.get_y() < next_y:
                pdf.set_y(next_y)

        pdf.ln(2)
        y = pdf.get_y()
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
        pdf.ln(3)

    pdf.output(str(output_path))
    return {
        "output_path": output_path,
        "total": len(filtered_jobs),
        "statuses": statuses or [],
        "applied_only": applied_only,
    }

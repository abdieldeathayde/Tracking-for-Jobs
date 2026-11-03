import argparse
import sys
from pathlib import Path

from urllib.parse import quote_plus

from selenium.common.exceptions import (
    InvalidSessionIdException,
    TimeoutException
)
from selenium.webdriver.support.ui import WebDriverWait

if __package__ in (None, ""):
    sys.path.insert(
        0,
        str(Path(__file__).resolve().parent.parent)
    )

from jobapply.config import EXCEL_PATH, PLATFORMS
from jobapply.browser.selenium_manager import BrowserManager

from jobapply.collectors.job_collector import JobCollector
from jobapply.collectors.linkedin_collector import LinkedInCollector

from jobapply.spreadsheet.excel_manager import (
    APPLICATION_STATUSES,
    ExcelManager
)

from jobapply.resume.resume_manager import ResumeManager

from jobapply.applications.application_manager import (
    ApplicationAssistant
)

from jobapply.utils.logger import get_logger


logger = get_logger()

JOB_QUERIES = {
    "infra": [
        "Analista de TI Júnior",
        "Analista de Suporte Junior"
    ],
    "dev": [
        "Java Developer",
        "Fullstack developer",
        "Frontend Developer",
        "Mobile Developer"
    ]
}


def main():

    parser = argparse.ArgumentParser(
        description="JobApply Automation"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # Inicialização

    subparsers.add_parser(
        "init",
        help="Criar planilha Excel"
    )

    subparsers.add_parser(
        "list",
        help="Listar vagas cadastradas"
    )

    update_parser = subparsers.add_parser(
        "update",
        help="Atualizar o status de candidatura de uma vaga"
    )
    update_parser.add_argument(
        "--id",
        type=int,
        required=True
    )
    update_parser.add_argument(
        "--status",
        choices=APPLICATION_STATUSES,
        required=True
    )

    # Pesquisa

    search_parser = subparsers.add_parser(
        "search",
        help="Abrir pesquisas de vagas"
    )

    search_parser.add_argument(
        "--area",
        choices=["infra", "dev", "ambas"],
        default="ambas"
    )

    search_parser.add_argument(
        "--local",
        nargs="+",
        default=["Blumenau SC", "Gaspar SC"],
        metavar="CIDADE"
    )

    search_parser.add_argument(
        "--modalidade",
        choices=["Remoto", "Híbrido", "Presencial"],
        nargs="+",
        default=["Remoto", "Híbrido", "Presencial"],
        metavar="TIPO"
    )

    search_parser.add_argument(
        "--plataforma",
        choices=PLATFORMS.keys(),
        default="linkedin"
    )

    # Cadastro de vaga

    add_parser = subparsers.add_parser(
        "add",
        help="Cadastrar vaga"
    )

    add_parser.add_argument(
        "--empresa",
        required=True
    )

    add_parser.add_argument(
        "--cargo",
        required=True
    )

    add_parser.add_argument(
        "--url",
        required=True
    )

    add_parser.add_argument(
        "--modalidade",
        choices=[
            "Remoto",
            "Híbrido",
            "Presencial",
            "Não informado"
        ],
        default="Não informado"
    )

    add_parser.add_argument(
        "--localidade",
        default="Não informado"
    )

    add_parser.add_argument(
        "--plataforma",
        choices=[
            "LinkedIn",
            "Gupy",
            "Indeed",
            "Outra"
        ],
        default="Outra"
    )

    add_parser.add_argument(
        "--area",
        choices=["infra", "dev"],
        required=True
    )

    # Abrir candidatura

    open_parser = subparsers.add_parser(
        "open",
        help="Abrir vaga para candidatura assistida"
    )

    open_parser.add_argument(
        "--url",
        required=True
    )

    open_parser.add_argument(
        "--area",
        choices=["infra", "dev"],
    )

    open_parser.add_argument(
        "--empresa",
        required=True
    )

    open_parser.add_argument(
        "--cargo",
        required=True
    )

    args = parser.parse_args()

    excel = ExcelManager(
        EXCEL_PATH
    )

    # Inicialização

    if args.command == "init":

        excel.ensure_workbook()

        print(
            f"Planilha criada: {EXCEL_PATH}"
        )

    elif args.command == "list":
        jobs = excel.list_jobs()
        if not jobs:
            print("Nenhuma vaga cadastrada.")
            return

        print(
            f"{'ID':>4}  {'STATUS':<16} {'CARGO':<32} "
            f"{'EMPRESA':<24} {'LOCALIDADE':<28} LINK"
        )
        print("-" * 140)
        for job in jobs:
            print(
                f"{job['ID']:>4}  "
                f"{str(job['Status da candidatura'] or ''):<16} "
                f"{str(job['Cargo'] or '')[:32]:<32} "
                f"{str(job['Empresa'] or '')[:24]:<24} "
                f"{str(job['Localidade'] or '')[:28]:<28} "
                f"{job['Link da vaga'] or ''}"
            )

    elif args.command == "update":
        if not excel.update_application_status(
            args.id,
            args.status
        ):
            parser.error(
                f"Não existe vaga com ID {args.id}."
            )
        print(
            f"Status da vaga {args.id} atualizado para "
            f"'{args.status}'."
        )

    # Pesquisa de vagas

    elif args.command == "search":

        if args.area == "ambas":

            selected_queries = (
                JOB_QUERIES["dev"] +
                JOB_QUERIES["infra"]
            )

        else:

            selected_queries = JOB_QUERIES[
                args.area
            ]

        collected_jobs = []

        with BrowserManager() as browser:

            for platform, template in PLATFORMS.items():

                if platform != args.plataforma:
                    continue
                for query in selected_queries:

                    for location in args.local:

                        if platform == "linkedin":
                            url = LinkedInCollector.search_url(
                                query,
                                location,
                                args.modalidade
                            )
                        else:
                            url = (
                                template
                                if platform == "gupy"
                                else template.format(
                                    query=quote_plus(query),
                                    location=quote_plus(location)
                                )
                            )

                        try:
                            browser.driver.get(url)
                        except InvalidSessionIdException:
                            logger.warning(
                                "Sessão do navegador encerrada durante a pesquisa."
                            )
                            print(
                                "O navegador foi fechado ou desconectado. "
                                "A pesquisa foi interrompida."
                            )
                            return

                        if platform == "linkedin":
                            try:
                                WebDriverWait(
                                    browser.driver,
                                    10
                                ).until(
                                    lambda driver:
                                    driver.find_elements(
                                        "css selector",
                                        LinkedInCollector.CARD_SELECTOR
                                    )
                                )
                                search_results = (
                                    LinkedInCollector.collect(
                                        browser.driver,
                                        query,
                                        location
                                    )
                                )
                            except InvalidSessionIdException:
                                logger.warning(
                                    "Sessão do navegador encerrada "
                                    "durante a coleta do LinkedIn."
                                )
                                print(
                                    "O navegador foi fechado ou "
                                    "desconectado. A busca foi interrompida."
                                )
                                return
                            except TimeoutException:
                                logger.warning(
                                    "Nenhum anúncio carregado no LinkedIn "
                                    "para %s em %s.",
                                    query,
                                    location
                                )
                                print(
                                    f"Nenhum anúncio carregado: "
                                    f"{query} - {location}. "
                                    "O LinkedIn pode exigir login ou limitar "
                                    "a busca."
                                )
                                continue

                            collected_jobs.extend(search_results)
                            print(
                                f"Busca LinkedIn: {query} - {location}; "
                                f"{len(search_results)} anúncio(s) lido(s)."
                            )
                            continue

                        print(
                            f"Pesquisa: {platform} - {query} - {location}"
                        )

                        input(
                            "Analise a página. "
                            "Pressione ENTER para continuar..."
                        )

        if args.plataforma == "linkedin":
            unique_jobs = LinkedInCollector.unique_records(
                collected_jobs
            )
            saved_count = excel.add_jobs(unique_jobs)
            print(
                f"Busca concluída: {len(unique_jobs)} vaga(s) única(s) "
                f"encontrada(s), {saved_count} nova(s) registrada(s) "
                "na planilha."
            )

    # Cadastro de oportunidade

    elif args.command == "add":

        try:

            curriculum = ResumeManager.select(
                args.cargo,
                args.area
            )

            record = JobCollector.build_record(
                company=args.empresa,
                title=args.cargo,
                url=args.url,
                modality=args.modalidade,
                location=args.localidade,
                platform=args.plataforma
            )

            record["curriculum"] = str(
                curriculum
            )

            excel.add_job(record)

            logger.info(
                "Vaga cadastrada: %s",
                args.cargo
            )

            print(
                "Vaga cadastrada com sucesso!"
            )

        except Exception as error:

            logger.exception(
                "Erro ao cadastrar vaga"
            )

            print(
                f"Erro: {error}"
            )

    # Candidatura assistida

    elif args.command == "open":

        try:

            curriculum = ResumeManager.select(
                args.cargo,
                args.area
            )

            print(
                "Currículo selecionado:",
                curriculum
            )

            with BrowserManager() as browser:

                browser.driver.get(
                    args.url
                )

                assistant = ApplicationAssistant(
                    browser.driver
                )

                assistant.inspect_and_prepare(
                    curriculum
                )

                input(
                    "\nRevise a candidatura no navegador. "
                    "Faça o envio manual somente após conferir. "
                    "Pressione ENTER para registrar o progresso..."
                )

                record = JobCollector.build_record(
                    company=args.empresa,
                    title=args.cargo,
                    url=args.url
                )

                record["curriculum"] = str(
                    curriculum
                )

                record["application_status"] = (
                    "Em progresso"
                )

                excel.add_job(record)

                print(
                    "Vaga registrada na planilha."
                )

        except Exception as error:

            logger.exception(
                "Erro na candidatura assistida"
            )

            print(
                f"Erro: {error}"
            )


if __name__ == "__main__":

    main()
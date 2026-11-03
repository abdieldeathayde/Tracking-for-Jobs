import argparse

from urllib.parse import quote_plus

from config import EXCEL_PATH, PLATFORMS

from jobapply.browser.selenium_manager import BrowserManager

from jobapply.collectors.job_collector import JobCollector

from jobapply.spreadsheet.excel_manager import ExcelManager

from jobapply.resume.resume_manager import ResumeManager

from jobapply.applications.application_manager import (
    ApplicationAssistant
)

from jobapply.utils.logger import get_logger


logger = get_logger()


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
        default="Blumenau SC"
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
        required=True
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

    # Pesquisa de vagas

    elif args.command == "search":

        queries = {

            "infra": [
                "Suporte Técnico TI",
                "Infraestrutura de TI",
                "Service Desk"
            ],

            "dev": [
                "Desenvolvedor Java",
                "Java Spring Boot",
                "Desenvolvedor Angular"
            ]
        }

        if args.area == "ambas":

            selected_queries = (
                queries["infra"] +
                queries["dev"]
            )

        else:

            selected_queries = queries[
                args.area
            ]

        with BrowserManager() as browser:

            for platform, template in PLATFORMS.items():

                for query in selected_queries:

                    if platform == "gupy":

                        url = template

                    else:

                        url = template.format(
                            query=quote_plus(query),
                            location=quote_plus(args.local)
                        )

                    browser.driver.get(url)

                    print(
                        f"Pesquisa: {platform} - {query}"
                    )

                    input(
                        "Analise a página. "
                        "Pressione ENTER para continuar..."
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
import argparse
import random
import time
from urllib.parse import quote_plus

from selenium.common.exceptions import (
    InvalidSessionIdException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait

from jobapply.applications.application_manager import ApplicationAssistant
from jobapply.browser.selenium_manager import BrowserManager
from jobapply.collectors.job_collector import JobCollector
from jobapply.collectors.linkedin_collector import LinkedInCollector
from jobapply.config import (
    EXCEL_PATH,
    PLATFORMS,
    REQUEST_DELAY_MAX,
    REQUEST_DELAY_MIN,
    WAIT_SECONDS,
)
from jobapply.resume.resume_manager import ResumeManager
from jobapply.spreadsheet.excel_manager import (
    APPLICATION_STATUSES,
    ExcelManager,
)
from jobapply.utils.logger import get_logger
from jobapply.utils.urls import detect_platform, validate_http_url


logger = get_logger()

JOB_QUERIES = {
    "infra": [
        "Analista de TI Júnior",
        "Analista de Suporte Junior",
    ],
    "dev": [
        "Java Developer",
        "Fullstack developer",
        "Frontend Developer",
        "Mobile Developer",
    ],
}


def main():
    parser = argparse.ArgumentParser(description="JobApply Automation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Criar planilha Excel")

    list_parser = subparsers.add_parser("list", help="Listar vagas cadastradas")
    list_parser.add_argument(
        "--status",
        choices=APPLICATION_STATUSES,
        help="Mostrar apenas vagas com este status",
    )

    subparsers.add_parser(
        "summary",
        help="Exibir um resumo das candidaturas por status",
    )

    update_parser = subparsers.add_parser(
        "update",
        help="Atualizar o status de candidatura de uma vaga",
    )
    update_parser.add_argument("--id", type=int, required=True)
    update_parser.add_argument(
        "--status",
        choices=APPLICATION_STATUSES,
        required=True,
    )

    search_parser = subparsers.add_parser(
        "search",
        help="Abrir pesquisas de vagas",
    )
    search_parser.add_argument(
        "--area",
        choices=["infra", "dev", "ambas"],
        default="ambas",
    )
    search_parser.add_argument(
        "--local",
        nargs="+",
        default=["Blumenau SC", "Gaspar SC"],
        metavar="CIDADE",
    )
    search_parser.add_argument(
        "--modalidade",
        choices=["Remoto", "Híbrido", "Presencial"],
        nargs="+",
        default=["Remoto", "Híbrido", "Presencial"],
        metavar="TIPO",
    )
    search_parser.add_argument(
        "--plataforma",
        choices=PLATFORMS.keys(),
        default="linkedin",
    )
    search_parser.add_argument(
        "--easy-apply",
        action="store_true",
        help="Filtrar apenas vagas com Candidatura Simplificada no LinkedIn",
    )

    add_parser = subparsers.add_parser("add", help="Cadastrar vaga")
    add_parser.add_argument("--empresa", required=True)
    add_parser.add_argument("--cargo", required=True)
    add_parser.add_argument("--url", required=True)
    add_parser.add_argument(
        "--modalidade",
        choices=["Remoto", "Híbrido", "Presencial", "Não informado"],
        default="Não informado",
    )
    add_parser.add_argument("--localidade", default="Não informado")
    add_parser.add_argument(
        "--plataforma",
        choices=["LinkedIn", "Gupy", "Indeed", "Outra"],
        default="Outra",
    )
    add_parser.add_argument("--area", choices=["infra", "dev"], required=True)

    open_parser = subparsers.add_parser(
        "open",
        help="Abrir vaga para candidatura assistida",
    )
    open_parser.add_argument("--url", required=True)
    open_parser.add_argument("--area", choices=["infra", "dev"])
    open_parser.add_argument("--empresa", required=True)
    open_parser.add_argument("--cargo", required=True)

    args = parser.parse_args()
    excel = ExcelManager(EXCEL_PATH)

    if args.command == "init":
        excel.ensure_workbook()
        print(f"Planilha criada: {EXCEL_PATH}")

    elif args.command == "list":
        jobs = excel.list_jobs(status=args.status)
        if not jobs:
            if args.status:
                print(
                    "Nenhuma vaga cadastrada com o status "
                    f"'{args.status}'."
                )
            else:
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

    elif args.command == "summary":
        summary = excel.get_summary()
        print(f"Total de vagas: {summary['total']}")
        for status, count in summary["by_status"].items():
            print(f"{status:<20} {count:>4}")

    elif args.command == "update":
        if not excel.update_application_status(args.id, args.status):
            parser.error(f"Não existe vaga com ID {args.id}.")
        print(
            f"Status da vaga {args.id} atualizado para "
            f"'{args.status}'."
        )

    elif args.command == "search":
        if args.area == "ambas":
            selected_queries = JOB_QUERIES["dev"] + JOB_QUERIES["infra"]
        else:
            selected_queries = JOB_QUERIES[args.area]

        collected_jobs = []
        search_pairs = [
            (query, location)
            for query in selected_queries
            for location in args.local
        ]

        with BrowserManager() as browser:
            template = PLATFORMS[args.plataforma]
            for index, (query, location) in enumerate(search_pairs):
                if args.plataforma == "linkedin":
                    url = LinkedInCollector.search_url(
                        query,
                        location,
                        args.modalidade,
                        easy_apply=args.easy_apply,
                    )
                else:
                    url = (
                        template
                        if args.plataforma == "gupy"
                        else template.format(
                            query=quote_plus(query),
                            location=quote_plus(location),
                        )
                    )

                try:
                    browser.driver.get(url)
                except InvalidSessionIdException:
                    logger.warning("Sessão do navegador encerrada durante a pesquisa.")
                    print(
                        "O navegador foi fechado ou desconectado. "
                        "A pesquisa foi interrompida."
                    )
                    return

                if args.plataforma == "linkedin":
                    if LinkedInCollector.is_authwall(browser.driver):
                        logger.warning("LinkedIn solicitou login/authwall durante a busca.")
                        print(
                            "O LinkedIn solicitou login (authwall). "
                            "Interrompendo busca para proteger sua conta."
                        )
                        break

                    try:
                        WebDriverWait(browser.driver, WAIT_SECONDS).until(
                            lambda driver: driver.find_elements(
                                "css selector",
                                LinkedInCollector.CARD_SELECTOR,
                            )
                        )
                        search_results = LinkedInCollector.collect(
                            browser.driver,
                            query,
                            location,
                        )
                    except InvalidSessionIdException:
                        logger.warning(
                            "Sessão do navegador encerrada durante a coleta do LinkedIn."
                        )
                        print(
                            "O navegador foi fechado ou desconectado. "
                            "A busca foi interrompida."
                        )
                        return
                    except TimeoutException:
                        logger.warning(
                            "Nenhum anúncio carregado no LinkedIn para %s em %s.",
                            query,
                            location,
                        )
                        print(
                            f"Nenhum anúncio carregado: {query} - {location}. "
                            "O LinkedIn pode exigir login ou limitar a busca."
                        )
                        continue

                    collected_jobs.extend(search_results)
                    print(
                        f"Busca LinkedIn: {query} - {location}; "
                        f"{len(search_results)} anúncio(s) lido(s)."
                    )

                    if index < len(search_pairs) - 1 and REQUEST_DELAY_MAX > 0:
                        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
                    continue

                print(f"Pesquisa: {args.plataforma} - {query} - {location}")
                input("Analise a página. Pressione ENTER para continuar...")

        if args.plataforma == "linkedin":
            unique_jobs = LinkedInCollector.unique_records(collected_jobs)
            saved_count = excel.add_jobs(unique_jobs)
            print(
                f"Busca concluída: {len(unique_jobs)} vaga(s) única(s) "
                f"encontrada(s), {saved_count} nova(s) registrada(s) "
                "na planilha."
            )

    elif args.command == "add":
        try:
            curriculum = ResumeManager.select(args.cargo, args.area)
            record = JobCollector.build_record(
                company=args.empresa,
                title=args.cargo,
                url=args.url,
                modality=args.modalidade,
                location=args.localidade,
                platform=args.plataforma,
            )
            record["curriculum"] = str(curriculum)

            if excel.add_job(record):
                logger.info("Vaga cadastrada: %s", args.cargo)
                print("Vaga cadastrada com sucesso!")
            else:
                print("Essa vaga já está cadastrada pelo mesmo link.")
        except Exception as error:
            logger.exception("Erro ao cadastrar vaga")
            print(f"Erro: {error}")

    elif args.command == "open":
        try:
            safe_url = validate_http_url(args.url)
            curriculum = ResumeManager.select(args.cargo, args.area)
            print("Currículo selecionado:", curriculum)

            with BrowserManager() as browser:
                browser.driver.get(safe_url)
                assistant = ApplicationAssistant(browser.driver)
                assistant.inspect_and_prepare(curriculum)

                input(
                    "\nRevise a candidatura no navegador. "
                    "Faça o envio manual somente após conferir. "
                    "Pressione ENTER para registrar o progresso..."
                )

                record = JobCollector.build_record(
                    company=args.empresa,
                    title=args.cargo,
                    url=safe_url,
                    platform=detect_platform(safe_url),
                )
                record["curriculum"] = str(curriculum)
                record["application_status"] = "Em progresso"

                outcome = excel.register_assisted_application(record)
                if outcome == "added":
                    print("Vaga registrada na planilha.")
                elif outcome == "updated":
                    print("Vaga atualizada para 'Em progresso' na planilha.")
                else:
                    print("Essa vaga já estava registrada na planilha.")
        except Exception as error:
            logger.exception("Erro na candidatura assistida")
            print(f"Erro: {error}")


if __name__ == "__main__":
    main()
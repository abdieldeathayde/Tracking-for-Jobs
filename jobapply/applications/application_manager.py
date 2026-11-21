from pathlib import Path

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from jobapply.config import WAIT_SECONDS
from jobapply.utils.logger import get_logger

logger = get_logger()


class ApplicationAssistant:

    EASY_APPLY_SELECTORS = (
        ".jobs-apply-button",
        "button[aria-label*='Candidatura simplificada']",
        "button[aria-label*='Easy Apply']",
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, WAIT_SECONDS)

    def _open_easy_apply_modal_if_present(self) -> bool:
        for selector in self.EASY_APPLY_SELECTORS:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for button in buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        self.wait.until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "[role='dialog']")
                            )
                        )
                        logger.info("Modal de candidatura simplificada aberto.")
                        return True
                except (TimeoutException, WebDriverException) as error:
                    logger.warning(
                        "Não foi possível abrir o modal de candidatura: %s",
                        error,
                    )
        return False

    def inspect_and_prepare(self, curriculum_path, try_easy_apply=True):
        self.wait.until(
            lambda driver: driver.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        print("Página:", self.driver.title)
        print("URL:", self.driver.current_url)

        curriculum_path = Path(curriculum_path).resolve()
        if not curriculum_path.is_file() or curriculum_path.suffix.lower() != ".pdf":
            logger.warning("Currículo inválido ou inexistente: %s", curriculum_path)
            print("Currículo inválido ou não encontrado.")
            return {"attached": False, "easy_apply_opened": False}

        easy_apply_opened = False
        if try_easy_apply:
            easy_apply_opened = self._open_easy_apply_modal_if_present()

        upload_fields = self.driver.find_elements(
            By.CSS_SELECTOR,
            "input[type='file']",
        )

        attached = False
        if upload_fields:
            try:
                upload_fields[0].send_keys(str(curriculum_path))
                attached = True
                logger.info("Currículo anexado na página.")
                print("Currículo anexado com sucesso.")
            except Exception as error:
                logger.warning("Erro ao anexar currículo: %s", error)
                print("Erro ao anexar currículo:", error)
        else:
            print("Campo de currículo não encontrado.")
            print("Faça o anexo manualmente.")

        print("Revise os campos da candidatura.")
        print("O envio depende da sua aprovação.")

        return {
            "attached": attached,
            "easy_apply_opened": easy_apply_opened,
        }
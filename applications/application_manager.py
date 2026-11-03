from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from jobapply.config import WAIT_SECONDS

class ApplicationAssistant:

    def __init__(self, driver):

        self.driver = driver

        self.wait = WebDriverWait(
            driver,
            WAIT_SECONDS
        )

    def inspect_and_prepare(self, curriculum_path):

        self.wait.until(
            lambda driver:
            driver.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        print("Página:", self.driver.title)

        print("URL:", self.driver.current_url)

        curriculum_path = Path(
            curriculum_path
        ).resolve()

        upload_fields = self.driver.find_elements(
            "css selector",
            "input[type='file']"
        )

        if upload_fields and curriculum_path.exists():

            try:

                upload_fields[0].send_keys(
                    str(curriculum_path)
                )

                print(
                    "Currículo anexado com sucesso."
                )

            except Exception as error:

                print(
                    "Erro ao anexar currículo:",
                    error
                )

        else:

            print(
                "Campo de currículo não encontrado."
            )

            print(
                "Faça o anexo manualmente."
            )

        print(
            "Revise os campos da candidatura."
        )

        print(
            "O envio depende da sua aprovação."
        )
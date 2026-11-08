from selenium import webdriver
from selenium.common.exceptions import InvalidSessionIdException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from jobapply.config import BROWSER, HEADLESS

class BrowserManager:
    def __init__(self):
        self.driver = None

    def __enter__(self):

        if BROWSER == "firefox":
         
            options = FirefoxOptions()

            if HEADLESS:
                options.add_argument("-headless")

            self.driver = webdriver.Firefox(
                options=options
            )

        elif BROWSER == "edge":

            options = EdgeOptions()

            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")

            if HEADLESS:
                options.add_argument("--headless=new")

            self.driver = webdriver.Edge(
                options=options
            )

        else:

            options = ChromeOptions()

            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")

            if HEADLESS:
                options.add_argument("--headless=new")

            self.driver = webdriver.Chrome(
                options=options
            )

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        if self.driver:
            try:
                self.driver.quit()
            except InvalidSessionIdException:
                pass

            
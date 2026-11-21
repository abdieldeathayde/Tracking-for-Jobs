from selenium import webdriver
from selenium.common.exceptions import InvalidSessionIdException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from jobapply.config import BROWSER, BROWSER_PROFILE_DIR, HEADLESS


class BrowserManager:
    def __init__(self):
        self.driver = None

    def __enter__(self):
        if BROWSER == "firefox":
            options = FirefoxOptions()
            if HEADLESS:
                options.add_argument("-headless")
            if BROWSER_PROFILE_DIR:
                options.add_argument("-profile")
                options.add_argument(str(BROWSER_PROFILE_DIR))
            self.driver = webdriver.Firefox(options=options)

        elif BROWSER == "edge":
            options = EdgeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            if HEADLESS:
                options.add_argument("--headless=new")
            if BROWSER_PROFILE_DIR:
                options.add_argument(f"--user-data-dir={BROWSER_PROFILE_DIR}")
            self.driver = webdriver.Edge(options=options)

        else:
            options = ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            if HEADLESS:
                options.add_argument("--headless=new")
            if BROWSER_PROFILE_DIR:
                options.add_argument(f"--user-data-dir={BROWSER_PROFILE_DIR}")
            self.driver = webdriver.Chrome(options=options)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            try:
                self.driver.quit()
            except InvalidSessionIdException:
                pass
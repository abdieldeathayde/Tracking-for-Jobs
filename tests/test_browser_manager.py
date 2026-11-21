from unittest.mock import MagicMock
from selenium.common.exceptions import InvalidSessionIdException

from jobapply.browser import selenium_manager
from jobapply.browser.selenium_manager import BrowserManager


def test_browser_manager_uses_edge_headless_and_quits(monkeypatch):
    mock_driver = MagicMock()
    mock_edge = MagicMock(return_value=mock_driver)

    monkeypatch.setattr(selenium_manager, "BROWSER", "edge")
    monkeypatch.setattr(selenium_manager, "HEADLESS", True)
    monkeypatch.setattr(selenium_manager.webdriver, "Edge", mock_edge)

    with BrowserManager() as browser:
        assert browser.driver is mock_driver

    options = mock_edge.call_args.kwargs["options"]
    assert "--headless=new" in options.arguments
    mock_driver.quit.assert_called_once()


def test_browser_manager_ignores_invalid_session_on_exit(monkeypatch):
    mock_driver = MagicMock()
    mock_driver.quit.side_effect = InvalidSessionIdException("closed")

    monkeypatch.setattr(selenium_manager, "BROWSER", "chrome")
    monkeypatch.setattr(selenium_manager, "HEADLESS", False)
    monkeypatch.setattr(
        selenium_manager.webdriver,
        "Chrome",
        MagicMock(return_value=mock_driver),
    )

    with BrowserManager():
        pass

    mock_driver.quit.assert_called_once()
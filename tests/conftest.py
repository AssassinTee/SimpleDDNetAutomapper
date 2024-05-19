import sys

import pytest
from PyQt5.QtWidgets import QApplication

app = None


@pytest.fixture(scope="session")
def init_q_app():
    """
    some Qt components need an application
    """
    global app
    if app is None:
        app = QApplication(sys.argv)
    yield

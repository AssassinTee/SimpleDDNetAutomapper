import sys

import pytest

from PyQt6.QtWidgets import QApplication

app = None


@pytest.fixture(scope="session")
def q_app():
    global app
    if app is None:
        app = QApplication(sys.argv)
    yield

"""
Class that handles the application state, sometimes you need to grab information from different points in the
application
"""
from typing import Optional

from PyQt6.QtGui import QPixmap

from src.backend.rule_manager import RuleManager


class AppState:
    _instance = None

    def __init__(self):
        raise RuntimeError("singleton, use instance() instead")

    def _init(self):
        self.rule_manager: RuleManager = RuleManager()
        self.main_image_path: Optional[str] = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init()
        return cls._instance

    @classmethod
    def imagePath(cls):
        return cls.instance().main_image_path

    @classmethod
    def ruleManager(cls):
        return cls.instance().rule_manager

    @classmethod
    def setImagePath(cls, image_path):
        cls.instance().main_image_path = image_path

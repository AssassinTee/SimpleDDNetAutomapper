"""
Class that handles the application state, sometimes you need to grab information from different points in the
application
"""
from typing import Optional

from PyQt6.QtGui import QPixmap

from src.backend.rule_manager import RuleManager
from src.signals.signal_emitter import ApplicationStatusEmitter, ApplicationStatusEnum
from pathlib import Path


class AppState:
    _instance = None

    def __init__(self):
        raise RuntimeError("singleton, use instance() instead")

    def _init(self):
        self.rule_manager: RuleManager = RuleManager()
        self.main_image_path: Optional[str] = None
        self.signal_emitter = ApplicationStatusEmitter()

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
        cls.instance().rule_manager.loadRules(Path(image_path).stem)
        cls.instance().signal_emitter.application_status_signal.emit(
            ApplicationStatusEnum.IMAGE_LOADED,
            f"image loaded: {str(image_path)}")

    @classmethod
    def reset(cls):
        # do not call _init here, don't overwrite the signal emitter, reset manually
        cls.instance().rule_manager: RuleManager = RuleManager()
        cls.instance().main_image_path: Optional[str] = None
        cls.instance().signal_emitter.application_status_signal.emit(
            ApplicationStatusEnum.RESET_APP,
            "Reset rules and images")

    @classmethod
    def setStatus(cls, status_type: ApplicationStatusEnum, message: str):
        if status_type == ApplicationStatusEnum.IMAGE_LOADED:
            raise ValueError(f"Application status {status_type} is not allowed for messaging")
        cls.instance().signal_emitter.application_status_signal.emit(status_type, message)

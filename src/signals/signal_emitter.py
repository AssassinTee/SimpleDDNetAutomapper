from PyQt6.QtCore import pyqtSignal, QObject
from enum import Enum


class ConfigurationClickedEmitter(QObject):
    neighbor_signal = pyqtSignal(int, name="NeighborClick")
    modification_signal = pyqtSignal(int, bool, name="ModificationSignal")


class ApplicationStatusEnum(Enum):
    IMAGE_LOADED = "ImageLoaded"
    WARNING = "Warning"
    INFO = "Info"


class ApplicationStatusEmitter(QObject):
    application_status_signal = pyqtSignal(ApplicationStatusEnum, str, name="ApplicationStatus")

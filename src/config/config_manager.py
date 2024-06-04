from pathlib import Path
from typing import Any

import yaml

from src.config.storage_finder import StorageFinder


class ConfigManager:
    _instance = None
    config_path = Path("config.yml")
    _config: Any = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    def _init(self):
        self._config: Any = None
        if not Path(self.config_path).is_file():
            self.createConfig()
            self.writeConfig()
        if not Path(self.config_path).is_file():
            raise RuntimeError('Could not create config.yml')
        self._config = yaml.safe_load(open(self.config_path))

    def createConfig(self):
        client_path = StorageFinder.instance().getClientPath()
        data_path = StorageFinder.instance().getDataPath()
        data = {
            'version': "1.0.0",
            'client_path': str(client_path),
            'data_path': str(data_path),
        }
        self._config = data

    def writeConfig(self):
        with open(self.config_path, 'w') as file:
            yaml.safe_dump(self._config, file, default_flow_style=False)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init()
        return cls._instance

    @classmethod
    def config(cls):
        return cls.instance()._config

    @classmethod
    def setConfig(cls, setting, value):
        if setting not in cls.instance()._config.keys():
            raise ValueError(f"Unknown setting '{setting}'")
        cls.instance()._config[setting] = value
        cls.instance().writeConfig()

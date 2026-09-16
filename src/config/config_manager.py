import logging
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

from src.config.storage_finder import StorageFinder


class Config(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    version: str = "1.0.0"
    client_path: Path | None = None
    data_path: Path | None = None


class ConfigManager:
    _instance = None
    config_path = Path("config.yml")
    _config: Config | None = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    def _init(self):
        self._config = None
        if not self.config_path.is_file():
            self.createConfig()
            self.writeConfig()
        if not self.config_path.is_file():
            raise RuntimeError('Could not create config.yml')
        data = yaml.safe_load(self.config_path.read_text()) or {}
        self._config = Config.model_validate(data)
        self._checkConfig()

    def _checkConfig(self) -> bool:
        updated = False
        if self._config.data_path and not self._config.data_path.is_dir():
            self._config.data_path = None
            updated = True
        if self._config.client_path and not self._config.client_path.is_file():
            self._config.client_path = None
            updated = True

        if updated:
            self.writeConfig()
        return updated

    def createConfig(self):
        client_path = None
        data_path = None
        # noinspection PyBroadException
        try:
            client_path = StorageFinder.instance().getClientPath()
            data_path = StorageFinder.instance().getDataPath()
        except Exception as e:
            logging.error("An error occured while creating the config")
            logging.error(str(e))

        self._config = Config(client_path=client_path, data_path=data_path)

    def writeConfig(self):
        self.config_path.write_text(
            yaml.safe_dump(self._config.model_dump(mode="json"), default_flow_style=False)
        )

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init()
        return cls._instance

    @classmethod
    def config(cls) -> Config:
        return cls.instance()._config

    @classmethod
    def setConfig(cls, setting, value):
        instance = cls.instance()
        if setting not in Config.model_fields:
            raise ValueError(f"Unknown setting '{setting}'")
        setattr(instance._config, setting, value)
        if not instance._checkConfig():
            instance.writeConfig()  # make sure the config gets written

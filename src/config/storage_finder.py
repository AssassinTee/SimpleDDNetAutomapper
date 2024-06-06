import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


class StorageFinderBase(ABC):
    _instance = None

    @abstractmethod
    def findData(self):
        pass

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @abstractmethod
    def _init(self):
        pass

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init()
        return cls._instance

    @abstractmethod
    def getClientPath(self):
        pass

    @abstractmethod
    def getDataPath(self):
        pass


class StorageFinder(StorageFinderBase):
    def _init(self):
        self.client_path = None
        self.data_path = None
        self.findData()

    def findData(self):
        linux_paths: List[str] = [
            "/usr/share/ddnet/data",
            "/usr/share/games/ddnet/data",
            "/usr/local/share/ddnet/data",
            "/usr/local/share/games/ddnet/data",
            "/usr/pkg/share/ddnet/data",
            "/usr/pkg/share/games/ddnet/data",
            "/opt/ddnet/data",
            os.path.expanduser('~/.steam/steam/steamapps/common/DDraceNetwork/ddnet/data'),
            os.path.expanduser('~/.local/share/Steam/steamapps/common/DDraceNetwork/ddnet/data'),
            "/usr/share/teeworlds/data",
            "/usr/share/games/teeworlds/data",
            "/usr/local/share/teeworlds/data",
            "/usr/local/share/games/teeworlds/data",
            "/usr/pkg/share/teeworlds/data",
            "/usr/pkg/share/games/teeworlds/data",
            "/opt/teeworlds/data",
            os.path.expanduser('~/.steam/steam/steamapps/common/DDraceNetwork/ddnet/data'),
            os.path.expanduser('~/.local/share/Steam/steamapps/common/Teeworlds/tw/data'),
        ]
        match sys.platform:
            case 'linux':
                self._findLocations(linux_paths, sys.platform)
            case 'win32' | 'cygwin':
                paths = [
                    os.path.expandvars(r'%APPDATA%\DDNet'),
                    os.path.expandvars(r'%PROGRAMFILES(x86)%\Steam\steamapps\common\DDraceNetwork\ddnet\data'),
                    os.path.expandvars(r'%APPDATA%\Teeworlds'),
                    os.path.expandvars(r'%PROGRAMFILES(x86)%\Steam\steamapps\common\Teeworlds\tw\data'),
                ]
                self._findLocations(paths, sys.platform)
            case _:
                logger.warning("Trying to detect client and data path on unknown OS")
                self._findLocations(linux_paths, sys.platform)
        if not self.data_path:
            logger.warning("Failed to detect ddnet 'data' directory, please set it manually in the settings")
        if not self.client_path:
            logger.warning("Failed to detect ddnet 'client_path' directory, please set it manually in the settings")

    def getClientPath(self):
        if self.client_path:
            return Path(self.client_path)
        else:
            self._findClient(self.data_path, sys.platform)
            if self.client_path:  # don't recurse here
                return Path(self.client_path)
        return None

    def getDataPath(self):
        if self.data_path:
            try:
                p = Path(self.data_path)
                if p.is_dir():
                    return p
            except OSError:
                pass
        return None

    def _findLocations(self, paths: List[str], os_name):
        for path in paths:
            data_path = Path(path)
            if data_path.exists() and data_path.is_dir():
                if self.data_path is None:
                    self.data_path = data_path
                # client may be found in another data directory location
                client_path = StorageFinder._findClient(data_path, os_name)
                if client_path:
                    self.client_path = client_path
                    break

        return

    @staticmethod
    def _findClient(data_path, os_name):
        if data_path:
            pattern = "ddnet.exe" if os_name in ["win32", "cygwin"] else "ddnet*"
            for p in Path(data_path).parent.glob(pattern, case_sensitive=False):
                if p.is_file():
                    return p
        return None

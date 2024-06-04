import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


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
    client_path = None
    data_path = None

    def _init(self):
        self.findData()

    def findData(self):
        match sys.platform:
            case 'linux':
                paths: List[str] = [
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
                for data_path in paths:
                    if Path(data_path).exists() and Path(data_path).is_dir():
                        self.data_path = data_path
                        break
                return
            case 'win32':
                self._findWindows()
                return
            case 'cygwin:':
                self._findWindows()
                return
            case 'darwin':
                raise RuntimeError("MacOS is currently not supported")

    def _findWindows(self):
        paths = [
            os.path.expandvars(r'%APPDATA%\DDNet'),
            os.path.expandvars(r'%PROGRAMFILES(x86)%\Steam\steamapps\common\DDraceNetwork\ddnet\data'),
            os.path.expandvars(r'%APPDATA%\Teeworlds'),
            os.path.expandvars(r'%PROGRAMFILES(x86)%\Steam\steamapps\common\Teeworlds\tw\data'),
        ]
        for data_path in paths:
            if Path(data_path).exists() and Path(data_path).is_dir():
                self.data_path = data_path
                break
        return

    def getClientPath(self):
        if self.data_path:
            try:
                for p in Path(self.data_path).parent.glob('ddnet*'):
                    if p.is_file():
                        return p
            except OSError:
                pass
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

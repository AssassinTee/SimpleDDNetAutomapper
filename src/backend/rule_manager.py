from pathlib import Path
from typing import List, Dict, Optional

from src.backend import rpp_writer
from src.backend.group_handler import GroupHandler
from src.backend.rules_writer import createRuleLines
from src.backend.tile_handler import TileHandler
from src.config.config_manager import ConfigManager
from src.logger import BroadErrorHandler
import logging
logger = logging.getLogger(__name__)
RuleConfig = Dict[str, List[str]]


class RuleManager:

    def __init__(self):
        self._config: Dict[str, List[str]] = {}
        self._header: List[str] = []
        self._loadedRules = False

    def _loadRuleFile(self, filename_base):
        if not self._loadedRules:
            filename = f"{filename_base}.rules"
            data_path = ConfigManager.config().data_path
            if not data_path:
                logger.warning("No data directory configured, skipping rule load")
                self._config = {}
                self._header = []
                self._loadedRules = True
                return
            full_file_path = RuleManager._automapPath().joinpath(Path(filename))

            # load file if it exists
            if full_file_path.is_file():
                self._readRuleFile(full_file_path)

            # file doesn't exist, just to be explicit
            else:
                self._config = {}
                self._header = []
            self._loadedRules = True

    @BroadErrorHandler(logger)
    def loadRules(self, filename):
        if not self._loadedRules:
            filename = RuleManager._getFileBase(filename)
            try:
                self._loadRuleFile(filename)
            except ValueError:
                return False
            return True

    @BroadErrorHandler(logger)
    def saveRule(self, filename, rule_name):
        filename = RuleManager._getFileBase(filename)
        if not self._loadedRules:
            self._loadRuleFile(filename)
        self._config[rule_name] = []  # overwrite rules
        self._config[rule_name] = RuleManager._createRulesFromTileHandler()
        self._writeRuleFile(filename)

    def getRules(self) -> List[str]:
        if not self._loadedRules:
            return []
        return list(self._config.keys())

    @staticmethod
    def _getFileBase(filename: str):
        # remove .rules mime type
        if filename.startswith("."):
            raise ValueError("rules are not allowed to start with .")
        splits = filename.split(".")
        if len(splits) >= 2 and splits[-1] == "rules":
            filename = ".".join(splits[0:-1])
        return filename

    @staticmethod
    def _createRulesFromTileHandler():
        return createRuleLines(TileHandler.instance().neighborhood_map)

    @staticmethod
    def _automapPath() -> Path:
        data_path = ConfigManager.config().data_path
        if not data_path:
            raise ValueError("No editor directory path known, cannot save rules")
        automap_path = data_path.joinpath(Path("editor/automap"))
        automap_path.mkdir(parents=True, exist_ok=True)
        return automap_path

    @staticmethod
    def rppSource(rule_name: str, image_stem: str) -> str:
        return rpp_writer.dumps(TileHandler.instance().getAllTileData(), rule_name, image_stem,
                                GroupHandler.instance().getGroups())

    @BroadErrorHandler(logger)
    def saveRppSource(self, filename, rule_name):
        # dropped next to the .rules file, compiling it is still manual and needs rpp's base.r beside it
        stem = RuleManager._getFileBase(filename)
        full_path = RuleManager._automapPath().joinpath(Path(f"{stem}.r"))
        full_path.write_text(RuleManager.rppSource(rule_name, stem))
        logger.debug(f"Wrote rpp source to {full_path}")

    def _writeRuleFile(self, filename_base: str):
        if len(filename_base) == 0 or filename_base[0] == '/' or filename_base[0] == '\\':
            raise ValueError(f"the filename '{filename_base}' is invalid")

        # handle file location
        filename = f"{filename_base}.rules"
        full_path = RuleManager._automapPath().joinpath(Path(filename))

        # write file
        with open(str(full_path), 'w') as f:
            # write header, may be a comment
            if len(self._header):
                for line in self._header:
                    f.write(line)
                    f.write('\n')

            # write rules
            for key in self._config.keys():
                f.write(f"[{key}]\n")
                lines = self._config[key]
                for line in lines:
                    f.write(line)
                    f.write('\n')

    def _readRuleFile(self, full_file_path: Path):
        self._config = {}

        with open(str(full_file_path), 'r', encoding='utf-8') as f:
            section: Optional[str] = None

            # read file line by line
            while line := f.readline():
                line = line.rstrip()

                # handle sections
                if len(line) >= 2 and line[0] == '[' and line[-1] == ']':
                    section = line[1:-1]
                    self._config[section] = []

                # handle normal lines
                else:
                    if section:
                        self._config[section].append(line)
                    # https://github.com/ddnet/ddnet/blob/c7dc7b6a94528040678b7a0fab17ccb447e1d94d/src/game/editor/auto_map.cpp#L72C2-L72C146
                    elif len(line) > 0 and line[0] != '#' and line[0] != '\n' and line[0] != '\r' and line[0] != '\t' \
                            and line[0] != '\v' and line[0] != ' ':
                        raise ValueError("files may contain rules without section, aborting")
                    else:
                        # starting with a comment or something ignored, read header
                        self._header.append(line)

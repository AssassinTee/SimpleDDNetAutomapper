from pathlib import Path
from typing import List, Dict, Optional

from src.backend.tile_handler import TileHandler
from src.backend.tile_status import TileStatus
from src.config.config_manager import ConfigManager
from src.widgets.widget_base_tile import BaseTile
from src.logger import BroadErrorHandler

RuleConfig = Dict[str, List[str]]


class RuleManager:

    def __init__(self):
        self._config: Dict[str, List[str]] = {}
        self._header: List[str] = []
        self._loadedRules = False

    def _loadRuleFile(self, filename_base):
        if not self._loadedRules:
            filename = f"{filename_base}.rules"
            data_path = Path(ConfigManager.config()["data_path"])
            if not data_path:
                raise ValueError("No editor directory path known")

            automapper_path = data_path.joinpath(Path("editor/automap"))
            if not automapper_path.exists():
                automapper_path.mkdir()

            full_file_path = automapper_path.joinpath(Path(filename))

            # load file if it exists
            if full_file_path.is_file():
                self._readRuleFile(full_file_path)

            # file doesn't exist, just to be explicit
            else:
                self._config = {}
                self._header = []
            self._loadedRules = True

    @BroadErrorHandler
    def loadRules(self, filename):
        if not self._loadedRules:
            filename = RuleManager._getFileBase(filename)
            self._loadRuleFile(filename)

    @BroadErrorHandler
    def saveRule(self, filename, rule_name):
        filename = RuleManager._getFileBase(filename)
        if not self._loadedRules:
            self._loadRuleFile(filename)
        self._config[rule_name] = []  # overwrite rules
        self._config[rule_name] = RuleManager._createRulesFromTileHandler()
        self._writeRuleFile(filename)

    def getRules(self) -> List[str]:
        if not self._loadedRules:
            raise ValueError("Rules are not loaded yet")
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
        rule_pos_map = {
            0: "1 1",
            1: "0 1",
            2: "-1 1",
            3: "1 0",
            4: "-1 0",
            5: "1 -1",
            6: "0 -1",
            7: "-1 -1",
        }

        rule_list = []
        for i in range(2 ** 8):
            base_tiles: List[BaseTile] = TileHandler.instance().findTilesByNeighborhood(i)
            if len(base_tiles) > 0:
                # use first one, TODO: randomize?
                tile_id, tile_status = base_tiles[0]
                index_rule = RuleManager._createIndexRule(tile_id, tile_status)
                placing_rules = []
                for j in range(8):
                    full_neighbor = ((i >> j) & 1) > 0
                    str_full = "FULL" if full_neighbor else "EMPTY"
                    rule = f"Pos {rule_pos_map[j]} {str_full}"
                    placing_rules.append(rule)
                rule_list.extend([index_rule, *placing_rules])
        return rule_list

    @staticmethod
    def _createIndexRule(tile_id: int, tile_status: TileStatus):
        str_index = f"Index {tile_id}"
        str_x_flip = " XFLIP" if tile_status.v_flip else ""
        str_y_flip = " YFLIP" if tile_status.h_flip else ""
        str_rotate = " ROTATE" if tile_status.rot else ""
        return f"{str_index}{str_x_flip}{str_y_flip}{str_rotate}"

    def _writeRuleFile(self, filename_base: str):
        if len(filename_base) == 0 or filename_base[0] == '/' or filename_base[0] == '\\':
            raise ValueError(f"the filename '{filename_base}' is invalid")

        # handle file location
        filename = f"{filename_base}.rules"
        data_path = ConfigManager.config()["data_path"]
        if not data_path:
            full_path = filename  # save at root directory
        else:
            automap_path = Path(data_path).joinpath(Path("editor/automap"))
            if not automap_path.exists():
                automap_path.mkdir()
            full_path = automap_path.joinpath(filename)

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

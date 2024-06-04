from typing import List, Dict

from src.backend.tile_connection import TileConnection
from src.backend.tile_handler import TileHandler
from src.backend.tile_status import TileStatus
from src.globals import NUM_TILES
from src.widgets.widget_base_tile import BaseTile

RuleConfig = Dict[str, List[str]]


class RuleManager:
    _instance = None

    def __init__(self):
        raise RuntimeError('This is a static class')

    @staticmethod
    def _loadRuleFile(filename_base) -> RuleConfig:
        filename = f"{filename_base}.rules"
        # TODO check if file exists, if exists, load
        # StorageFinder.findRule(filename)
        # if exists
        # config = ConfigParser()
        # config.read(filename)
        # else
        config = {filename_base: []}
        return config

    @staticmethod
    def saveRule(filename, rule_name):

        # remove mime type and check it if exists
        splits = filename.split(".")
        if len(splits) > 2:
            raise ValueError("The name must have format <rule> or <rule>.rules")
        if len(splits) == 2:
            if splits[1] != "rules":
                raise ValueError(f"Unknown rule mime type '{splits[1]}'")
            filename = splits[0]

        config: RuleConfig = RuleManager._loadRuleFile(filename)
        config[rule_name] = []  # overwrite rules
        config[rule_name] = RuleManager._createRulesFromTileHandler()
        RuleManager._writeRuleFile(filename, config)

    @staticmethod
    def _createRulesFromTileHandler():
        rule_pos_map = {
            0: "-1 -1",
            1: "0 -1",
            2: "1 -1",
            3: "-1 0",
            4: "1 0",
            5: "-1 1",
            6: "0 1",
            7: "1 1",
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
        num_rotates = tile_status.rot // 90
        x_flip = tile_status.v_flip
        y_flip = tile_status.h_flip
        rotate = num_rotates > 0
        if num_rotates == 2:
            x_flip = not x_flip
            y_flip = not y_flip
            rotate = False
        if num_rotates == 3:
            x_flip = not x_flip
            y_flip = not y_flip
            rotate = True

        str_x_flip = " XFLIP" if x_flip else ""
        str_y_flip = " YFLIP" if y_flip else ""
        str_rotate = " ROTATE" if rotate else ""
        return f"{str_index}{str_x_flip}{str_y_flip}{str_rotate}"

    @classmethod
    def _writeRuleFile(cls, filename_base, config: RuleConfig):
        filename = f"{filename_base}.rules"
        with open(filename, 'w') as f:
            for key in config.keys():
                f.write(f"[{key}]\n")
                lines = config[key]
                for line in lines:
                    f.write(line)
                    f.write('\n')

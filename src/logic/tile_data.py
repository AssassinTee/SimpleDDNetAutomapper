from src.logic.tile_connection import TileConnection, encodeListSmall
from typing import Set, List


class TileData:
    def __init__(self, con: TileConnection, flip_h: bool, flip_v: bool, rot: bool, empty: bool):
        self.con = con
        self.h_flip = flip_h
        self.v_flip = flip_v
        self.rot = rot
        self.empty = empty

    def getAllRelations(self) -> List[TileConnection]:
        relations = [self.con]
        if self.h_flip:
            relations.append(self.con.hFlip())
        if self.v_flip:
            relations.append(self.con.vFlip())
        if self.rot:
            rot1 = self.con.rotate90()
            rot2 = rot1.rotate90()
            rot3 = rot2.rotate90()
            relations.append(rot1)
            if not (self.v_flip and self.h_flip):
                relations.append(rot2)
            relations.append(rot3)
        return relations

    def getPermutations(self) -> Set[int]:
        relations = self.getAllRelations()
        permutations = []
        for relation in relations:
            permutations.extend(relation.getPermutations())
        return encodeListSmall(permutations)

    def __copy__(self):
        td = self.con.__copy__()
        return TileData(td, self.h_flip, self.v_flip, self.rot, self.empty)

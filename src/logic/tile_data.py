from logic.tile_connection import TileConnection, encodeListSmall
from typing import Set, List

class TileData():
    def __init__(self, con: TileConnection, fliph: bool, flipv: bool, rot: bool, empty: bool):
        self.con = con
        self.hflip = fliph
        self.vflip = flipv
        self.rot = rot
        self.empty = empty

    def getAllRelations(self) -> List[TileConnection]:
        relations = [self.con]
        if self.hflip:
            relations.append(self.con.hflip())
        if self.vflip:
            relations.append(self.con.vflip())
        if self.rot:
            rot1 = self.con.rotate90()
            rot2 = rot1.rotate90()
            rot3 = rot2.rotate90()
            relations.append(rot1)
            if not (self.vflip and self.hflip):
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
        return TileData(td, self.hflip, self.vflip, self.rot, self.empty)

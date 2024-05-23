from src.backend.tile_modificators import TileMods
from src.backend.tile_status import TileStatus
from src.backend.tile_connection import TileConnection
from typing import List, Tuple

TileMapState = Tuple[TileConnection, TileStatus]


class TileData:
    """
    This class holds all tile data, which is not Qt related
    """

    def __init__(self, con: TileConnection, status: TileStatus, mods: TileMods):
        self.con = con
        self.status = status
        self.mods = mods

    def getAllPossibleModifications(self) -> List[TileMapState]:
        """
        Returns a list of all TileConnections that are possible with the current modifications
        """
        # the modifications describe, how the tile connections can be manipulated
        con_list = [(self.con.__copy__(), self.status.__copy__())]

        # add h flip variants
        if self.mods.can_h_flip:
            con_list.append((self.con.hFlip(), self.status.hFlip()))
            # include h flip rotated
            if self.mods.can_rot:
                con_list.extend(self._getPossibleModificationsRotation(self.con.hFlip(), self.status.hFlip()))

        # add v flip variants
        if self.mods.can_v_flip:
            con_list.append((self.con.vFlip(), self.status.vFlip()))
            # include v flip rotated
            if self.mods.can_rot:
                con_list.extend(self._getPossibleModificationsRotation(self.con.vFlip(), self.status.vFlip()))

        # add v flip and h flip
        if self.mods.can_v_flip and self.mods.can_h_flip:
            con_list.append((self.con.vFlip().hFlip(), self.status.vFlip().hFlip()))

        # add original rotations
        con_list.extend(self._getPossibleModificationsRotation(self.con, self.status))

        # remove duplicates TODO all of this can be optimized
        unique_ids = set()
        ret = []
        for con, status in con_list:
            encoded_val = con.encode()
            if encoded_val not in unique_ids:
                ret.append((con, status))
                unique_ids.add(encoded_val)

        return ret

    def _getPossibleModificationsRotation(self, con: TileConnection, status: TileStatus):
        con_list = []
        if self.mods.can_rot:
            con_rot1, status_rot1 = con.rotate90(), status.rot90()
            con_rot2, status_rot2 = con_rot1.rotate90(), status_rot1.rot90()
            con_rot3, status_rot3 = con_rot2.rotate90(), status_rot2.rot90()
            con_list.append((con_rot1, status_rot1))
            con_list.append((con_rot2, status_rot2))
            con_list.append((con_rot3, status_rot3))
        return con_list

    def getAllPossibleTileStates(self) -> List[TileMapState]:
        all_possible_modifications = self.getAllPossibleModifications()
        all_possible_tile_states = []
        for modified_state, status in all_possible_modifications:

            # every modification state, e.g. rotating flipping, might have other neighborhood combinations
            neighborhoods = modified_state.getPossibleNeighborhoods()
            for neighborhood in neighborhoods:
                # note, that for every modified state, the tile status, e.g. is_rotated, is_v_flipped is the same
                all_possible_tile_states.append((neighborhood, status.__copy__()))
        return all_possible_tile_states

    def __copy__(self):
        td = self.con.__copy__()
        ts = self.status.__copy__()
        tm = self.mods.__copy__()
        return TileData(td, ts, tm)

    def __eq__(self, other):
        if isinstance(other, TileData):
            return self.con == other.con and \
                self.mods == other.mods and \
                self.status == other.status
        raise NotImplementedError

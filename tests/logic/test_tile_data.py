import pytest

from src.backend.tile_connection import TileConnection
from src.backend.tile_modificators import TileMods
from src.backend.tile_status import TileStatus
from src.backend.tile_data import TileData


class TestTileData:
    @staticmethod
    def create_tile_data(neighbors, status, mods) -> TileData:
        ts = TileStatus()
        ts.v_flip = status[0]
        ts.h_flip = status[1]
        ts.rot = status[2]
        ts.empty = status[3]
        return TileData(TileConnection(neighbors),
                        ts,
                        TileMods(mods[0], mods[1], mods[2]))

    @staticmethod
    def tile_data_list(create_tile_data):
        return [
            create_tile_data([0, 1, 0, 0, 0, 0, 0, 0], [False, False, False, False], [False, False, False]),
            create_tile_data([2, 1, 2, 0, 0, 2, 0, 2], [False, False, False, False], [False, False, True]),
            create_tile_data([0, 1, 2, 0, 1, 2, 0, 1], [False, False, False, False], [True, True, False]),
            create_tile_data([0, 1, 0, 0, 0, 0, 0, 0], [False, False, False, True], [True, True, False]),
            create_tile_data([0, 1, 0, 0, 0, 0, 0, 0], [False, False, False, True], [False, True, False]),
            create_tile_data([0, 0, 0, 1, 0, 0, 0, 0], [False, False, False, True], [True, False, False]),
            create_tile_data([2, 1, 2, 0, 0, 2, 0, 2], [False, False, False, False], [False, False, False]),
            create_tile_data([1, 0, 1, 0, 0, 1, 0, 1], [False, False, False, False], [False, False, True]),
            create_tile_data([2, 2, 2, 2, 2, 2, 2, 2], [True, True, True, False], [True, True, True]),
            create_tile_data([0, 1, 2, 1, 0, 2, 1, 0], [True, True, True, False], [True, True, True]),
        ]

    @staticmethod
    def tile_data_list_modifications(tile_data_list, create_tile_data):
        ret = []
        td_list = tile_data_list(create_tile_data)
        num_modifications = [
            1,  # no modifications
            4,  # only rotations
            4,  # fliph and flipv
            2,  # only vflip does something
            1,  # hflip doesn't do anything
            1,  # vflip doesn't do anything
            1,  # none
            1,  # rotating doesn't do anything
            1,  # fliph, flipv and rot, but nothing changes a thing
            8,  # flips and rot
        ]

        # pack for pytest
        for i, td in enumerate(td_list):
            ret.append([num_modifications[i], td])
        return ret

    @pytest.mark.parametrize("tile_data", tile_data_list(create_tile_data))
    def test_init(self, tile_data):
        assert isinstance(tile_data, TileData)

    def test_equal(self):
        td_list = self.tile_data_list(self.create_tile_data)
        for i, td in enumerate(td_list):
            assert td == td
            assert td != td_list[(i + 1) % len(td_list)]

    @pytest.mark.parametrize("tile_data", tile_data_list(create_tile_data))
    def test_copy(self, tile_data):
        t2 = tile_data.__copy__()
        assert t2 == tile_data
        assert t2.con == tile_data.con
        assert t2.status == tile_data.status
        assert t2.mods == tile_data.mods
        assert id(t2) != id(tile_data)
        # test deep copy
        assert id(t2.con) != id(tile_data.con)
        assert id(t2.status) != id(tile_data.status)
        assert id(t2.mods) != id(tile_data.mods)

    @pytest.mark.parametrize("num_mods, tile_data", tile_data_list_modifications(tile_data_list, create_tile_data))
    def test_get_modifications(self, num_mods, tile_data):
        mods = tile_data.getAllPossibleModifications()
        assert len(mods) == num_mods

        # check, that I am working on copies
        for tc, ts in mods:
            assert id(tc) != id(tile_data.con)
            assert id(ts) != id(tile_data.status)

        # check every tile status is only once available
        ts_list = [ts for _, ts in mods]
        for ts in ts_list:
            # I call copy here explicitly to show, that count does go over value and not reference
            assert ts_list.count(ts.__copy__()) == 1

    @pytest.mark.parametrize("num_mods, tile_data", tile_data_list_modifications(tile_data_list, create_tile_data))
    def test_get_tile_states(self, num_mods, tile_data):
        numb_changeable_states = tile_data.con.getNeighbors().count(2)
        num_states = 2**numb_changeable_states

        possible_tile_states = tile_data.getAllPossibleTileStates()

        # sanity checks (no sanity found)
        assert len(possible_tile_states) == num_mods * num_states
        assert len(possible_tile_states) > 0

        # check, that there is no ANY connection left
        for tile_con, _ in possible_tile_states:
            assert tile_con.getNeighbors().count(2) == 0

        # check, that I am working on copies
        for tc, ts in possible_tile_states:
            assert id(tc) != id(tile_data.con)
            assert id(ts) != id(tile_data.status)

        tc_list = [tc for tc, _ in possible_tile_states]

        # check easy combinations, that should be in
        # Note, that multiple states can have the same connection
        assert tc_list.count(tile_data.con.getFull()) >= 1
        assert tc_list.count(tile_data.con.getEmpty()) >= 1

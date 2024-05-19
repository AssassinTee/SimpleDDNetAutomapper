import pytest

from src.logic.tile_status import TileStatus


class TestTileStatus:
    def test_init(self):
        TileStatus()

    @staticmethod
    def create_tile_status(v_flip, h_flip, rot, empty) -> TileStatus:
        assert rot % 90 == 0
        t = TileStatus()
        t.v_flip = v_flip
        t.h_flip = h_flip
        t.rot = rot
        t.empty = empty
        return t

    @staticmethod
    def status_list(create_tile_status):
        return [
            TileStatus(),
            create_tile_status(True, False, 90, False),
            create_tile_status(False, False, 180, True),
            create_tile_status(True, True, 270, True),
            create_tile_status(False, True, 90, False),
        ]

    @pytest.mark.parametrize("status", status_list(create_tile_status))
    def test_copy_and_equal(self, status):
        t2 = status.__copy__()
        assert t2 == status
        assert id(t2) != id(status)
        t2.h_flip = not t2.h_flip
        assert t2 != status
        t2.h_flip = not t2.h_flip
        assert t2 == status

    @pytest.mark.parametrize("status", status_list(create_tile_status))
    def test_rot90(self, status):
        rot = status.rot
        rot_status = status.rot90()
        assert rot_status.rot % 90 == 0
        assert rot_status.rot < 360
        # make sure it's clockwise
        assert rot_status.rot == 0 or rot_status.rot > rot
        assert status == status.rot90().rot90().rot90().rot90()

    @pytest.mark.parametrize("status", status_list(create_tile_status))
    def test_rot45(self, status):
        assert status.rot45().rot45() == status.rot90()

    @pytest.mark.parametrize("status", status_list(create_tile_status))
    def test_v_flip(self, status):
        t = status.vFlip()
        assert t != status
        assert t.v_flip != status.v_flip
        assert id(t) != id(status)

    @pytest.mark.parametrize("status", status_list(create_tile_status))
    def test_h_flip(self, status):
        t = status.hFlip()
        assert t != status
        assert t.h_flip != status.h_flip
        assert id(t) != id(status)

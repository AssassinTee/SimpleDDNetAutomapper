from src.backend.tile_connection import TileConnection, encodeListSmall
import pytest


class TestTileConnection:

    @staticmethod
    def correct_neighbors():
        return [
            [0] * 8,
            [1] * 8,
            [2] * 8,
            [0, 1, 2, 0, 1, 2, 0, 1],
        ]

    @pytest.mark.parametrize("neighbors", correct_neighbors())
    def test_init(self, neighbors):
        TileConnection(neighbors)

    @pytest.mark.parametrize("neighbors", [
        [0],
        [2, 3, 4, 5, 6, 7, 8, 9],
        [0, 0, 0, 0, 0, 0, 0, 3],
        [0, 0, 0, 0, 0, 0, 0, -1],
    ])
    def test_init_illegal(self, neighbors):
        with pytest.raises(ValueError):
            TileConnection(neighbors)

    @pytest.mark.parametrize("encoded_val, neighbors", [
        [0, [0] * 8],
        [0b0101010101010101, [1] * 8],
        [0b0001000100010001, [0, 1, 0, 1, 0, 1, 0, 1]],
    ])
    def test_encode(self, encoded_val, neighbors):
        t = TileConnection(neighbors)
        assert t.encode() == encoded_val

    @pytest.mark.parametrize("encoded_val, neighbors", [
        [0, [0] * 8],
        [0b11111111, [1] * 8],
        [0b01010101, [0, 1, 0, 1, 0, 1, 0, 1]],
    ])
    def test_encode_small(self, encoded_val, neighbors):
        t = TileConnection(neighbors)
        assert t.encodeSmall() == encoded_val

    @pytest.mark.parametrize("neighbors", [
        [2] * 8,
        [0, 1, 2, 0, 1, 2, 0, 1],
    ])
    def test_encode_small_any(self, neighbors):
        t = TileConnection(neighbors)
        with pytest.raises(ValueError):
            t.encodeSmall()

    @pytest.mark.parametrize("tile_connection, tile_connection2", [
        [TileConnection([0] * 8), TileConnection([1] * 8)],
        [TileConnection([1] * 8), TileConnection([0] * 8)],
        [TileConnection([0, 1, 0, 1, 0, 1, 0, 1]), TileConnection([0, 0, 1, 1, 0, 0, 1, 1])],
    ])
    def test_compare(self, tile_connection, tile_connection2):
        assert tile_connection != tile_connection2
        assert tile_connection == tile_connection
        assert tile_connection2 == tile_connection2

    @pytest.mark.parametrize("tile_connections", [
        [TileConnection([0] * 8)],
        [],
        [TileConnection([0] * 8), TileConnection([1] * 8)],
        [TileConnection([0] * 8), TileConnection([0] * 8)],
    ])
    def test_encode_list_small(self, tile_connections):
        tcl = encodeListSmall(tile_connections)

        # check a case where the list might be shorter
        if len(tile_connections) >= 2 and tile_connections[0] == tile_connections[1]:
            assert len(tcl) < len(tile_connections)
        assert len(tcl) <= len(tile_connections)
        for tc in tile_connections:
            assert tc.encodeSmall() in tcl

    def test_str(self):
        t = TileConnection([1] * 8)
        assert len(str(t))

    def test_get_neighbors(self):
        n = [0, 1, 0, 1, 0, 1, 0, 1]
        t = TileConnection(n)
        assert t.getNeighbors() == n

    def test_set_neighbor(self):
        n = [0, 1, 0, 1, 0, 1, 0, 1]
        t = TileConnection(n)
        assert t.getNeighbors() == n
        t.setNeighbor(7, 0)
        assert t.getNeighbors() != n
        n[7] = 0
        assert t.getNeighbors() == n

    def test_copy(self):
        t = TileConnection([0, 1, 0, 1, 0, 1, 0, 1])
        t2 = t.__copy__()
        assert t == t2
        assert t.getNeighbors() == t2.getNeighbors()
        # make sure they are different objects
        assert id(t) != id(t2)

    @pytest.mark.parametrize("expected, neighbors", [
        [0, [0] * 8],
        [0b11111111, [1] * 8],
        [0b11111111, [2] * 8],
        [0b01101101, [0, 1, 2, 0, 1, 2, 0, 1]],
    ])
    def test_get_full(self, expected, neighbors):
        t = TileConnection(neighbors)
        t2 = t.getFull()
        assert t2.encodeSmall() == expected

    @pytest.mark.parametrize("expected, neighbors", [
        [0, [0] * 8],
        [0b11111111, [1] * 8],
        [0, [2] * 8],
        [0b01001001, [0, 1, 2, 0, 1, 2, 0, 1]],
    ])
    def test_get_empty(self, expected, neighbors):
        t = TileConnection(neighbors)
        t2 = t.getEmpty()
        assert t2.encodeSmall() == expected

    @pytest.mark.parametrize("neighbors", correct_neighbors())
    def test_rotate(self, neighbors):
        t = TileConnection(neighbors)
        t2 = t.__copy__()
        for i in range(4):  # rotate 360
            t2 = t2.rot()
        assert t2 == t

    @pytest.mark.parametrize("rotated, neighbors", [
        [0b00100000, [1, 0, 0, 0, 0, 0, 0, 0]],
        [0b00001000, [0, 1, 0, 0, 0, 0, 0, 0]],
        [0b00000001, [0, 0, 1, 0, 0, 0, 0, 0]],
        [0b01000000, [0, 0, 0, 1, 0, 0, 0, 0]],
        [0b00000010, [0, 0, 0, 0, 1, 0, 0, 0]],
        [0b10000000, [0, 0, 0, 0, 0, 1, 0, 0]],
        [0b00010000, [0, 0, 0, 0, 0, 0, 1, 0]],
        [0b00000100, [0, 0, 0, 0, 0, 0, 0, 1]],
    ])
    def test_rotation_is_clockwise(self, rotated, neighbors):
        t = TileConnection(neighbors)
        rot = t.rot()
        assert rot.encodeSmall() == rotated

    @pytest.mark.parametrize("neighbors", correct_neighbors())
    def test_v_flip(self, neighbors):
        t = TileConnection(neighbors)
        t2 = t.__copy__()
        assert t2.vFlip().vFlip() == t
        assert t2.vFlip() == t.vFlip()

    @pytest.mark.parametrize("neighbors", correct_neighbors())
    def test_h_flip(self, neighbors):
        t = TileConnection(neighbors)
        t2 = t.__copy__()
        assert t2.hFlip().hFlip() == t
        assert t2.hFlip() == t.hFlip()

    @pytest.mark.parametrize("neighbors", correct_neighbors())
    def test_flip_rot_sanity(self, neighbors):
        t = TileConnection(neighbors)
        t2 = t.__copy__()
        assert t.rot().rot() == t2.hFlip().vFlip()

    @pytest.mark.parametrize("expected, neighbors", [
        [[0], [0] * 8],
        [[0b11111111], [1] * 8],
        ["all", [2] * 8],
        [[0b01001001, 0b01101001, 0b01001101, 0b01101101], [0, 1, 2, 0, 1, 2, 0, 1]],
    ])
    def test_get_permutations(self, expected, neighbors):
        t = TileConnection(neighbors)
        perms = t.getPossibleNeighborhoods()
        perms_enc = [p.encodeSmall() for p in perms]
        if expected == "all":
            assert len(perms) == 2 ** 8
            for i in range(2 ** 8):
                assert i in perms_enc
        else:
            assert len(expected) == len(perms)
            for exp in expected:
                assert exp in perms_enc

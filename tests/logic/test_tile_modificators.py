import pytest

from src.backend.tile_modificators import TileMods


class TestTileModificators:
    @staticmethod
    def modificators():
        return [
            [False, False, False],
            [False, False, True],
            [False, True, False],
            [False, True, True],
            [True, False, False],
            [True, False, True],
            [True, True, False],
            [True, True, True],
        ]

    @pytest.mark.parametrize("mod", modificators())
    def test_init(self, mod):
        TileMods(mod[0], mod[1], mod[2])

    def test_eq(self):
        modies = self.modificators()
        for i, mods in enumerate(modies):
            mod = TileMods(mods[0], mods[1], mods[2])
            assert mod == mod
            mods2 = modies[(i + 1) % len(modies)]
            mod2 = TileMods(mods2[0], mods2[1], mods2[2])
            assert mod != mod2

    @pytest.mark.parametrize("mods", modificators())
    def test_copy(self, mods):
        mod = TileMods(mods[0], mods[1], mods[2])
        assert mod == mod
        mod2 = mod.__copy__()
        assert mod == mod2
        assert id(mod) != id(mod2)
        mod2.can_h_flip = not mod2.can_h_flip
        assert mod != mod2

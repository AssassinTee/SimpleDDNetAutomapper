import pytest

from src.backend.tile_connection import TileConnection
from src.backend.tile_data import TileData
from src.backend.tile_modificators import TileMods
from src.backend.tile_status import TileStatus
from src.backend.tile_handler import TileHandler
from src.widgets.widget_base_tile import BaseTile
from src.images_helper import ImageHelper


class TestTileHandler:
    def test_init(self):
        with pytest.raises(RuntimeError):
            TileHandler()

    def test_instance(self):
        assert isinstance(TileHandler.instance(), TileHandler)

    def test_reference(self):
        th1 = TileHandler.instance()
        th2 = TileHandler.instance()

        assert id(th1) == id(th2)

    @pytest.fixture
    def tile(self, q_app):
        tc = TileConnection([0, 1, 2, 1, 0, 1, 0, 2])  # asymetrical
        ts = TileStatus()
        tm = TileMods(True, True, True)
        td = TileData(tc, ts, tm)
        return BaseTile(0, td)

    @pytest.fixture
    def add_tile(self, tile):
        TileHandler.instance().addTileToStorage(tile)
        yield
        TileHandler.instance().removeTileFromStorage(tile.tile_id)

    @pytest.fixture
    def add_pixmap(self, tile):
        # add any pixmap
        pm = ImageHelper.instance().NO_TILE_FOUND
        tile.setPixmap(pm)
        TileHandler.instance().addPixmap(tile)
        yield
        del TileHandler.instance().pix_map[tile.tile_id]

    @pytest.mark.requires_q_app
    def test_add_tile_to_storage(self, add_tile):
        pass

    def test_get_tile(self):
        with pytest.raises(ValueError):
            TileHandler.instance().getTile(1)

    @pytest.mark.requires_q_app
    def test_get_pixmap(self, add_tile, add_pixmap):
        assert TileHandler.instance().getPixmap(0) is not None

    def test_get_pixmap_invalid_id(self):
        with pytest.raises(ValueError):
            TileHandler.instance().getPixmap(256)

    @pytest.mark.requires_q_app
    def test_add_pixmap_already_entered(self, tile, add_pixmap):
        with pytest.raises(ValueError):
            TileHandler.instance().addPixmap(tile)

    @pytest.mark.requires_q_app
    def test_add_pixmap_empty(self, tile):
        with pytest.raises(ValueError):
            TileHandler.instance().addPixmap(tile)

    @pytest.mark.requires_q_app
    def test_add_tile_to_storage_illegal_base_tile(self):
        with pytest.raises(ValueError):
            b = BaseTile(0, None)
            TileHandler.instance().addTileToStorage(b)

    @pytest.mark.requires_q_app
    def test_find_tiles(self, add_tile, tile):
        tile_states = tile.tile_data.getAllPossibleTileStates()
        states = [s for _, s in tile_states]
        for tile_con, _ in tile_states:
            neighborhood_entry_list = TileHandler.instance().findTiles(tile_con)
            assert len(neighborhood_entry_list) > 0
            for tile_id, state in neighborhood_entry_list:
                assert tile_id == tile.tile_id
                assert state in states

    @pytest.mark.requires_q_app
    def test_remove_tile_from_storage(self, add_tile, tile):
        TileHandler.instance().removeTileFromStorage(tile.tile_id)
        tile_states = tile.tile_data.getAllPossibleTileStates()
        for tile_con, _ in tile_states:
            neighborhood_entry_list = TileHandler.instance().findTiles(tile_con)
            assert len(neighborhood_entry_list) == 0

        assert len(TileHandler.instance().tile_id_map) == 0

    @pytest.mark.requires_q_app
    def test_update_storage(self, add_tile, tile):
        neighborhood_entry_list = TileHandler.instance().findTiles(tile.tile_data.con)
        num_matches = len(neighborhood_entry_list)
        TileHandler.instance().updateTileStorage(tile)

        neighborhood_entry_list = TileHandler.instance().findTiles(tile.tile_data.con)
        num_matches2 = len(neighborhood_entry_list)
        assert num_matches2 == num_matches

        # disable rotating and flipping
        tile.tile_data.mods.can_rot = not tile.tile_data.mods.can_rot
        tile.tile_data.mods.can_v_flip = not tile.tile_data.mods.can_v_flip
        tile.tile_data.mods.can_h_flip = not tile.tile_data.mods.can_h_flip
        TileHandler.instance().updateTileStorage(tile)
        neighborhood_entry_list = TileHandler.instance().findTiles(tile.tile_data.con)
        num_matches3 = len(neighborhood_entry_list)
        assert num_matches3 != num_matches

        # the only changes are coming from the tile connections
        assert num_matches3 == 2 ** tile.tile_data.con.getNeighbors().count(2)

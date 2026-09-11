import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402
from PyQt6.QtGui import QColor, QPainter, QPixmap  # noqa: E402

from src.buttons.button_tile_connection import TileConnectionButton  # noqa: E402
from src.backend.tile_data import TileData  # noqa: E402
from src.backend.tile_connection import TileConnection  # noqa: E402
from src.backend.tile_modificators import TileMods  # noqa: E402
from src.backend.tile_status import TileStatus  # noqa: E402
from src.widgets.widget_base_tile import BaseTile  # noqa: E402


def _make_tile(tile_id=1, status=None):
    tile_data = TileData(TileConnection([0] * 8), status or TileStatus(), TileMods(False, False, False))
    return BaseTile(tile_id, tile_data)


def _make_arrow_pixmap():
    pm = QPixmap(2, 2)
    pm.fill(QColor(K_EMPTY))
    p = QPainter(pm)
    p.fillRect(0, 0, 1, 1, QColor("red"))
    p.fillRect(1, 0, 1, 1, QColor("green"))
    p.fillRect(0, 1, 1, 1, QColor("blue"))
    p.fillRect(1, 1, 1, 1, QColor("yellow"))
    p.end()
    return pm


K_EMPTY = "#00000000"


@pytest.mark.requires_q_app
def test_set_tile_stores_status_copy(q_app):
    btn = TileConnectionButton(0)
    tile = _make_tile(7)
    base_status = TileStatus()
    rotated_status = TileStatus()
    rotated_status.rot = True

    btn.setTile(tile, False, base_status)
    assert btn._tile_status == base_status

    btn.setTile(tile, False, rotated_status)
    assert btn._tile_status == rotated_status
    assert btn._tile_status.rot


@pytest.mark.requires_q_app
def test_set_tile_dedups_only_when_status_is_equal(q_app):
    btn = TileConnectionButton(0)
    tile = _make_tile(7)
    base_status = TileStatus()
    rotated_status = TileStatus()
    rotated_status.rot = True

    btn.setTile(tile, False, base_status)
    stored_before = btn._tile_status

    # same tile + same status -> no re-render required
    btn.setTile(tile, False, base_status)
    assert btn._tile_status is stored_before

    # same tile but different orientation -> must be re-rendered
    btn.setTile(tile, False, rotated_status)
    assert btn._tile_status is not stored_before
    assert btn._tile_status.rot


@pytest.mark.requires_q_app
def test_rotated_suggestion_is_drawn_rotated(q_app):
    btn = TileConnectionButton(0)
    tile = _make_tile(3)
    tile.setPixmap(_make_arrow_pixmap())
    status = TileStatus()
    status.rot = True

    btn.setState(1)  # FULL: the tile is rendered
    btn.setTile(tile, False, status)

    img = btn.grab().toImage()
    assert img.pixelColor(0, 0).name() == "#0000ff"       # BL -> TL
    assert img.pixelColor(127, 0).name() == "#ff0000"     # TL -> TR
    assert img.pixelColor(127, 127).name() == "#008000"   # TR -> BR
    assert img.pixelColor(0, 127).name() == "#ffff00"     # BR -> BL


@pytest.mark.requires_q_app
def test_y_flipped_suggestion_is_drawn_mirrored(q_app):
    btn = TileConnectionButton(0)
    tile = _make_tile(3)
    tile.setPixmap(_make_arrow_pixmap())
    status = TileStatus()
    status.y_flip = True

    btn.setState(1)
    btn.setTile(tile, False, status)

    img = btn.grab().toImage()
    assert img.pixelColor(0, 0).name() == "#0000ff"       # BL -> TL
    assert img.pixelColor(0, 127).name() == "#ff0000"     # TL -> BL
    assert img.pixelColor(127, 0).name() == "#ffff00"     # BR -> TR

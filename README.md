[![Build](https://github.com/AssassinTee/SimpleDDNetAutomapper/actions/workflows/build.yml/badge.svg)](https://github.com/AssassinTee/SimpleDDNetAutomapper/actions/workflows/build.yml)
[![Tests](https://github.com/AssassinTee/SimpleDDNetAutomapper/actions/workflows/test.yml/badge.svg)](https://github.com/AssassinTee/SimpleDDNetAutomapper/actions/workflows/test.yml)
[![Lint](https://github.com/AssassinTee/SimpleDDNetAutomapper/actions/workflows/lint.yml/badge.svg)](https://github.com/AssassinTee/SimpleDDNetAutomapper/actions/workflows/lint.yml)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/AssassinTee/SimpleDDNetAutomapper/issues)

# NOTE
WIP (work in progress). This tool isn't ready yet to be announced to the public, but it 
reached the alpha stage.

That beeing said, if you want to test it and create automapper rules, edit your `config.yml` and enter
- `client_path`(optional): The absolute path to your ddnet client (On windows this is ddnet.exe) 
- `data_path`: The absolute path to your ddnet data (The `data` directory in your `ddnet` directory)

---

# Simple DDNet Automapper App
A simple tool to create automapping files for ddnet with a graphical user interface

## Download

_Give me a bloody exe:_
[https://github.com/AssassinTee/SimpleDDNetAutomapper/releases/latest](https://github.com/AssassinTee/SimpleDDNetAutomapper/releases/latest)

## Installation

You may want to put the software in its own directory, since it may generate files.


### Windows

This software comes bundled up, just download the version for your OS and start it.

### Ubuntu latest:
This software uses PyQt6, which is maybe missing some dependencies on your OS.
If you run into issues with this software, install
```bash
sudo apt update
sudo apt-get install -y libegl1
sudo apt-get install -y libxcb-xinerama0
sudo apt-get install -y -qq libglu1-mesa-dev libx11-xcb-dev '^libxcb*'
```

You can find more on this topic [here](https://askubuntu.com/questions/1485442/issue-with-installing-pyqt6-on-ubuntu-22-04)

## Guide

TODO: Do a proper guide, guide below is just for a minimal product

0. Go to `Settings` and configure ddnet and your `data` directory (usually in side the ddnet directory) properly
1. Load mapres image, like `grass_main.png` by clicking `Select Image`
2. Configure all tiles you want to use for your automapper
    - select FULL/EMPTY/ANY
      - FULL: This neighbor of the (middle) tile is FULL, not EMPTY
      - EMPTY: This neighbor of the (middle) tile is EMPTY, not FULL
      - ANY: This neighbor of the (middle)tile is EMPTY or FULL
    - select Rotate/X-Flip/Y-Flip, don't use Empty yet
      - Rotate: This (middle) tile can be rotated
      - X-Flip: This (middle) tile can be mirrored left <-> right (written as `XFLIP`)
      - Y-Flip: This (middle) tile can be mirrored top <-> bottom (written as `YFLIP`)
      - Empty: Not yet ready for usuage, FUTURE: Allows (middle) tile to be EMPTY
    - remove a configured tile with right click
3. Name your rule (top right, `Name Mapping Rule`)
4. Press `Generate`, this will test your mapping rules, press `Ok` and your mapping rules will automatically be saved
in the data directory

You can press `Generate` without being finished to check on your work, just press `Cancel` and continue 
editing your tiles

## How rules are ordered

- **Tiles**: For rule conflicts the most specific rule wins (e.g. a very specific rule will win over one using many any) 
- **Groups**: Groups higher in the list are applied first
- Groups are applied before Tiles

## TODO

- Migrate the remaining hardcoded neighbor tables to `src/backend/neighbor.py`
- Replace the 6 hand-rolled `instance()` singletons with module-level instances
- Fix window scaling: Linux stretches the tileset, macOS grows past the screen, ...
- Drop the `.rules` backend and keep only `.r`, which needs rpp shipped with the app
- Fix the center checkboxes, they never load their state back from the tile
- Teach `StorageFinder` where ddnet lives on macOS, maybe reuse patiga's tooling
- Improve packaging, ship rpp with the app and stop depending on the working directory
- Fix `@BroadErrorHandler` breaking PyQt's arg-count introspection, requires `checked=False` on connected slots
- Warn about unsaved changes on quit
- Hide the "Select Image" button while an image is loaded, use File > Open instead

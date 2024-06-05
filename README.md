# NOTE
WIP (work in progress). This tool isn't ready yet to be announced to the public, but it 
reached the alpha stage. If you encounter bugs or experience crashes, please don't report them yet as this software
has still a lot of loose ends.

That beeing said, if you want to test it and create automapper rules, edit your `config.yml` and enter
- `client_path`(optional): The absolute path to your ddnet client (On windows this is ddnet.exe) 
- `data_path`: The absolute path to your ddnet data (The `data` directory in your `ddnet` directory)

---

# Simple DDNet Automapper App
A simple tool to create automapping files for ddnet with a graphical user interface

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

1. Load mapres image, like `grass_main.png` by clicking `Select Image`
2. Configure Tiles you want to use for your automapper
    - select FULL/EMPTY/ANY, TODO explain what this means
    - select rotation/hflip/vflip, don't use empty yet
3. Name your rule (top right, `Name Mapping Rule`)
4. Press `Generate`, this will test your mapping rules, press `Ok` and your mapping rules will automatically be saved
in the data directory

You can press `Generate` without being finished to check on your work, just press `Cancel` and continue 
editing your tiles
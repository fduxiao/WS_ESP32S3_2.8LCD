#!/usr/bin/env python3
import os
from pathlib import Path


SELF = Path(__file__)
HERE = SELF.parent


rom_data = HERE / "rom_data.py"
LINE_LEN = 32


class Writter:
    def __init__(self, file) -> None:
        self.file = file

    def freeze(self, name, path):
        self.file.write(f"{name} = \\\n")
        with open(path, 'rb') as target:
            while True:
                bs = target.read(LINE_LEN)
                if len(bs) == 0:
                    break
                self.file.write(repr(bs))
                self.file.write("\\\n")
        self.file.write("\n")


with open(rom_data, "w") as file:
    writter = Writter(file)
    writter.freeze("data_main", HERE / "main.py")
    writter.freeze("data_defs", HERE / "defs.py")

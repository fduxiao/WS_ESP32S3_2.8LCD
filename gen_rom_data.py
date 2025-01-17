#!/usr/bin/env python3
from pathlib import Path


SELF = Path(__file__)
HERE = SELF.parent.absolute()


rom_data = HERE / "rom_data.py"
LINE_LEN = 32

INDENT = ' ' * 4


class Writter:
    def __init__(self, file) -> None:
        self.file = file

    def freeze(self, name, path):
        self.file.write(f"\n{name} = \\\n")
        with open(path, 'rb') as target:
            while True:
                bs = target.read(LINE_LEN)
                if len(bs) == 0:
                    break
                self.file.write(INDENT)
                self.file.write(repr(bs))
                self.file.write(" \\\n")
        self.file.write(f"{INDENT}b''\n")


with open(rom_data, "w") as file:
    writter = Writter(file)
    writter.freeze("data_defs", HERE / "defs.py")

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

    def write(self, data):
        return self.file.write(data)

    def write_name(self, name):
        self.write(f"\n{name} = \\\n")

    def write_line(self, bs):
        self.write(INDENT)
        self.write(repr(bs))
        self.write(" \\\n")

    def break_write(self, bs):
        i = 0
        while i < len(bs):
            self.write_line(bs[i:(i+LINE_LEN)])
            i += LINE_LEN

    def write_end(self):
        self.write(f"{INDENT}b''\n")

    def freeze(self, name, path):
        self.write_name(name)
        with open(path, 'rb') as target:
            while True:
                bs = target.read(LINE_LEN)
                if len(bs) == 0:
                    break
                self.write_line(bs)
        self.write_end()


with open(rom_data, "w") as file:
    writter = Writter(file)
    writter.freeze("data_defs", HERE / "defs.py")

    # write test wav
    writter.write_name("data_wav")
    freq = 440
    rate = 44100
    bits = 16
    time = 2
    amp = 1 << (bits - 1)
    amp /= 4
    import numpy as np
    # calculate one batch
    values = np.array(range(time * rate), dtype=float)
    values /= rate
    values = amp * np.sin(values * 2 * np.pi * freq)
    # cast to int16
    values = np.array(values, dtype=np.int16)
    # reshape to make left and right channels
    values = values.reshape((-1, 1))
    values = np.concatenate((values, values), axis=1).reshape(-1)
    values = values.tobytes()
    writter.break_write(values)
    writter.write_end()

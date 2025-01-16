import os
import rom_data


files = os.listdir('/')
os.chdir('/')


def ensure(path, data):
    if path not in files:
        with open(path, 'wb') as file:
            file.write(data)


ensure('main.py', rom_data.data_main)
ensure('defs.py', rom_data.data_defs)

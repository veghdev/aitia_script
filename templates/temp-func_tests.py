import subprocess
import argparse

import sys
import pathlib
import platform

program_path = pathlib.Path(__file__).absolute()
program_lib_path = pathlib.Path.joinpath(program_path.parent, '../lib').resolve()
program_version = '0.0.1'
program_platform = platform.system()
sys.path.append(str(program_lib_path))


def resolve_path(*args):
    if len(args) > 1:
        return pathlib.Path.joinpath(*args).resolve()
    else:
        return pathlib.Path(*args).resolve()


def generate(configs):
    for config in configs:
        path = resolve_path(program_path.parent, config)
        if path.is_file():
            subprocess.call(['python', r'temp-func_test.py', '-c', path, *sys.argv[1:]])
        else:
            generate(path.iterdir())


# main

generate(['config-func_test'])

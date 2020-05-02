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


def parse_args():
    parser = argparse.ArgumentParser(description='generate func_tests from templates',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--config',
                        help='select config directory',
                        nargs='+',
                        required=True)

    parser.add_argument('-t', '--test_dir',
                        help='test directory relative path',
                        default='../test')

    parser.add_argument('-rl', '--report_level',
                        help='set report level',
                        choices=['VERBOSE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO')
    parser.add_argument('--recreate_default_ini',
                       help='recreate default ini',
                       action="store_true",
                       default=False)
    parser.add_argument('--recreate_test_file',
                        help='recreate test file',
                        action="store_false",
                        default=True)

    args = parser.parse_args()

    return args


def resolve_path(*args):
    if len(args) > 1:
        return pathlib.Path.joinpath(*args).resolve()
    else:
        return pathlib.Path(*args).resolve()


def generate(configs):
    for config in configs:
        path = resolve_path(program_path.parent, config)
        if path.is_file():
            process = list()
            process.append('python')
            process.append(r'temp-func_test.py')

            process.append('-c')
            process.append(config)

            process.append('-t')
            process.append(args.test_dir)

            process.append('-rl')
            process.append(args.report_level)

            if args.recreate_default_ini:
                process.append('--recreate_default_ini')

            if not args.recreate_test_file:
                process.append('--recreate_default_ini')

            subprocess.call(process)
        else:
            generate(path.iterdir())


# main

args = parse_args()

generate(args.config)
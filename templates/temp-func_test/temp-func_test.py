import sys
import pathlib
import subprocess


def processing():
    global exit_code
    for process in processes:
        ans = subprocess.call(['python',r'{}'.format(pathlib.Path.joinpath(pathlib.Path(__file__).absolute().parent, process)), *sys.argv[1:]])
        if ans != 0:
            if exit_code != 0:
                if ans < exit_code:
                    exit_code = ans
            else:
                exit_code = ans
    exit(exit_code)


exit_code = 0
processes = list()
for dir in pathlib.Path(__file__).absolute().parent.iterdir():
    if dir.is_dir():
        for file in dir.iterdir():
            if file.is_file():
                if file.name == 'func_test.py':
                    processes.append('{}/{}'.format(dir.name, file.name))
processing()

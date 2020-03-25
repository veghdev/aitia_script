import pathlib
import sys
program_path = str(pathlib.Path(sys.path[0]))
program_name = pathlib.Path(__file__).stem
program_lib_path = str(pathlib.Path(f'{program_path}/../../../lib').resolve())
sys.path.append(program_lib_path)

import shutil
import os
import yaml
import subprocess
import filecmp
import re

from tools import Logger
from cterm import CtermInterface
from app.gy_app import ControlSgaCDRQueryServer, ControlSgaAutho
from tools.config_tools.ini_config_tools import read_ini_file, write_ini_file, modify_ini_content


# subroutines
def resolve_path(o_path, o_name, make_path=False):
    original = str(pathlib.Path(o_path + '/' + o_name))
    if not os.path.exists(original):
        new = str(pathlib.Path(o_path + '/' + '__' + o_name))
        if os.path.exists(new):
            with open(new, 'r') as file_handler:
                new = file_handler.read()
                new = str(pathlib.Path(shared_test_files_path + '/' + new))
                return {'path': new, 'o_name': o_name, 'o_path': original}
        else:
            if make_path:
                os.makedirs(original)
            else:
                raise Exception(f'can not find file: {original}')
    return {'path': original, 'o_name': o_name, 'o_path': original}


# parameters
log_level = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
log_path = str(pathlib.Path(program_path + '/' + program_name))
bin_path = str(pathlib.Path(program_path + '/' + '../bin'))
test_cases_path = str(pathlib.Path(program_path + '/' + 'test_cases'))
shared_test_files_path = str(pathlib.Path(program_path + '/' + 'shared_test_files'))

# create logger
logger = Logger(logger=program_name, log_level=log_level, log_file=log_path)
tab = '    '

logger.log('options:', text_level='INFO', foreground_color='light blue')
logger.log(f'{tab}program_name : {program_name}', text_level='INFO')
logger.log(f'{tab}program_path : {program_path}', text_level='INFO')
logger.log(f'{tab}program_lib_path : {program_lib_path}', text_level='INFO')
logger.log(f'{tab}log_level : {log_level}', text_level='INFO')
logger.log(f'{tab}log_path : {log_path}_yyyymmdd.log', text_level='INFO')
logger.log(f'{tab}bin_path : {bin_path}', text_level='INFO')
logger.log(f'{tab}test_cases_path : {test_cases_path}', text_level='INFO')
logger.log(f'{tab}shared_test_files_path : {shared_test_files_path}', text_level='INFO')


logger.log('start testing...', text_level='INFO', foreground_color='light blue')

try:
    passed = 0
    failed = 0
    unstable = 0
    # iterate through test case directories
    test_cases = os.listdir(pathlib.Path(test_cases_path))
    for test_case in test_cases:

        # test parameters
        logger.log(f'{tab}{test_case} - options:', text_level='DEBUG', foreground_color='light blue')

        in_resolved = resolve_path(str(pathlib.Path(test_cases_path + '/' + test_case)), 'in')
        out_resolved = resolve_path(str(pathlib.Path(test_cases_path + '/' + test_case)), 'out', make_path=True)
        debug_resolved = resolve_path(str(pathlib.Path(test_cases_path + '/' + test_case)), 'debug', make_path=True)
        ref_resolved = resolve_path(str(pathlib.Path(test_cases_path + '/' + test_case)), 'ref', make_path=True)
        if in_resolved['path'] != in_resolved['o_path']:
            logger.log(f'{tab}{test_case} - {tab}in_path : {in_resolved["path"]}'
                       f'(resolved from __{in_resolved["o_name"]})',
                       text_level='DEBUG', foreground_color='light cyan')
        else:
            logger.log(f'{tab}{test_case} - {tab}in_path : {in_resolved["path"]}', text_level='DEBUG')
        if out_resolved['path'] != out_resolved['o_path']:
            logger.log(f'{tab}{test_case} - {tab}out_path : {out_resolved["path"]}'
                       f'(resolved from __{out_resolved["o_name"]})',
                       text_level='DEBUG', foreground_color='light cyan')
        else:
            logger.log(f'{tab}{test_case} - {tab}out_path : {out_resolved["path"]}', text_level='DEBUG')
        if debug_resolved['path'] != debug_resolved['o_path']:
            logger.log(f'{tab}{test_case} - {tab}debug_path : {debug_resolved["path"]}'
                       f'(resolved from __{debug_resolved["o_name"]})',
                       text_level='DEBUG', foreground_color='light cyan')
        else:
            logger.log(f'{tab}{test_case} - {tab}debug_path : {debug_resolved["path"]}', text_level='DEBUG')
        if ref_resolved['path'] != ref_resolved['o_path']:
            logger.log(f'{tab}{test_case} - {tab}ref_path : {ref_resolved["path"]}'
                       f'(resolved from __{ref_resolved["o_name"]})',
                       text_level='DEBUG', foreground_color='light cyan')
        else:
            logger.log(f'{tab}{test_case} - {tab}ref_path : {ref_resolved["path"]}', text_level='DEBUG')

        command_resolve = resolve_path(str(pathlib.Path(test_cases_path + '/' + test_case)), 'command.yaml')
        if command_resolve['path'] != command_resolve['o_path']:
            logger.log(f'{tab}{test_case} - {tab}command_path : {command_resolve["path"]}'
                       f'(resolved from __{command_resolve["o_name"]})',
                       text_level='DEBUG', foreground_color='light cyan')
        else:
            logger.log(f'{tab}{test_case} - {tab}command_path : {command_resolve["path"]}', text_level='DEBUG')
        command_yaml = yaml.load(open(file=command_resolve['path'], mode='r'), Loader=yaml.FullLoader)

        test_files = [
            'SgaCDRViewer.ini',
            'testFilter.CdrFilt',
            'Sga_CDR-QueryServer.ini',
            'SgaAutho.ini',
            'SgaAutho.pwd',
            'SgaAutho.pwl',
            'sl.dat'
        ]
        for f_i in range(len(test_files)):
            test_files[f_i] = resolve_path(str(pathlib.Path(test_cases_path + '/' + test_case)), test_files[f_i])
            if test_files[f_i]['path'] != test_files[f_i]['o_path']:
                logger.log(f'{tab}{test_case} - {tab}test_file: {test_files[f_i]["path"]}'
                           f'(resolved from __{test_files[f_i]["o_name"]})',
                           text_level='DEBUG', foreground_color='light cyan')
            else:
                logger.log(f'{tab}{test_case} - {tab}test_file : {test_files[f_i]["path"]}', text_level='DEBUG')

        logger.log(f'{tab}{test_case} - parameters:', text_level='DEBUG', foreground_color='light blue')
        default_parameters = {
            'user': 'bssap',
            'password': 'Bssap01',
            'reason': 'testing',
            'log': str(pathlib.Path(out_resolved['path'] + '/' + 'log.log')),
            'filter': str(pathlib.Path(bin_path + '/' + 'testFilter.CdrFilt')),
            'out_type': 'txt',
            'out': str(pathlib.Path(out_resolved['path'] + '/' + 'out.txt'))
        }
        command_list = []
        for parameter in command_yaml['parameters']:
            for key in parameter:
                if parameter[key].startswith('{{') and parameter[key].endswith('}}'):
                    parameter[key] = parameter[key][2:-2].strip()
                    parameter[key] = eval(parameter[key])
                command_list.append(f'-{key}')
                command_list.append(parameter[key])
                logger.log(f'{tab}{test_case} - {tab}{key} : {parameter[key]}', text_level='DEBUG')

        if "description" in command_yaml:
            logger.log(f'{tab}{test_case} - {command_yaml["description"]}', text_level='INFO',
                       foreground_color='light blue')

        logger.log(f'{tab}{test_case} - start testing...', text_level='INFO', foreground_color='light blue')

        # delete previous testing out directory and create the actual
        if os.path.exists(out_resolved['path']):
            shutil.rmtree(out_resolved['path'])
        os.makedirs(out_resolved['path'])
        if os.path.exists(debug_resolved['path']):
            shutil.rmtree(debug_resolved['path'])
        os.makedirs(debug_resolved['path'])
        logger.log(f'{tab}{test_case} - clean out_path', text_level='DEBUG', foreground_color='light blue')

        # remove previous test_files from bin and copy new ones
        for file in test_files:
            bin_file = str(pathlib.Path(bin_path + '/' + file['o_name']))
            if os.path.exists(bin_file):
                os.remove(bin_file)
            shutil.copy2(file['path'], bin_file)
        logger.log(f'{tab}{test_case} - replace test_files in bin_path', text_level='DEBUG',
                   foreground_color='light blue')

        # start cterm interface
        cterm_name = 'cterm'
        os.chdir(bin_path)
        # cterm = CtermInterface(app=f'{cterm_name}.exe', path=bin_path, logger=logger)
        cterm = CtermInterface(app=f'{cterm_name}.exe', path=bin_path)
        os.chdir(program_path)

        # start sgaautho
        sgaautho_name = 'SgaAutho'
        sgaautho_logs = [p for p in pathlib.Path(bin_path).rglob(f'{sgaautho_name}*.log')]
        for log in sgaautho_logs:
            os.remove(str(log))
        sgaautho_ini_file = str(pathlib.Path(bin_path + '/' + f'{sgaautho_name}.ini'))
        sgaautho_ini = read_ini_file(sgaautho_ini_file)
        sgaautho_ini = modify_ini_content(ini_content=sgaautho_ini, section='Advanced', parameter='sLogFilesPath',
                                          value='.')
        write_ini_file(sgaautho_ini, sgaautho_ini_file)
        sgaautho = ControlSgaAutho(cterm_interface=cterm, path=bin_path, app=f'{sgaautho_name}.exe', logger=logger)
        sgaautho = ControlSgaAutho(cterm_interface=cterm, path=bin_path, app=f'{sgaautho_name}.exe')
        sgaautho.start()
        logger.log(f'{tab}{test_case} - start {sgaautho_name}', text_level='DEBUG', foreground_color='light blue')

        # start sgacdrqueryserver
        sgacdrqueryserver_name = 'Sga_CDR-QueryServer'
        sgacdrqueryserver_logs = [p for p in pathlib.Path(bin_path).rglob(f'{sgacdrqueryserver_name}*.log')]
        for log in sgacdrqueryserver_logs:
            os.remove(str(log))
        sgacdrqueryserver_ini_file = str(pathlib.Path(bin_path + '/' + f'{sgacdrqueryserver_name}.ini'))
        sgacdrqueryserver_ini = read_ini_file(sgacdrqueryserver_ini_file)
        sgacdrqueryserver_ini = modify_ini_content(ini_content=sgacdrqueryserver_ini, section='Advanced',
                                                   parameter='sLogFilesPath', value='.')
        sgacdrqueryserver_ini = modify_ini_content(ini_content=sgacdrqueryserver_ini, section='DAT files',
                                                   parameter='sPath_mod0', value=str(in_resolved['path']))
        sgacdrqueryserver_ini = modify_ini_content(ini_content=sgacdrqueryserver_ini, section='INDEX files',
                                                   parameter='sPath_mod0', value=str(in_resolved['path']))
        write_ini_file(sgacdrqueryserver_ini, sgacdrqueryserver_ini_file)
        # sgacdrqueryserver = ControlSgaCDRQueryServer(cterm_interface=cterm, path=bin_path,
        #                                              app=f'{sgacdrqueryserver_name}.exe', logger=logger)
        sgacdrqueryserver = ControlSgaCDRQueryServer(cterm_interface=cterm, path=bin_path,
                                                     app=f'{sgacdrqueryserver_name}.exe')
        sgacdrqueryserver.start()
        logger.log(f'{tab}{test_case} - start {sgacdrqueryserver_name}', text_level='DEBUG',
                   foreground_color='light blue')

        # start sgacdrviewer
        sgacdrviewer_name = 'SgaCDRViewer'
        sgacdrviewer = str(pathlib.Path(bin_path + '/' + sgacdrviewer_name + '.exe'))
        # cterm.command('pcall', sgacdrviewer, *command_list)
        command_list.insert(0, sgacdrviewer)
        process = subprocess.Popen(command_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()

        # stop sgacdrqueryserver
        sgacdrqueryserver.stop()
        sgacdrqueryserver_logs = [p for p in pathlib.Path(bin_path).rglob(f'{sgacdrqueryserver_name}*.log')]
        for log in sgacdrqueryserver_logs:
            debug_file = str(pathlib.Path(debug_resolved['path'] + '/' + log.name))
            shutil.move(str(log), debug_file)
        logger.log(f'{tab}{test_case} - stop {sgacdrqueryserver_name}', text_level='DEBUG',
                   foreground_color='light blue')

        # stop sgaautho
        sgaautho.stop()
        sgaautho_logs = [p for p in pathlib.Path(bin_path).rglob(f'{sgaautho_name}*.log')]
        for log in sgaautho_logs:
            debug_file = str(pathlib.Path(debug_resolved['path'] + '/' + log.name))
            shutil.move(str(log), debug_file)
        logger.log(f'{tab}{test_case} - stop {sgaautho_name}', text_level='DEBUG', foreground_color='light blue')

        # move test_files from bin to debug folder
        for file in test_files:
            bin_file = str(pathlib.Path(bin_path + '/' + file['o_name']))
            debug_file = str(pathlib.Path(debug_resolved['path'] + '/' + file['o_name']))
            if os.path.exists(bin_file):
                shutil.move(bin_file, debug_file)
        logger.log(f'{tab}{test_case} - move test_files from bin_path to test_case_debug_path', text_level='DEBUG',
                   foreground_color='light blue')

        # validate
        test_case_passed = 0
        test_case_failed = 0
        for file in os.listdir(out_resolved["path"]):
            out_file = pathlib.Path(out_resolved["path"] + '/' + file)
            ref_file = pathlib.Path(ref_resolved["path"] + '/' + file)
            if os.path.exists(ref_file):
                if pathlib.Path(out_file).suffix == '.log':
                    out_file_content = None
                    ref_file_content = None
                    try:
                        with open(out_file, 'r') as out_file_handler:
                            out_file_content = out_file_handler.read()
                    finally:
                        out_file_handler.close()
                    try:
                        with open(ref_file, 'r') as ref_file_handler:
                            ref_file_content = ref_file_handler.read()
                    finally:
                        ref_file_handler.close()
                    date1_regex = r"\d{4}.\d{2}.\d{2} \d{2}:\d{2}:\d{2}"
                    date2_regex = r"\d{4}.\d{2}.\d{2}. \d{2}:\d{2}:\d{2}"
                    replace_string = "2000.01.01 00:00:00"
                    out_file_content = re.sub(date1_regex, replace_string, out_file_content, 0)
                    out_file_content = re.sub(date2_regex, replace_string, out_file_content, 0)
                    ref_file_content = re.sub(date1_regex, replace_string, ref_file_content, 0)
                    ref_file_content = re.sub(date2_regex, replace_string, ref_file_content, 0)
                    if out_file_content.strip() == ref_file_content.strip():
                        test_case_passed += 1
                        logger.log(f'{tab}{test_case} - {tab}{file}: PASSED', text_level='INFO',
                                   foreground_color='light green')
                    else:
                        test_case_failed += 1
                        logger.log(f'{tab}{test_case} - {tab}{file}: FAILED (FILE CONTENT)', text_level='ERROR',
                                   foreground_color='light red')
                else:
                    if filecmp.cmp(out_file, ref_file):
                        test_case_passed += 1
                        logger.log(f'{tab}{test_case} - {tab}{file}: PASSED', text_level='INFO',
                                   foreground_color='light green')
                    else:
                        test_case_failed += 1
                        logger.log(f'{tab}{test_case} - {tab}{file}: FAILED (FILE CONTENT)', text_level='ERROR',
                                   foreground_color='light red')
            else:
                test_case_failed += 1
                logger.log(f'{tab}{test_case} - {tab}{file}: FAILED (REF FILE DOES NOT EXISTS)', text_level='ERROR',
                           foreground_color='light red')
        for file in os.listdir(ref_resolved["path"]):
            out_file = pathlib.Path(out_resolved["path"] + '/' + file)
            if not os.path.exists(out_file):
                test_case_failed += 1
                logger.log(f'{tab}{test_case} - {tab}{file}: FAILED (OUT FILE DOES NOT EXISTS)', text_level='ERROR',
                           foreground_color='light red')

        if test_case_passed == 0 and test_case_failed == 0:
            unstable += 1
            logger.log(f'{tab}{test_case} - end testing: PASSED: {test_case_passed} - FAILED: {test_case_failed}',
                       text_level='WARNING', foreground_color='yellow')
        elif test_case_passed > 0 and test_case_failed == 0:
            passed += 1
            logger.log(f'{tab}{test_case} - end testing: PASSED: {test_case_passed} - FAILED: {test_case_failed}',
                       text_level='INFO', foreground_color='light green')
        else:
            failed += 1
            logger.log(f'{tab}{test_case} - end testing: PASSED: {test_case_passed} - FAILED: {test_case_failed}',
                       text_level='ERROR', foreground_color='light red')

    if passed == 0 and failed == 0 and unstable >= 0:
        logger.log(f'end testing: PASSED: {passed} - FAILED: {failed}', text_level='WARNING', foreground_color='yellow')
        logger.log(f'exit status: UNSTABLE', text_level='WARNING', foreground_color='yellow')
        exit(3)
    elif passed > 0 and failed == 0 and unstable == 0:
        logger.log(f'end testing: PASSED: {passed} - FAILED: {failed}', text_level='INFO',
                   foreground_color='light green')
        logger.log(f'exit status: SUCCESS', text_level='INFO', foreground_color='light green')
        exit(0)
    else:
        logger.log(f'end testing: PASSED: {passed} - FAILED: {failed}', text_level='ERROR',
                   foreground_color='light red')
        logger.log(f'exit status: FAILURE', text_level='ERROR', foreground_color='light red')
        exit(2)

except Exception as e:
    logger.log('{}: unexpected error: {}'.format(e.__class__.__name__, e),
               text_level='CRITICAL', foreground_color='light red')
    logger.log(f'exit status: UNEXPECTED FAILURE', text_level='CRITICAL', foreground_color='light red')
    exit(1)

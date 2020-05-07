import yaml
import jinja2.ext
import shutil
import os
import socket
import contextlib
import argparse

import sys
import pathlib
import platform

program_path = pathlib.Path(__file__).absolute()
program_lib_path = pathlib.Path.joinpath(program_path.parent, '../lib').resolve()
program_version = '0.0.1'
program_platform = platform.system()
sys.path.append(str(program_lib_path))

from cterm import CtermInterface
from app.cross_platform_qt_app import Control
from tools.logging_tools.logger import Logger


def parse_args():
    parser = argparse.ArgumentParser(description='generate func_test from template',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-c', '--config',
                        help='config',
                        required=True)

    parser.add_argument('-t', '--test_dir',
                        help='test_dir',
                        default='../test')
    parser.add_argument('-l', '--lib_dir',
                        help='lib_dir',
                        default='../lib')

    parser.add_argument('-bd', '--bin_dir',
                        help='bin_dir',
                        default='../../bin')

    parser.add_argument('-cd', '--contrib_dir',
                        help='contrib_dir',
                        default='../../contrib')

    parser.add_argument('--no_create_dirs',
                        help='no_create_dirs',
                        action="store_false",
                        default=True)
    parser.add_argument('--no_create_default_ini',
                        help='no_create_default_ini',
                        action="store_false",
                        default=True)

    parser.add_argument('-rl', '--report_level',
                        help='report_level',
                        choices=['VERBOSE', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO')

    parser.add_argument('--recreate_default_ini',
                        help='recreate_default_ini',
                        action="store_true",
                        default=False)

    args = parser.parse_args()

    return args


# subroutines

def resolve_path(*args):
    if len(args) > 1:
        return pathlib.Path.joinpath(*args).resolve()
    else:
        return pathlib.Path(*args).resolve()


def find_free_port():
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('localhost', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return str(s.getsockname()[1])


def create_env_dir():
    env_dir.mkdir(parents=True, exist_ok=True)
    logger.info('check env_dir: {}'.format(env_dir))


def create_default_ini():
    ini_dir = resolve_path(env_dir, yaml_config['app']['ini']['dir'])
    ini_dir.mkdir(parents=True, exist_ok=True)
    logger.info('check ini_dir: {}'.format(ini_dir))
    default_ini = resolve_path(ini_dir, yaml_config['app']['name'] + '.ini')
    if not default_ini.exists() or args.recreate_default_ini:
        app_dir = resolve_path(test_dir, args.bin_dir)
        logger.debug('app_dir: {}'.format(app_dir))
        for i in range(len(yaml_config['app']['platforms'])):
            if program_platform != yaml_config['app']['platforms'][i]['platform']:
                continue
            necessary_components = [
                resolve_path(app_dir, yaml_config['app']['platforms'][i]['executable'])
            ]
            for item in yaml_config['app']['platforms'][i]['necessary_components']:
                necessary_components.append(resolve_path(app_dir, item))
            tmp_bin_dir = resolve_path(ini_dir, 'tmp')
            tmp_bin_dir.mkdir(parents=True, exist_ok=True)
            logger.debug('tmp_bin_dir: {}'.format(tmp_bin_dir))
            for item in necessary_components:
                shutil.copy2(item, tmp_bin_dir)
                logger.debug('shutil.copy2({}, {})'.format(item, tmp_bin_dir))
            try:
                os.chdir(tmp_bin_dir)
                cterm_interface = CtermInterface(cterm=resolve_path(app_dir, 'cterm.exe'))
                app = Control(cterm_interface=cterm_interface, ip='127.0.0.1', port=find_free_port(),
                              app=resolve_path(tmp_bin_dir, yaml_config['app']['platforms'][i]['executable']))
                app.start()
                app.save_config()
                app.stop()
                del app
                del cterm_interface
            except Exception as e:
                raise Exception(e)
            finally:
                os.chdir(program_path.parent)
            shutil.copy2(
                resolve_path(tmp_bin_dir, resolve_path(yaml_config['app']['platforms'][i]['executable']).stem + '.ini'),
                default_ini)
            logger.debug('shutil.copy2({}, {})'.format(
                resolve_path(tmp_bin_dir, resolve_path(yaml_config['app']['platforms'][i]['executable']).stem + '.ini'),
                default_ini))
            shutil.rmtree(tmp_bin_dir)
            logger.debug('shutil.rmtree({})'.format(tmp_bin_dir))
            break
    logger.info('check default_ini: {}'.format(default_ini))


def check_multiplatform_elements():
    executable_exists = None
    cterm_exists = None
    adg_exists = None
    for i in range(len(yaml_config['app']['platforms'])):
        if i == 0:
            executable_exists = False
            if 'executable' in yaml_config['app']['platforms'][i]:
                executable_exists = True
            cterm_exists = False
            if 'cterm' in yaml_config['app']['platforms'][i]['utilities']:
                cterm_exists = True
            adg_exists = False
            if 'adg' in yaml_config['app']['platforms'][i]['utilities']:
                adg_exists = True
        else:
            assert executable_exists == ('executable' in yaml_config['app']['platforms'][i]), \
                'multiplatform items do not match'
            assert cterm_exists == ('cterm' in yaml_config['app']['platforms'][i]['utilities']), \
                'multiplatform items do not match'
            assert adg_exists == ('adg' in yaml_config['app']['platforms'][i]['utilities']), \
                'multiplatform items do not match'


def preprocessing__app_test__processing__in_uri():
    tmp_in_uris = yaml_config['app_test']['processing']['in_uri']

    if tmp_in_uris != 'None':
        for in_uri in tmp_in_uris[:]:
            if in_uri.startswith('file-'):
                tmp = in_uri.split('-')[1]

                tmp = tmp.split('://')
                suffix = [tmp[0]]
                if len(in_uris) == 0:
                    suffix = tmp[0].split('|')
                tmp = tmp[1]

                tmp = tmp.split('/testFile?')
                path = tmp[0]
                tmp = tmp[1]

                params = tmp.split('&')
                searching = False
                searching_paths = None
                optional = False
                for param in params[:]:
                    if param.startswith('name='):
                        param_index = params.index(param)
                        param = param.replace('uriDir', 'input')
                        param = param.replace('uriIndex', str(len(in_uris)))
                        params[param_index] = param
                    elif param.startswith('searching='):
                        tmp_param = param.split('=')
                        if tmp_param[1] != 'False':
                            searching = True
                            searching_paths = tmp_param[1].split('|')
                            params.remove(param)
                    elif param.startswith('optional='):
                        tmp_param = param.split('=')
                        if tmp_param[1] == 'True':
                            optional = True
                        params.remove(param)

                in_uri = {
                    'path': path,
                    'suffix': suffix,
                    'params': '&'.join(params),
                    'searching': searching,
                    'searching_paths': searching_paths,
                    'optional': optional
                }

                if in_uri not in in_uris:
                    in_uris.append(in_uri)
            else:
                raise Exception('not handled input format: {}'.format(in_uri))


def preprocessing__app_test__processing__out_uri():
    tmp_out_uris = yaml_config['app_test']['processing']['out_uri']

    if tmp_out_uris != 'None':
        for out_uri in tmp_out_uris[:]:
            if out_uri.startswith('file-'):
                tmp = out_uri.split('-', 1)[1]

                tmp = tmp.split('://')
                suffix = tmp[0]
                tmp = tmp[1]

                tmp = tmp.split('/testFile?')
                path = tmp[0]
                tmp = tmp[1]

                params = tmp.split('&')
                validate = True
                debug = True
                for param in params[:]:
                    if param.startswith('name='):
                        param_index = params.index(param)
                        param = param.replace('uriDir', 'output')
                        param = param.replace('uriIndex', str(len(out_uris)))
                        params[param_index] = param
                    elif param.startswith('validate='):
                        tmp_param = param.split('=')
                        if tmp_param[1] == 'False':
                            validate = False
                        params.remove(param)
                    elif param.startswith('debug='):
                        tmp_param = param.split('=')
                        if tmp_param[1] == 'False':
                            debug = False
                        params.remove(param)

                out_uri = {
                    'path': path,
                    'suffix': suffix,
                    'params': '&'.join(params),
                    'validate': validate,
                    'debug': debug
                }

                if out_uri not in out_uris:
                    out_uris.append(out_uri)
            else:
                raise Exception('not handled output format: {}'.format(out_uri))


def preprocessing__app_test__app_config__ini_config__file():
    ini_config__files = yaml_config['app_test']['app_config']['ini_config']['file']

    if ini_config__files != 'None':
        for ini_config__file in ini_config__files[:]:

            # har
            if ini_config__file.startswith("'S1APGeo', 'CsvName'"):
                assert ini_config__file == "'S1APGeo', 'CsvName', testFile", \
                    'app_test.app_config.ini_config.file got: {}, expected: {}'.format(
                        ini_config__file,
                        "'S1APGeo', 'CsvName', testFile")
                ini_config__files.remove(ini_config__file)
            if ini_config__file.startswith("'S1APGeo', 'CsvDir'"):
                path = ini_config__file.split(', ')[2]
                path = path.strip("'")
                assert path.startswith('_out'), \
                    'app_test.app_config.ini_config.file got: {}, expected: {}'.format(
                        ini_config__file,
                        "'S1APGeo', 'CsvDir', '_out...'")
                ini_config__files.remove(ini_config__file)
                out_geo_csv = {
                    'path': path,
                    'suffix': 'csv'
                }
                if out_geo_csv not in out_geo_csvs:
                    out_geo_csvs.append(out_geo_csv)

    if len(yaml_config['app_test']['app_config']['ini_config']['file']) == 0:
        del yaml_config['app_test']['app_config']['ini_config']['file']


def preprocessing__app_test__app_config__runtime_config__file():
    runtime_config__files = yaml_config['app_test']['app_config']['runtime_config']['file']

    if runtime_config__files != 'None':
        for runtime_config__file in runtime_config__files[:]:

            # cdr
            if runtime_config__file.startswith("'CDR', 'DataPathPrimary'") \
                    or runtime_config__file.startswith("'CDR', 'IndexPath'") \
                    or runtime_config__file.startswith("'S1APCDRWriter', 'DataPathPrimary'") \
                    or runtime_config__file.startswith("'S1APCDRWriter', 'IndexPath'") \
                    or runtime_config__file.startswith("'SIPCDRWriter', 'DataPathPrimary'") \
                    or runtime_config__file.startswith("'SIPCDRWriter', 'IndexPath'"):
                sec, par, path = runtime_config__file.split(', ')
                sec = sec.strip("'")
                par = par.strip("'")
                path = path.strip("'")
                assert path.startswith('_out') and path.endswith('testFile'), \
                    'app_test.app_config.runtime_config.file got: {}, expected: {}'.format(
                        runtime_config__file,
                        "'CDR/S1APCDRWriter/SIPCDRWriter', 'DataPathPrimary/IndexPath', '_out/.../testFile'")
                path = path.split('/testFile')[0]
                runtime_config__files.remove(runtime_config__file)
                out_cdr = {
                    'path': path,
                    'type': sec
                }
                if out_cdr not in out_cdrs:
                    assert len(out_cdrs) == 0, \
                        'app_test.app_config.runtime_config.file CDR/S1APCDRWriter/SIPCDRWriter/DataPathPrimary-CDR/IndexPath does not equal'
                    out_cdrs.append(out_cdr)

            # har
            if runtime_config__file.startswith("'S1APHARWriterRuntime', 'HAROutputBaseName'"):
                assert runtime_config__file == "'S1APHARWriterRuntime', 'HAROutputBaseName', testFile", \
                    'app_test.app_config.runtime_config.file got: {}, expected: {}'.format(
                        runtime_config__file,
                        "'S1APHARWriterRuntime', 'HAROutputBaseName', testFile")
                runtime_config__files.remove(runtime_config__file)
            if runtime_config__file.startswith("'S1APHARWriterRuntime', 'HAROutputDir'"):
                path = runtime_config__file.split(', ')[2]
                path = path.strip("'")
                assert path.startswith('_out'), \
                    'app_test.app_config.runtime_config.file got: {}, expected: {}'.format(
                        runtime_config__file,
                        "'S1APHARWriterRuntime', 'HAROutputDir', '_out...'")
                runtime_config__files.remove(runtime_config__file)
                out_har = {
                    'path': path,
                    'suffix': '001'
                }
                if out_har not in out_hars:
                    out_hars.append(out_har)

            # s1ap_dump
            if runtime_config__file.startswith("'S1APAssembler', 'DumpFile'"):
                path = runtime_config__file.split(', ')[2]
                path = path.strip("'")
                assert path.startswith('_out') and path.endswith('testFile'), \
                    'app_test.app_config.runtime_config.file got: {}, expected: {}'.format(
                        runtime_config__file,
                        "'S1APAssembler', 'DumpFile', '_out/.../testFile'")
                path = path.split('/testFile')[0]
                runtime_config__files.remove(runtime_config__file)
                out_s1ap_dump = {
                    'path': path,
                    'suffix': 's1ap'
                }
                if out_s1ap_dump not in out_s1ap_dumps:
                    out_s1ap_dumps.append(out_s1ap_dump)

    if len(yaml_config['app_test']['app_config']['runtime_config']['file']) == 0:
        del yaml_config['app_test']['app_config']['runtime_config']['file']


def create_dirs():
    in_dirs = list()
    out_dirs = list()
    ref_dirs = list()

    # in
    for in_uri in in_uris:
        test_file_dir = resolve_path(env_dir, in_uri['path'])
        if test_file_dir not in in_dirs:
            in_dirs.append(test_file_dir)
            test_file_dir.mkdir(parents=True, exist_ok=True)
            dir_link_path = resolve_path(test_file_dir, '_path_links.cfg')
            if in_uri['searching']:
                try:
                    file = open(dir_link_path, 'w')
                    for searching_path in in_uri['searching_paths']:
                        file.write(searching_path + '\n')
                except Exception as e:
                    raise Exception(e)
                finally:
                    file.close()
            else:
                if dir_link_path.exists():
                    dir_link_path.unlink()

    if 'preprocessing' in yaml_config['app_test']['processing']:
        if 'in_preprocessing' in yaml_config['app_test']['processing']['preprocessing']:
            if yaml_config['app_test']['processing']['preprocessing']['in_preprocessing'] != "None":
                test_file_dir = resolve_path(env_dir, eval(yaml_config['app_test']['processing']['preprocessing']['in_preprocessing'])['path'])
                if test_file_dir not in in_dirs:
                    in_dirs.append(test_file_dir)

    # out
    for out_case in out_uris + out_cdrs + out_hars + out_s1ap_dumps + out_geo_csvs:
        test_file_dir = resolve_path(env_dir, out_case['path'])
        if test_file_dir not in out_dirs:
            out_dirs.append(test_file_dir)
        ref_file_dir = resolve_path(env_dir, '_ref' + out_case['path'])
        if ref_file_dir not in ref_dirs:
            ref_dirs.append(ref_file_dir)

    if 'postprocessing' in yaml_config['app_test']['processing']:
        if 'out_postprocessing' in yaml_config['app_test']['processing']['postprocessing']:
            if yaml_config['app_test']['processing']['postprocessing']['out_postprocessing'] != "None":
                for out_postprocessing in eval(yaml_config['app_test']['processing']['postprocessing']['out_postprocessing']):
                    test_file_dir = resolve_path(env_dir, out_postprocessing['path'])
                    if test_file_dir not in in_dirs:
                        out_dirs.append(test_file_dir)
                    ref_file_dir = resolve_path(env_dir, '_ref' + out_postprocessing['path'])
                    if ref_file_dir not in ref_dirs:
                        ref_dirs.append(ref_file_dir)

    for test_file_dir in in_dirs + out_dirs + ref_dirs:
        test_file_dir.mkdir(parents=True, exist_ok=True)
        logger.info('check test_file_dir: {}'.format(test_file_dir))


# main

args = parse_args()

logger = Logger(name=program_path.stem, level=args.report_level)

# load yaml_config_file

test_dir = resolve_path(program_path.parent, args.test_dir)
try:
    file = open(resolve_path(test_dir, 'vars.cfg'), 'w')
    file_content = "bin {}\ncontrib {}".format(args.bin_dir, args.contrib_dir)
    file.write(file_content + '\n')
except Exception as e:
    raise Exception(e)
finally:
    file.close()

yaml_config_file = args.config


class NullUndefined(jinja2.Undefined):
    def __getattr__(self, key):
        return ''


yaml_template = jinja2.Template(str(yaml.load(open(file=yaml_config_file, mode='r'), Loader=yaml.FullLoader)),
                                undefined=NullUndefined)
yaml_config = yaml.safe_load(yaml_template.render(yaml.safe_load(yaml_template.render())))

# preprocessing yaml_config_file

if len(yaml_config['app']['platforms']) > 1:
    check_multiplatform_elements()

in_uris = list()
out_uris = list()
out_cdrs = list()
out_geo_csvs = list()
out_hars = list()
out_s1ap_dumps = list()

preprocessing__app_test__processing__in_uri()
preprocessing__app_test__processing__out_uri()
preprocessing__app_test__app_config__ini_config__file()
preprocessing__app_test__app_config__runtime_config__file()

# check environment

env_dir = resolve_path(test_dir, yaml_config['env']['dir'])
create_env_dir()

create_default_ini()

create_dirs()

# generate template

jinja2_file_loader = jinja2.FileSystemLoader('temp-func_test')

jinja2_env = jinja2.Environment(loader=jinja2_file_loader,
                                extensions=['jinja2.ext.do', 'jinja2.ext.loopcontrols', 'jinja2.ext.debug'],
                                trim_blocks=False,
                                lstrip_blocks=False,
                                keep_trailing_newline=True)
jinja2_template = jinja2_env.get_template('temp-func_test.j2')

test_file_content = jinja2_template.render(config=yaml_config,
                                           in_uris=in_uris,
                                           out_uris=out_uris,
                                           out_cdrs=out_cdrs,
                                           out_geo_csvs=out_geo_csvs,
                                           out_hars=out_hars,
                                           out_s1ap_dumps=out_s1ap_dumps)
test_file_content = test_file_content.replace('# j2-temp #\n', '')
test_file_content = test_file_content.replace('# j2-temp #', '')
# print('test_file_content: {}'.format(test_file_content))

# write template

test_file = resolve_path(env_dir, 'func_test.py')
test_file_handler = open(test_file, 'w')
test_file_handler.write(test_file_content + '\n')
test_file_handler.close
logger.info('check test_file: {}'.format(test_file))

# write summary template

func_tests = list()
for config in resolve_path(yaml_config_file).parent.iterdir():
    func_tests.append('processes.append' + "('" + config.stem.split('.')[-1] + '/func_test.py' + "')")
func_tests = '\n'.join(func_tests)

if yaml_config['env']['name'] != "":
    path = resolve_path(test_dir, yaml_config['env']['dir']).parent
    summary_file = resolve_path(path, 'func_test.py')

    summary_file_content = """import sys
import subprocess
\n\ndef processing():
    global exit_code
    for process in processes:
        ans = subprocess.call(['python',r'{}'.format(process), *sys.argv[1:]])
        if ans != 0:
            if exit_code != 0:
                if ans < exit_code:
                    exit_code = ans
            else:
                exit_code = ans
    exit(exit_code)
\n\nexit_code = 0
processes = list()
{}
processing()""".format('{}', func_tests)

    try:
        file = open(summary_file, 'w')
        file.write(summary_file_content + '\n')
    except Exception as e:
        raise Exception(e)
    finally:
        file.close()

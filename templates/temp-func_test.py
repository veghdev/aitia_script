import re
import yaml
import jinja2
import shutil
import os
import socket
import contextlib

import sys
import pathlib
import platform

program_path = pathlib.Path(__file__)
program_lib_path = pathlib.Path(program_path.parent, '../lib').resolve()
program_version = '0.0.1'
program_platform = platform.system()
sys.path.append(str(program_lib_path))

from cterm import CtermInterface
from app.cross_platform_qt_app import Control
from tools.logging_tools.logger import Logger


# variables

yaml_config_file = 'config-func_test.yaml'
test_dir = pathlib.Path(program_path.parent, '../test')

recreate_default_ini = False
recreate_test_file = True


# subroutines

def find_free_port():
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('localhost', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return str(s.getsockname()[1])


def create_env_dir():
    env_dir.mkdir(parents=True, exist_ok=True)
    logger.info('check env_dir: {}'.format(env_dir))


def create_default_ini():
    ini_dir = pathlib.Path.joinpath(env_dir, yaml_config['app']['ini']['dir']).resolve()
    ini_dir.mkdir(parents=True, exist_ok=True)
    logger.info('check ini_dir: {}'.format(ini_dir))
    default_ini = pathlib.Path.joinpath(ini_dir, yaml_config['app']['name'] + '.ini').resolve()
    if not default_ini.exists() or recreate_default_ini:
        app_dir = pathlib.Path.joinpath(env_dir, yaml_config['app']['dir']).resolve()
        logger.debug('app_dir: {}'.format(app_dir))
        for i in range(len(yaml_config['app']['platforms'])):
            if program_platform != yaml_config['app']['platforms'][i]['platform']:
                continue
            necessary_components = [
                pathlib.Path.joinpath(app_dir, yaml_config['app']['platforms'][i]['executable']).resolve()
            ]
            for item in yaml_config['app']['platforms'][i]['necessary_components']:
                necessary_components.append(pathlib.Path.joinpath(app_dir, item).resolve())
            tmp_bin_dir = pathlib.Path.joinpath(ini_dir, 'tmp').resolve()
            tmp_bin_dir.mkdir(parents=True, exist_ok=True)
            logger.debug('tmp_bin_dir: {}'.format(tmp_bin_dir))
            for item in necessary_components:
                shutil.copy2(item, tmp_bin_dir)
                logger.debug('shutil.copy2({}, {})'.format(item, tmp_bin_dir))
            try:
                os.chdir(tmp_bin_dir)
                cterm_interface = CtermInterface(cterm=pathlib.Path.joinpath(app_dir, 'cterm.exe').resolve())
                app = Control(cterm_interface=cterm_interface, ip='127.0.0.1', port=find_free_port(),
                              app=pathlib.Path.joinpath(tmp_bin_dir,
                                                        yaml_config['app']['platforms'][i]['executable']).resolve())
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
                pathlib.Path.joinpath(
                    tmp_bin_dir,
                    pathlib.Path(yaml_config['app']['platforms'][i]['executable']).stem + '.ini').resolve(),
                default_ini)
            logger.debug('shutil.copy2({}, {})'.format(
                pathlib.Path.joinpath(
                    tmp_bin_dir,
                    pathlib.Path(yaml_config['app']['platforms'][i]['executable']).stem + '.ini').resolve(),
                default_ini))
            shutil.rmtree(tmp_bin_dir)
            logger.debug('shutil.rmtree({})'.format(tmp_bin_dir))
            break
    logger.info('check default_ini: {}'.format(default_ini))


def check_multiplatform():
    if len(yaml_config['app']['platforms']) > 1:
        # check items
        executable_exists = None
        ext_cterm_exists = None
        ext_adg_exists = None
        for i in range(len(yaml_config['app']['platforms'])):
            if i == 0:
                executable_exists = False
                if 'executable' in yaml_config['app']['platforms'][i]:
                    executable_exists = True
                ext_cterm_exists = False
                if 'cterm' in yaml_config['app']['platforms'][i]['ext']:
                    ext_cterm_exists = True
                ext_adg_exists = False
                if 'adg' in yaml_config['app']['platforms'][i]['ext']:
                    ext_adg_exists = True
            else:
                assert executable_exists == ('executable' in yaml_config['app']['platforms'][i]), \
                    'multiplatform items do not match'
                assert ext_cterm_exists == ('cterm' in yaml_config['app']['platforms'][i]['ext']), \
                    'multiplatform items do not match'
                assert ext_adg_exists == ('adg' in yaml_config['app']['platforms'][i]['ext']), \
                    'multiplatform items do not match'
        return True
    return False


def preprocess_uri_section(uri_section):
    processed_uri_section = {
        'input': list(),
        'output': list()
    }

    for uri in uri_section:
        assert uri.startswith('file-'), \
            'parsing uri({}): expected transport: "file"'.format(uri)
        tmp_uri = uri.split('-')[1]

        tmp_uri = tmp_uri.split('://')
        uri_format = tmp_uri[0]
        tmp_uri = tmp_uri[1]

        tmp_uri = tmp_uri.split('/testFile?')
        uri_dirs = tmp_uri[0].split('/')
        tmp_uri = tmp_uri[1]
        assert 0 < len(uri_dirs) < 3, \
            'parsing uri({}): expected 1-2 uri directories, but get: {} - {}'.format(uri,
                                                                                     len(uri_dirs),
                                                                                     uri_dirs)

        main_in_dirs = ['_in', '_in_tmp']
        main_out_dirs = ['_out', '_out_tmp']
        assert uri_dirs[0] in main_in_dirs or uri_dirs[0] in main_out_dirs, \
            'parsing uri({}): expected uri_main_dir: {} or {}, but get: {}'.format(uri,
                                                                                   main_in_dirs,
                                                                                   main_out_dirs,
                                                                                   uri_dirs[0])
        uri_main_dir = uri_dirs[0]
        if len(uri_dirs) == 2:
            uri_sub_dir = uri_dirs[1]
        else:
            uri_sub_dir = ''

        tmp_uri = tmp_uri.split('&')
        for i in range(len(tmp_uri)):
            param = tmp_uri[i].split('=')
            tmp_uri[i] = {param[0]: param[1]}
        uri_parameters = tmp_uri

        uri = {
            'uri_key': '{}/{}/{}'.format(uri_main_dir, uri_sub_dir, uri_format),
            'uri_format': uri_format,
            'uri_main_dir': uri_main_dir,
            'uri_sub_dir': uri_sub_dir,
            'uri_parameters': uri_parameters
        }

        if uri_main_dir in main_in_dirs:
            if uri not in processed_uri_section['input']:
                processed_uri_section['input'].append(uri)
        else:
            if uri not in processed_uri_section['output']:
                processed_uri_section['output'].append(uri)

    for i in range(len(processed_uri_section['output'])):
        searching_key = '{}/{}/{}'.format(processed_uri_section['output'][i]['uri_main_dir'],
                                          processed_uri_section['output'][i]['uri_sub_dir'],
                                          'yaml')
        generate_debug = True
        for uri in processed_uri_section['output']:
            if searching_key == uri['uri_key']:
                generate_debug = False
                break
        processed_uri_section['output'][i]['generate_debug'] = generate_debug

        validate = True
        for j in range(len(processed_uri_section['output'][i]['uri_parameters'])):
            if 'name' in processed_uri_section['output'][i]['uri_parameters'][j]:
                processed_uri_section['output'][i]['uri_parameters'][j]['name'] = \
                    processed_uri_section['output'][i]['uri_parameters'][j]['name'].replace('uriDir', 'output')
                processed_uri_section['output'][i]['uri_parameters'][j]['name'] = \
                    processed_uri_section['output'][i]['uri_parameters'][j]['name'].replace('uriIndex', str(i))
            if 'validate' in processed_uri_section['output'][i]['uri_parameters'][j]:
                validate = processed_uri_section['output'][i]['uri_parameters'][j]['validate']
        if {'validate': validate} in processed_uri_section['output'][i]['uri_parameters']:
            processed_uri_section['output'][i]['uri_parameters'].remove({'validate': validate})
        processed_uri_section['output'][i]['validate'] = validate

    for i in range(len(processed_uri_section['input'])):
        searching_ref = False
        for j in range(len(processed_uri_section['input'][i]['uri_parameters'])):
            if 'name' in processed_uri_section['input'][i]['uri_parameters'][j]:
                processed_uri_section['input'][i]['uri_parameters'][j]['name'] = \
                    processed_uri_section['input'][i]['uri_parameters'][j]['name'].replace('uriDir', 'input')
                processed_uri_section['input'][i]['uri_parameters'][j]['name'] = \
                    processed_uri_section['input'][i]['uri_parameters'][j]['name'].replace('uriIndex', str(i))
            if 'searchingRef' in processed_uri_section['input'][i]['uri_parameters'][j]:
                searching_ref = processed_uri_section['input'][i]['uri_parameters'][j]['searchingRef']
        if {'searchingRef': searching_ref} in processed_uri_section['input'][i]['uri_parameters']:
            processed_uri_section['input'][i]['uri_parameters'].remove({'searchingRef': searching_ref})
        processed_uri_section['input'][i]['searching_ref'] = searching_ref

    return processed_uri_section


def postprocess_uri_section(uri_section):
    processed_uri_section = uri_section

    for i in range(len(processed_uri_section['output'])):
        processed_uri = processed_uri_section['output'][i]
        searching_key = '{}/{}/{}'.format(processed_uri['uri_main_dir'],
                                          processed_uri['uri_sub_dir'],
                                          'yaml')
        generate_debug = True
        for uri in processed_uri_section['output']:
            if searching_key == uri['uri_key']:
                generate_debug = False
                break
        processed_uri['generate_debug'] = generate_debug

        validate = True
        for j in range(len(processed_uri['uri_parameters'])):
            if 'name' in processed_uri['uri_parameters'][j]:
                processed_uri['uri_parameters'][j]['name'] = \
                    processed_uri['uri_parameters'][j]['name'].replace('uriDir', 'output')
                processed_uri['uri_parameters'][j]['name'] = \
                    processed_uri['uri_parameters'][j]['name'].replace('uriIndex', str(i))
            if 'validate' in processed_uri['uri_parameters'][j]:
                validate = processed_uri['uri_parameters'][j]['validate']
        if {'validate': validate} in processed_uri['uri_parameters']:
            processed_uri['uri_parameters'].remove({'validate': validate})
        processed_uri['validate'] = validate

        tmp_dirs = "'{}'".format(processed_uri['uri_main_dir'])
        if processed_uri['uri_sub_dir'] != '':
            tmp_dirs = tmp_dirs + ", '{}'".format(processed_uri['uri_sub_dir'])
        tmp_dirs = "pathlib.Path.joinpath(program_path, {}, test_file_in.stem + '.{}')"\
            .format(tmp_dirs, processed_uri['uri_format'])
        processed_uri['sub_clean'] = tmp_dirs

        tmp_params = ''
        for j, param in enumerate(processed_uri['uri_parameters']):
            for key in param:
                if j != 0:
                    tmp_params = tmp_params + '&'
                tmp_params = tmp_params + '{}={}'.format(key, param[key])
        uri = "'file-{}://{}?{}'.format({})".format(
            processed_uri['uri_format'],
            "{}",
            tmp_params,
            tmp_dirs
        )
        processed_uri['sub_uri'] = uri

    for i in range(len(processed_uri_section['input'])):
        processed_uri = processed_uri_section['input'][i]
        searching_ref = False
        for j in range(len(processed_uri['uri_parameters'])):
            if 'name' in processed_uri['uri_parameters'][j]:
                processed_uri['uri_parameters'][j]['name'] = \
                    processed_uri['uri_parameters'][j]['name'].replace('uriDir', 'input')
                processed_uri['uri_parameters'][j]['name'] = \
                    processed_uri['uri_parameters'][j]['name'].replace('uriIndex', str(i))
            if 'searchingRef' in processed_uri['uri_parameters'][j]:
                searching_ref = processed_uri['uri_parameters'][j]['searchingRef']
        if {'searchingRef': searching_ref} in processed_uri['uri_parameters']:
            processed_uri['uri_parameters'].remove({'searchingRef': searching_ref})
        processed_uri['searching_ref'] = searching_ref

        tmp_dirs = "'{}'".format(processed_uri['uri_main_dir'])
        if processed_uri['uri_sub_dir'] != '':
            tmp_dirs = tmp_dirs + ", '{}'".format(processed_uri['uri_sub_dir'])
        tmp_dirs = "pathlib.Path.joinpath(program_path, {}, test_file_in.stem + '.{}')" \
            .format(tmp_dirs, processed_uri['uri_format'])

        tmp_params = ''
        for j, param in enumerate(processed_uri['uri_parameters']):
            for key in param:
                if j != 0:
                    tmp_params = tmp_params + '&'
                tmp_params = tmp_params + '{}={}'.format(key, param[key])
        uri = "'file-{}://{}?{}'.format({})".format(
            processed_uri['uri_format'],
            "{}",
            tmp_params,
            tmp_dirs
        )
        processed_uri['sub_uri'] = uri

    return processed_uri_section


# main

logger = Logger(name=program_path.stem, level='DEBUG')


# load yaml_config_file

class NullUndefined(jinja2.Undefined):
    def __getattr__(self, key):
        return ''


yaml_template = jinja2.Template(str(yaml.load(open(file=yaml_config_file, mode='r'), Loader=yaml.FullLoader)),
                                undefined=NullUndefined)
yaml_config = yaml.safe_load(yaml_template.render(yaml.safe_load(yaml_template.render())))


# preprocessing yaml_config_file

check_multiplatform()
uri_config = yaml_config['app_test']['processing']['uri']
uri_config = preprocess_uri_section(uri_config)
uri_config = postprocess_uri_section(uri_config)


# check environment

env_dir = pathlib.Path.joinpath(test_dir, yaml_config['env']['dir']).resolve()
create_env_dir()

create_default_ini()


# generate template

jinja2_file_loader = jinja2.FileSystemLoader('temp-func_test')
jinja2_env = jinja2.Environment(loader=jinja2_file_loader,
                                trim_blocks=False,
                                lstrip_blocks=False,
                                keep_trailing_newline=True)
jinja2_template = jinja2_env.get_template('temp-func_test.j2')
test_file_content = jinja2_template.render(config=yaml_config,
                                           uri_config=uri_config).replace('# j2-temp #\n', '')
# print('test_file_content: {}'.format(test_file_content))

# write template

test_file = pathlib.Path(env_dir, yaml_config['app_test']['name'] + '.py')
if not test_file.exists() or recreate_test_file:
    test_file_handler = open(test_file, 'w')
    test_file_handler.write(test_file_content + '\n')
    test_file_handler.close
logger.info('check test_file: {}'.format(test_file))

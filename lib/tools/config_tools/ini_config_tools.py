import inspect
import pathlib
import re

import logging


class Ini:

    _logger = None

    def __init__(self, ini):
        try:
            self._logger = logging.getLogger(__name__)
            self.content = ini
            if not isinstance(ini, list):
                self.file = ini
            else:
                self.file = None
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, ini):
        try:
            if isinstance(ini, pathlib.Path):
                self._content = self._read_ini_file(ini)
            elif isinstance(ini, str):
                self._content = self._read_ini_file(pathlib.Path(ini))
            elif isinstance(ini, list):
                self._content = ini
            else:
                assert False, 'unexpected argument type: {} - {} - {}'.format('ini', ini, type(ini))
            if 'verbose' in dir(self._logger):
                self._logger.verbose('content: {}'.format(self._content))
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, ini):
        try:
            if isinstance(ini, pathlib.Path):
                self._file = ini
            elif isinstance(ini, str):
                self._file = pathlib.Path(ini)
            elif ini is None:
                self._file = None
            else:
                assert False, 'unexpected argument type: {} - {} - {}'.format('ini', ini, type(ini))
            if 'verbose' in dir(self._logger):
                self._logger.verbose('file: {}'.format(self._file))
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))

    def write_content_to_file(self, file=None):
        try:
            if file is None:
                if self._file is not None:
                    file = self._file
                else:
                    assert False, 'missing property: {}'.format('file')
            fh = open(file, 'w')
            for section in self._content:
                if 'description' in section:
                    if section['description'] != '':
                        fh.write(';' + ' ' + section['description'] + '\n')
                if section['commented']:
                    fh.write(';' + ' ')
                fh.write('[' + section['name'] + ']' + '\n')
                for parameter in section['parameters']:
                    if 'description' in parameter:
                        if parameter['description'] != '':
                            fh.write(';' + ' ' + parameter['description'] + '\n')
                    if parameter['commented']:
                        fh.write(';' + ' ')
                    fh.write(parameter['name'] + '=' + parameter['value'] + '\n')
                fh.write('\n')
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))
        finally:
            fh.close()

    def set_up_parameter(self, section, parameter, value):
        try:
            index = self._get_index(section, parameter)
            ans = {
                'section': section,
                'parameter': parameter,
                'prev_value': '',
                'value': value
            }
            if index['section_index'] is not None and index['parameter_index'] is not None:
                ans['prev_value'] = self._content[index['section_index']]['parameters'][index['parameter_index']]['value']
                self._content[index['section_index']]['parameters'][index['parameter_index']]['value'] = value
            elif index['section_index'] is not None and index['parameter_index'] is None:
                self._content[index['section_index']]['parameters'].append({
                    'name': parameter,
                    'value': value,
                    'commented': False
                })
            elif index['section_index'] is None and index['parameter_index'] is None:
                parameters = list()
                parameters.append({
                    'name': parameter,
                    'value': value,
                    'commented': False
                })
                self._content.append({
                    'name': section,
                    'parameters': parameters,
                    'commented': False
                })
            return ans
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))

    def _read_ini_file(self, ini):
        try:
            fh = open(ini)
            content = []
            unlinked_comment = None
            while True:
                line = fh.readline()
                if not line:
                    break
                line = line.strip()
                # empty lines
                if line == '':
                    continue
                line_type = self._get_ini_line_type(line)
                if line.startswith(';') or line.startswith('#'):
                    line = line[1:]
                    line = line.strip()

                # sections or commented_sections
                if line_type == 'section' or line_type == 'commented_section':
                    section = {'name': re.search(r'\[(.*)\]', line).group(1)}
                    if unlinked_comment is not None:
                        section['description'] = unlinked_comment
                        unlinked_comment = None
                    section['parameters'] = []
                    if line_type == 'commented_section':
                        section['commented'] = True
                    else:
                        section['commented'] = False
                    content.append(section)
                # parameters or commented_parameters
                elif line_type == 'parameter' or line_type == 'commented_parameter':
                    assert len(content) != 0, 'unexpected line: {}'.format(line)
                    parameter = {'name': re.search(r'(.*)=(.*)', line).group(1)}
                    if unlinked_comment is not None:
                        parameter['description'] = unlinked_comment
                        unlinked_comment = None
                    parameter['value'] = re.search(r'(.*)=(.*)', line).group(2)
                    if line_type == 'commented_parameter':
                        parameter['commented'] = True
                    else:
                        parameter['commented'] = False
                    content[-1]['parameters'].append(parameter)
                # comments
                elif line_type == 'comment':
                    unlinked_comment = line
                else:
                    assert False, 'unexpexted line type: {} - {}'.format(line, line_type)
            return content
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))
        finally:
            fh.close()

    def _get_ini_line_type(self, line):
        try:
            if line.startswith(';') or line.startswith('#'):
                line = line[1:]
                line = line.strip()
                if re.search(r'\[(.*)\]', line) and line.startswith('['):
                    return 'commented_section'
                elif re.search(r'(.*)=(.*)', line) and ' ' not in re.search(r'(.*)=(.*)', line).group(1):
                    return 'commented_parameter'
                else:
                    return 'comment'
            else:
                if re.search(r'\[(.*)\]', line) and line.startswith('['):
                    return 'section'
                elif re.search(r'(.*)=(.*)', line):
                    return 'parameter'
                else:
                    assert False, 'unexpected line: {}'.format(line)
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))

    def _get_index(self, section, parameter=None):
        try:
            s_i = None
            p_i = None
            for i in range(len(self._content)):
                if not self._content[i]['commented']:
                    if self._content[i]['name'] == section:
                        s_i = i
                        break
            if s_i is not None:
                if parameter is not None:
                    for i in range(len(self._content[s_i]['parameters'])):
                        if not self._content[s_i]['parameters'][i]['commented']:
                            if self._content[s_i]['parameters'][i]['name'] == parameter:
                                p_i = i
                                break
            return {'section_index': s_i, 'parameter_index': p_i}
        except Exception as e:
            raise Exception('{}.{}() {}: {}'.format(
                self.__class__.__name__, inspect.currentframe().f_code.co_name, e.__class__.__name__, e))

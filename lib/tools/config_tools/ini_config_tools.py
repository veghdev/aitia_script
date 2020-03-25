from inspect import currentframe
import re


def read_ini_file(file):
    try:
        f = open(file)
        ini_content = []
        unlinked_comment = None
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            # empty lines
            if line == '':
                continue
            line_type = _get_line_type(line)
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
                ini_content.append(section)
            # parameters or commented_parameters
            elif line_type == 'parameter' or line_type == 'commented_parameter':
                assert len(ini_content) != 0, f'parameter: {line} can not be linked to any section'
                parameter = {'name': re.search(r'(.*)=(.*)', line).group(1)}
                if unlinked_comment is not None:
                    parameter['description'] = unlinked_comment
                    unlinked_comment = None
                parameter['value'] = re.search(r'(.*)=(.*)', line).group(2)
                if line_type == 'commented_parameter':
                    parameter['commented'] = True
                else:
                    parameter['commented'] = False
                ini_content[-1]['parameters'].append(parameter)
            # comments
            elif line_type == 'comment':
                unlinked_comment = line
            else:
                assert False, f'unhandled line type: {line_type}'
        return ini_content
    except Exception as e:
        raise Exception('{}() {}: {}'.format(currentframe().f_code.co_name, e.__class__.__name__, e))
    finally:
        f.close()


def _get_line_type(line):
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
            assert False, f'can not be parsed line: {line}'


def write_ini_file(ini_content, file):
    try:
        f = open(file, 'w')
        for section in ini_content:
            if 'description' in section:
                if section['description'] != '':
                    f.write(';' + ' ' + section['description'] + '\n')
            if section['commented']:
                f.write(';' + ' ')
            f.write('[' + section['name'] + ']' + '\n')
            for parameter in section['parameters']:
                if 'description' in parameter:
                    if parameter['description'] != '':
                        f.write(';' + ' ' + parameter['description'] + '\n')
                if parameter['commented']:
                    f.write(';' + ' ')
                f.write(parameter['name'] + '=' + parameter['value'] + '\n')
            f.write('\n')
    except Exception as e:
        raise Exception('{}() {}: {}'.format(currentframe().f_code.co_name, e.__class__.__name__, e))
    finally:
        f.close()


def modify_ini_content(ini_content, section, parameter, value):
    try:
        index = _get_index(ini_content, section, parameter)
        ini_content[index['section_index']]['parameters'][index['parameter_index']]['value'] = value
        return ini_content
    except Exception as e:
        raise Exception('{}() {}: {}'.format(currentframe().f_code.co_name, e.__class__.__name__, e))


def _get_section_index(ini_content, section):
    for s_i in range(len(ini_content)):
        if not ini_content[s_i]['commented']:
            if not ini_content[s_i]['name'] == section:
                return s_i
    assert False, f'can not be find section: {section}'


def _get_index(ini_content, section, parameter=None):
    s_i = None
    p_i = None
    for i in range(len(ini_content)):
        if not ini_content[i]['commented']:
            if ini_content[i]['name'] == section:
                s_i = i
                break
    if parameter is not None:
        for i in range(len(ini_content[s_i]['parameters'])):
            if not ini_content[s_i]['parameters'][i]['commented']:
                if ini_content[s_i]['parameters'][i]['name'] == parameter:
                    p_i = i
                    break
    return {'section_index': s_i, 'parameter_index': p_i}


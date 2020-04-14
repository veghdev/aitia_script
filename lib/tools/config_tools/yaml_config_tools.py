import yaml


def find_value_with_key_dotted_path(yaml_object, key_dotted_path):
    if key_dotted_path.find('.') == -1:
        return yaml_object[key_dotted_path]
    else:
        pos = key_dotted_path.find('.')
        yaml_object = yaml_object[key_dotted_path[:pos]]
        key_dotted_path = key_dotted_path[pos + 1:]
        if not key_dotted_path.startswith("self."):
            return find_value_with_key_dotted_path(yaml_object, key_dotted_path)
        else:
            key_dotted_path = key_dotted_path[5:]
            for item in yaml_object:
                if key_dotted_path in item:
                    for key in item:
                        if item[key].find('{{ ') and item[key].find(' }}'):
                            return item[key_dotted_path]



def resolve_double_curly_brackets_variables(file):
    raw_yaml = yaml.load(open(file=file, mode='r'), Loader=yaml.FullLoader)
    data = open(file=file, mode='r').read()

    while True:
        pos1, pos2 = data.find('{{ '), data.find(' }}')
        if pos1 == -1:
            break
        data = data.replace('{{ ' + data[(pos1 + 3):(pos2 - 0)] + ' }}',
                            find_value_with_key_dotted_path(raw_yaml, data[(pos1 + 3):(pos2 - 0)]))
    return yaml.safe_load(data)

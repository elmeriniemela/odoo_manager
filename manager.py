
import os
import json
import glob
import re
from contextlib import contextmanager
from shutil import copyfile

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion import PathCompleter

@contextmanager
def quittable():
    try:
        yield
    except (EOFError, KeyboardInterrupt):
        print("Bye")
        quit()


def ask_dir():
    Path = PathCompleter(only_directories=True)
    while True:
        with quittable():
            path = prompt('> ', completer=Path)
        if os.path.isdir(path):
            return path
        print("Not a valid directory")

def get_config():
    CONFIG_FILE = 'config.json'
    def ask_config():
        config = {}
        print("Give the odoo source installation folder")
        config['odoo_path'] = ask_dir()
        print("Give the folder where you keep modules")
        config['addons_path'] = ask_dir()
        print("Whats your full name, used as the author of the modules?")
        config['author'] = input()
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        return config

    if not os.path.isfile('config.json'):
        return ask_config()
    with open('config.json') as f:
        return json.load(f)


def load_odoo_data(*paths):
    print("Loading available odoo modules..")
    models = set()
    wizards = set()
    modules = set()
    for path in paths:
        glob_path = os.path.normpath(path + f'/**/*.py')
        python_files = glob.glob(glob_path, recursive=True)
        for python_file in python_files:
            if python_file.endswith('__manifest__.py'):
                modules.add(os.path.basename(os.path.dirname(python_file)))
            else:
                with open(python_file) as f:
                    results = re.findall(r'''models\.([\w]+)[\w\W]*?[\W]_name = ['"](.*?)['"]''', f.read())
                    for match in results:
                        model_type, model_name = match
                        if model_type == 'Model':
                            models.add(model_name)
                        elif model_type == 'TransientModel':
                            wizards.add(model_name)
    return modules, models, wizards


def input(history=FileHistory('history.txt'), auto_suggest=AutoSuggestFromHistory(), **kwargs):
    with quittable():
        return prompt('> ',
            history=history,
            auto_suggest=auto_suggest,
            **kwargs
        )

def get_set(suggestions=set()):
    Suggest = WordCompleter(sorted(suggestions), sentence=True)
    output = set()
    while 1:
        answer = input(
            completer=Suggest
        )
        if not answer:
            break
        
        output.add(answer.strip())
    return output


current_dir = os.path.dirname(os.path.realpath(__file__))
TEMPLATE = os.path.join(current_dir, 'module_template')
CONFIG = get_config()
MODULES, MODELS, WIZARDS = load_odoo_data(CONFIG['odoo_path'], CONFIG['addons_path'])


def sub_module_map(model):
    return {
        '{model.name}': model.replace('_', '.'),
        '{model_name}': model.replace('.', '_'),
        '{ModelName}': ''.join([s.capitalize() for s in model.split('.')]),
    }

def map_files(models, data, template_file, file_ending):
    path_content = {}
    for model in models:
        model_data = data
        model_map = sub_module_map(model)
        for find, replace in model_map.items():
            model_data = model_data.replace(find, replace)
        model_path = os.path.join(os.path.dirname(template_file), model_map['{model_name}'] + file_ending)
        path_content[model_path] = model_data
    return path_content

def init_map(models, template_file):
    path_content = {}
    if models:
        init_template = "# -*- coding: utf-8 -*-\n\n{}\n"
        init_content = '\n'.join([f"from . import {model.replace('.', '_')}" for model in models])
        init_path = os.path.join(os.path.dirname(template_file), '__init__.py')
        path_content[init_path] = init_template.format(init_content)
    return path_content



if __name__ == '__main__':

    print("Name of the module")
    module_name = input()

    print("Any models to inherit? (empty input = done)")
    models = get_set(suggestions=MODELS)
    print("Any wizards to inherit? (empty input = done)")
    wizards = get_set(suggestions=WIZARDS)
    print("To which of the models or wizards you wish to create views? (empty input = done)")
    views = get_set(suggestions=models | wizards)
    print("Any dependencies?")
    depends = get_set(suggestions=MODULES)


    # models = set(['account.invoice', 'account.finvoice'])
    # wizards = set(['download.shit'])
    # views = set(['account.invoice', 'download.shit'])
    # depends = set(['finvoice'])

    sub_modules = {}
    if models:
        sub_modules['models'] = models
    if wizards:
        sub_modules['wizards'] = wizards


    files = glob.glob(TEMPLATE+"/**/*.*", recursive=True) + glob.glob(TEMPLATE+"/**/.*", recursive=True)

    views_paths = [f"'views/{sub_module.replace('.', '_')}_view.xml'," for sub_module in views]
    data = '\n        '.join(views_paths)

    general_map = {
        '{title_name}': ' '.join([s.capitalize() for s in module_name.split('_')]),
        '{module_name}': module_name,
        '{dependencies}': '\n        '.join([f"'{module}'," for module in depends]),
        '{depends}': next(iter(depends)) if depends else 'module',
        '{sub_modules}': ', '.join(sub_modules.keys()),
        '{data}': data,
        '{author}': CONFIG['author'],
    }
    module_dir = os.path.join(CONFIG['addons_path'], module_name)
    path_content = {}
    for file in files[:]:
        with open(file) as f:
            try:
                data = f.read()
            except UnicodeDecodeError:
                continue
            for find, replace in general_map.items():
                data = data.replace(find, replace)
            files.remove(file)
            folder = os.path.basename(os.path.dirname(file))
            file_name = os.path.basename(file)
            if folder == 'models' and file_name == 'model_name.py':
                path_content.update(map_files(models, data, file, '.py'))
                path_content.update(init_map(models, file))
            elif folder == 'wizards' and file_name == 'model_name.py':
                path_content.update(map_files(wizards, data, file, '.py'))
                path_content.update(init_map(wizards, file))
            elif folder == 'views' and file_name == 'model_name_view.xml':
                path_content.update(map_files(views, data, file, '_view.xml'))
            else:
                path_content[file] = data


    for file_path, data in path_content.items():
        new_path = os.path.join(module_dir, os.path.relpath(file_path, TEMPLATE))
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        with open(new_path, 'w') as f:
            f.write(data)

    for remaining_file in files:
        new_path = os.path.join(module_dir, os.path.relpath(remaining_file, TEMPLATE))
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        copyfile(remaining_file, new_path)

    print(f"Template created at {module_dir}")

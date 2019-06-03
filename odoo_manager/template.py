
import os
import glob
import shutil
import re
import pkg_resources
import json
import datetime as dt



from jinja2 import Environment, PackageLoader
CLASS_ENV = Environment(
    loader=PackageLoader('odoo_manager', 'templates'),
)
    

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE = os.path.join(CURRENT_DIR, 'module_template')
CACHE_FILE = pkg_resources.resource_filename('odoo_manager', 'cache.json')




class ModuleTemplate:

    def __str__(self):
        return CLASS_ENV.get_template('ModuleTemplate').render(
            name=self.name,
            models=self.models,
            wizards=self.wizards,
            views=self.views,
            depends=self.depends,
        )

    def __repr__(self):
        return f'{self.name}: {self.module_dir}'
    
    def __init__(self, config, name):
        self.config = config
        self.name = name
        self.module_dir = os.path.join(self.config['addons_path'], self.name)
        if os.path.exists(self.module_dir):
            raise FileExistsError("Module exists: %s" % self.module_dir)
        self.wizards = set()
        self.models = set()
        self.views = set()
        self.depends = set()

        self.available_models = set()
        self.available_wizards = set()
        self.available_modules = set()

    def add(self, data_type='models', name='account.invoice'):
        getattr(self, data_type).add(name)

    def write(self):
        shutil.rmtree(self.module_dir, ignore_errors=True)
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


        env = Environment(
            loader=PackageLoader('odoo_manager', 'module_template'),
        )

        general_map = {
            'title_name': ' '.join([s.capitalize() for s in self.name.split('_')]),
            'depends'
            'first_dependency': next(iter(self.depends)) if self.depends else 'module',
            'sub_modules': [n for n in ['models', 'wizards'] if getattr(self, n)],
            'views': self.views,
            'author': self.config['author'],
        }
        path_content = {}
        for template_name in env.list_templates():
            try:
                template = env.get_template(template_name)
            except UnicodeDecodeError:
                continue
            folder = os.path.basename(os.path.dirname(template_name))
            file_name = os.path.basename(template_name)
            if folder == 'models' and file_name == 'model_name.py':
                path_content.update(map_files(self.models, data, template_name, '.py'))
                path_content.update(init_map(self.models, template_name))
            elif folder == 'wizards' and file_name == 'model_name.py':
                path_content.update(map_files(self.wizards, data, template_name, '.py'))
                path_content.update(init_map(self.wizards, template_name))
            elif folder == 'views' and file_name == 'model_name_view.xml':
                path_content.update(map_files(self.views, data, template_name, '_view.xml'))
            else:
                path_content[template_name] = data


        for file_path, data in path_content.items():
            new_path = os.path.join(self.module_dir, os.path.relpath(file_path, TEMPLATE))
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            with open(new_path, 'w') as f:
                f.write(data)

        for remaining_file in files:
            new_path = os.path.join(self.module_dir, os.path.relpath(remaining_file, TEMPLATE))
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            shutil.copyfile(remaining_file, new_path)

        return f"Template created at {self.module_dir}"

    def load_odoo_data(self, *paths):
        print("Loading available odoo modules..")
        modified = dt.datetime.utcfromtimestamp(os.path.getmtime(CACHE_FILE))
        time_passed = dt.datetime.utcnow() - modified
        if time_passed < dt.timedelta(hours=1):
            with open(CACHE_FILE) as f:
                for key, value in json.load(f).items():
                    self.__dict__[key] = set(value)
            return

        for path in paths:
            glob_path = os.path.normpath(path + f'/**/*.py')
            python_files = glob.glob(glob_path, recursive=True)
            for python_file in python_files:
                if python_file.endswith('__manifest__.py'):
                    self.available_modules.add(os.path.basename(os.path.dirname(python_file)))
                    continue
                with open(python_file) as f:
                    results = re.findall(r'''models\.([\w]+)[\w\W]*?[\W]_name = ['"](.*?)['"]''', f.read())
                for match in results:
                    model_type, model_name = match
                    if model_type == 'Model':
                        self.available_models.add(model_name)
                    elif model_type == 'TransientModel':
                        self.available_wizards.add(model_name)

        with open(CACHE_FILE, 'w') as f:
            json.dump({
                'available_models': list(self.available_models),
                'available_wizards': list(self.available_wizards),
                'available_modules': list(self.available_modules),
            }, f, indent=4)


import os
import json
from contextlib import contextmanager

import pkg_resources
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion import PathCompleter

from odoo_manager.template import ModuleTemplate

HISTFILE = pkg_resources.resource_filename('odoo_manager', 'history.txt')
CONFIG_FILE = pkg_resources.resource_filename('odoo_manager', 'config.json')

def input(completions=set(), **kwargs):
    auto_suggest = AutoSuggestFromHistory()
    history = FileHistory(HISTFILE)
    Suggest = WordCompleter(sorted(completions), sentence=True)
    with quittable():
        return prompt('> ',
            history=history,
            completer=Suggest,
            auto_suggest=auto_suggest,
            **kwargs
        )


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
    def ask_config():
        print("**** CONFIG ('{}') ****".format(CONFIG_FILE))
        config = {}
        print("Give the odoo source installation folder")
        config['odoo_path'] = ask_dir()
        print("Whats your full name, used as the author of the modules?")
        config['author'] = input()
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return config

    if not os.path.isfile(CONFIG_FILE):
        return ask_config()
    with open(CONFIG_FILE) as f:
        return json.load(f)



def display_screen(module_template, additional_text):
    os.system('clear')
    print(module_template)
    print()
    print("1. Add models")
    print("2. Add wizards")
    print("3. Add views")
    print("4. Add dependencies")
    print("5. Rename module")
    print("6. Write")
    if additional_text:
        print()
        print(additional_text)
    print()


def main():
    config = get_config()

    template = ModuleTemplate(config)
    template.load_odoo_data(config['odoo_path'])

    command_mapping = {
        "1": ("Name of the model? (i.e account.invoice)", 'models', template.available_models),
        "2": ("Name of the wizard? (i.e download.bank.statements)", 'wizards', template.available_wizards),
        "3": ("Name of the view's res_model? (i.e account.invoice)", 'views', template.available_wizards | template.available_models),
        "4": ("Name of the dependency? (i.e hr_expense)", 'depends', template.available_modules),
        "5": ("Name of the module? (i.e sprintit_module_name)", 'name', set()),
    }
    # First ask the name
    command = '5'
    while True:
        comment = ""
        if command in command_mapping:
            question, attribute, suggestions = command_mapping[command]
            print(question)
            value = input(completions=suggestions)
            res = template.add(attribute, value)
            if res:
                comment = res

        elif command == "6":
            comment = template.write()
        elif command:
            comment = "Invalid Command '{}'".format(command)

        display_screen(template, comment)
        command = input()


if __name__ == '__main__':
    main()

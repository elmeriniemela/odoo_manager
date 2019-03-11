import os, sys
from shutil import copytree, rmtree, copyfile
current_dir = os.path.dirname(os.path.realpath(__file__))


ADDONS_PATH = "/home/elmeri/Code/addons12"
TEMPLATE = os.path.join(current_dir, 'module_template')


def sub_module_map(model_name):
    return {
        '{model_name}': model_name,
        '{model.name}': model_name.replace('_', '.'),
        '{ModelName}': ''.join([s.capitalize() for s in model_name.split('_')]),
    }


if sys.argv[1] == 'startapp':
    assert sys.argv[2], 'Must specify a name for module'
    module_name = sys.argv[2]

    module_dir = os.path.join(ADDONS_PATH, module_name)
    assert not os.path.exists(module_dir), 'Module name exists'
    models = input("Include models? Enter model_name ie. account_invoice ('n' = don't include)\n") or 'account_invoice'
    wizard = input("Include wizard? Enter model_name ie. download_statements_wizard ('n' = don't include)\n") or 'download_statements_wizard'
    views = input("Include views? ('n' = don't include)\n")
    depends = input("Module dependecy? (only one module allowed)\n") or 'account'
    copytree(TEMPLATE, module_dir)
    sub_modules = {}
    if models == 'n':
        rmtree(os.path.join(module_dir, "models"))
    elif models:
        sub_modules.update({'models': models})
    if wizard == 'n':
        rmtree(os.path.join(module_dir, "wizard"))
    elif wizard:
        sub_modules.update({'wizard': wizard})
    if views == 'n':
        rmtree(os.path.join(module_dir, "views"))
    module = os.walk(module_dir)

    views = [f"'views/{sub_module}_view.xml'" for sub_module in sub_modules.values()]
    data = '\n        '.join(views)

    general_map = {
        '{title_name}': ' '.join([s.capitalize() for s in module_name.split('_')]),
        '{module_name}': module_name,
        '{depends}': depends,
        '{sub_modules}': ', '.join(sub_modules.keys()),
        '{data}': data,
    }
    for (dirpath, dirnames, filenames) in module:
        final_map = {}
        if 'models' in dirpath:
            final_map.update(sub_module_map(models))
        if 'wizard' in dirpath:
            final_map.update(sub_module_map(wizard))
        final_map.update(general_map)

        if 'view.xml' not in filenames:
            for filename in filenames:
                if filename.endswith('.xml') or filename.endswith('.py') or filename.endswith('.rst'):
                    with open(os.path.join(dirpath, filename)) as f:
                        content = f.read()
                        for key, value in final_map.items():
                            content = content.replace(key, value)
                    if filename == 'model_name.py':
                        os.rename(os.path.join(dirpath, filename),
                                  os.path.join(dirpath, "%s.py" % final_map['{model_name}']))
                        filename = "%s.py" % final_map['{model_name}']
                    with open(os.path.join(dirpath, filename), 'w') as f:
                         f.write(content)  
        else:
            for module in sub_modules.values():
                xml_src = os.path.join(dirpath, module + '_view.xml')
                copyfile(os.path.join(dirpath, 'view.xml'), xml_src)
                modelmap = {}
                modelmap.update(general_map)
                modelmap.update(sub_module_map(module))

                with open(xml_src) as f:
                    content = f.read()
                    for key, value in modelmap.items():
                        content = content.replace(key, value)
                with open(xml_src, 'w') as f:
                        f.write(content)  
            os.remove(os.path.join(dirpath, 'view.xml'))


                    
 



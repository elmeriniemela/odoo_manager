import os, sys
from shutil import copytree, rmtree, copyfile
current_dir = os.path.dirname(os.path.realpath(__file__))



if sys.argv[1] == 'del':
    folder = sys.argv[2].lstrip('.').rstrip('\\')
    if not folder.startswith('\\'):
        folder = '\\' + folder

    target = current_dir + folder
    if not os.path.isdir(target):
        print(f"Module not found in this directory {target}")
        quit()

    s = 'rmdir ' + target
    input(s)
    os.system(s)


if sys.argv[1] == 'link':
    while True:
        path = input("Addons10 module: (use '/' for subfolders)\n")
        folders = path.split('/')
        formatted_path = '\\'.join(folders)

        src = f'G:\\My Drive\\Code\\addons10\\{formatted_path}'
        if not os.path.isdir(src):
            print("Module not found in addons10")
            continue

        module = folders[-1]
        project_path = input("Project path: (use '/' for subfolders)\n")
        if not project_path:
            s = f'mklink /D "{current_dir}\\{module}" "{src}"'
        if project_path:
            project_folders = project_path.split('/')
            formatted_project_path = '\\'.join(project_folders)
            s = f'mklink /D "{current_dir}\\{formatted_project_path}" "{src}"'
        input(s)
        os.system(s)
        break

if sys.argv[1] == 'my_modules':
    my_modules = []
    addons10_path = "G:\\My Drive\\Code\\addons10\\"
    addons = os.listdir(addons10_path)
    for addon in addons:
        if os.path.exists(addons10_path + addon + "\\__manifest__.py"):
            with open(addons10_path + addon + "\\__manifest__.py") as manifest:
                if "Elmeri" in manifest.read():
                    my_modules.append(addon)

    path = input("Subfolders? \n")
    folders = path.split('/')
    formatted_path = '\\'.join(folders)
    for module in my_modules:
        if not os.path.exists(f"{current_dir}\\{formatted_path}\\{module}"):
            s = f'mklink /D "{current_dir}\\{formatted_path}\\{module}" "{addons10_path}{module}"'
            input(s)
            os.system(s)


def sub_module_map(model_name):
    return {
        '{model_name}': model_name,
        '{model.name}': model_name.replace('_', '.'),
        '{ModelName}': ''.join([s.capitalize() for s in model_name.split('_')]),
    }


if sys.argv[1] == 'startapp':
    assert sys.argv[2], 'Must specify a name for module'
    module_name = sys.argv[2]
    addons10_path = "G:\\My Drive\\Code\\addons10\\"
    template_dir = "G:\\My Drive\\Code\\module_template"
    module_dir = addons10_path + module_name
    assert not os.path.exists(module_dir), 'Module name exists'
    models = input("Include models? Enter model_name ie. account_invoice ('n' = don't include)\n") or 'account_invoice'
    wizard = input("Include wizard? Enter model_name ie. download_statements_wizard ('n' = don't include)\n") or 'download_statements_wizard'
    views = input("Include views? ('n' = don't include)\n")
    depends = input("Module dependecy? (only one module allowed)\n") or 'account'
    copytree(template_dir, module_dir)
    sub_modules = {}
    if models == 'n':
        rmtree(module_dir + "\\models")
    elif models:
        sub_modules.update({'models': models})
    if wizard == 'n':
        rmtree(module_dir + "\\wizard")
    elif wizard:
        sub_modules.update({'wizard': wizard})
    if views == 'n':
        rmtree(module_dir + "\\views")
    module = os.walk(module_dir)

    views = [f"'views/{sub_module}.xml'" for sub_module in sub_modules.values()]
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
                xml_src = os.path.join(dirpath, module + '.xml')
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


                    
 



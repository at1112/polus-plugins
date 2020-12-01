from pathlib import Path
import os, shutil

base_path = Path(__file__).parent
plugin_path = base_path.joinpath('cookietin')
cookiecutter_path = base_path.joinpath('cookiecutter.json')

plugins = list(plugin_path.iterdir())

for i,plugin in enumerate(reversed(plugins)):
    path = Path(os.getcwd()).joinpath('polus-imagej-' + plugin.name + '-plugin')
    if path.is_dir():
        shutil.rmtree(str(path.absolute()))
    
    shutil.copy(str(plugin.joinpath('cookiecutter.json')),cookiecutter_path)
    
    os.system('cookiecutter ./utils/polus-imagej-util/ --no-input')

from importlib import machinery
import os
import types
import subprocess
# Constants to use
HOME = os.path.expanduser("~")
# TODO this should be in a better place
DEFAULT_CONFIG = os.path.join(HOME, 'shell', '.default.py')
PATH = []

# import default and user config
loader = machinery.SourceFileLoader('default_config', DEFAULT_CONFIG)
default_config = types.ModuleType(loader.name)
loader.exec_module(default_config)

if os.path.isfile(mod_path := os.path.join(HOME, ".pysh.py")):
    loader = machinery.SourceFileLoader(
        'config', mod_path)
elif os.path.isfile(mod_path := os.path.join(HOME, ".pysh.rc")):
    loader = machinery.SourceFileLoader(
        'config', mod_path)
elif os.path.isfile(mod_path := os.path.join(HOME, ".pysh")):
    loader = machinery.SourceFileLoader(
        'config', mod_path)

config = types.ModuleType(loader.name)
loader.exec_module(config)


def init():
    global PATH
    if isinstance(config.PATH, str):
        PATH = config.PATH.split(':')
    elif isinstance(config.PATH, list):
        PATH = config.PATH
    else:
        print("Path is malformed, using default")
        PATH = default_config.PATH


def resolve(name):
    func = None
    # Try to find executable in path and create the function to call
    for path in PATH:
        if os.path.isfile(exec_path := os.path.join(path, name)):
            def func(arg_list=[], std_in=None, std_out=None, std_err=None):
                process = subprocess.run([exec_path, *arg_list],
                                         stdin=std_in,
                                         stdout=std_out,
                                         stderr=std_err,
                                         universal_newlines=True,
                                         bufsize=0)

                return process

                # return process.stdout.readlines(), process.stderr.readlines()
            return func
    # If not in path try to call the function from config
    if config_func := getattr(config, name):
        def func(arg_list=[], std_in=None, std_out=None, std_err=None):
            config_func()

    return func


if __name__ == "__main__":
    init()
    resolve('test_func')()
    resolve('ls')()

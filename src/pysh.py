
from importlib import machinery
import os
import types
import subprocess
# Constants to use
HOME = os.path.expanduser("~")
# TODO this should be in a better place
DEFAULT_CONFIG = os.path.join(HOME, 'shell', '.default.py')
PATH = []
PROMPT = ""
ERROR = 0

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
    global PROMPT

    PATH = getattr(config, 'PATH', default_config.PATH)
    if isinstance(PATH, str):
        PATH = PATH.split(':')
    elif not isinstance(PATH, list):
        print("path malformed, using default")
        PATH = default_config.PATH

    PROMPT = getattr(config, 'PROMPT', default_config.PROMPT)


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
    if config_func := getattr(config, name, None):
        def func(arg_list=[], std_in=None, std_out=None, std_err=None):
            config_func()

    return func


# TODO at some point be able to string interpolate some things here
def render_prompt() -> str:
    return PROMPT if ERROR == 0 else f'(%d) %s' % (ERROR, PROMPT)


if __name__ == "__main__":
    init()

    while True:
        command = input(render_prompt())

        if command.strip().lower() == "exit":
            exit(0)
        else:
            [exec_name, *args] = command.split(' ')
            exec_function = resolve(exec_name)

            if exec_function is not None:
                exec_function()
            else:
                print("command not found")
                ERROR = 404

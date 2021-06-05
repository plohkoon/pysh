
from importlib import machinery
import os
import types
import subprocess
import shlex
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
    # Configure and clean PATH
    PATH = getattr(config, 'PATH', default_config.PATH)
    if isinstance(PATH, str):
        PATH = PATH.split(':')
    elif not isinstance(PATH, list):
        print("path malformed, using default")
        PATH = default_config.PATH
    # Get PROMPT
    PROMPT = getattr(config, 'PROMPT', default_config.PROMPT)


def resolve(name):
    func = None
    # Try to find executable in path and create the function to call
    for path in PATH:
        if os.path.isfile(exec_path := os.path.join(path, name)):
            def func(arg_list=[], std_in=None, std_out=None, std_err=None):
                process = subprocess.Popen([exec_path, *arg_list],
                                           stdin=std_in if std_in is not None else subprocess.PIPE,
                                           stdout=subprocess.PIPE if std_out is not None else None,
                                           stderr=subprocess.PIPE if std_err is not None else None,
                                           universal_newlines=True,
                                           bufsize=80)

                return process
            return func
    # If not in path try to call the function from config
    if config_func := getattr(config, name, None):
        def func(arg_list=[], std_in=None, std_out=None, std_err=None):
            config_func()

    return func


# TODO at some point be able to string interpolate some things here
def render_prompt() -> str:
    return PROMPT if ERROR == 0 else f'(%d) %s' % (ERROR, PROMPT)


def pipe_index_generator(arr: list[str]) -> tuple[int, int]:
    start = 0
    end = 0

    for i in range(len(arr)):
        if arr[i] == '|':
            end = i
            yield start, end
            start = i + 1

    yield start, len(arr)


if __name__ == "__main__":
    init()

    while True:
        command = input(render_prompt())

        if command.strip().lower() == "exit":
            exit(0)
        else:
            # TODO for now assume " | " with spaces is pipe, eventually fix this
            arg_list = shlex.split(command)
            pipe_split_commands = [arg_list[s:e]
                                   for s, e in pipe_index_generator(arg_list)]

            last_process = None

            for num, [exec_name, *args] in enumerate(pipe_split_commands):
                exec_function = resolve(exec_name)
                # TODO this currently breaks for interactive processes
                if exec_function is not None:
                    last_process = exec_function(arg_list=args,
                                                 std_in=None if last_process is None else last_process.stdout,
                                                 std_out=True if num < len(
                                                     pipe_split_commands) - 1 else None,
                                                 std_err=None)
                else:
                    print("command not found")
                    ERROR = 404

            if last_process is not None:
                last_process.communicate()
                ERROR = last_process.returncode

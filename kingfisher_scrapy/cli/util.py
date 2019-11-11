import os
import glob
import inspect
import importlib

from kingfisher_scrapy.cli.commands.base import CLICommand


def gather_cli_commands_instances():
    commands = {}
    dir_path = os.path.dirname(os.path.realpath(__file__))
    commands_dir = os.path.join(dir_path, 'commands')
    for file in glob.glob(commands_dir + '/*.py'):
        module = importlib.import_module('kingfisher_scrapy.cli.commands.' + file.split('/')[-1].split('.')[0])
        for item in dir(module):
            value = getattr(module, item)
            if inspect.isclass(value) and issubclass(value, CLICommand) \
                    and value is not CLICommand:
                commands[getattr(value, 'command')] = value()
    return commands

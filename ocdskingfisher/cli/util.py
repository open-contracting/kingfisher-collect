import os
import glob
import inspect
import importlib

import ocdskingfisher.cli.commands.base


def gather_cli_commands_instances(config=None):
    commands = {}
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sources_dir = os.path.join(dir_path, '..', '..', 'ocdskingfisher', 'cli', 'commands')
    for file in glob.glob(sources_dir + '/*.py'):
        module = importlib.import_module('ocdskingfisher.cli.commands.' + file.split('/')[-1].split('.')[0])
        for item in dir(module):
            value = getattr(module, item)
            if inspect.isclass(value) and issubclass(value, ocdskingfisher.cli.commands.base.CLICommand) \
                    and value is not ocdskingfisher.cli.commands.base.CLICommand:
                commands[getattr(value, 'command')] = value(config=config)
    return commands



class CLICommand:
    command = ''

    def __init__(self, config=None):
        self.config = config

    def configure_subparser(self, subparser):
        pass

    def run_command(self, args):
        pass

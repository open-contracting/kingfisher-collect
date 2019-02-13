import os
import configparser


"""This holds configuration information for Kingfisher.
Whatever tool is calling it - CLI or other code - should create one of these, set it up as required and pass it around.
"""


class Config:

    def __init__(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        # This sets the default base dir in the code folder. There is an issue to change this later.
        # https://github.com/open-contracting/kingfisher/issues/223
        self.data_dir = os.path.join(this_dir, "..", "data")

    def load_user_config(self):

        if os.environ.get('KINGFISHER_DATA_DIR'):
            self.data_dir = os.environ.get('KINGFISHER_DATA_DIR')
            return

        config = configparser.ConfigParser()

        if os.path.isfile(os.path.expanduser('~/.config/ocdskingfisher/config.ini')):
            config.read(os.path.expanduser('~/.config/ocdskingfisher/config.ini'))
        else:
            return

        self.data_dir = config.get('DATA', 'DIR', fallback=self.data_dir)

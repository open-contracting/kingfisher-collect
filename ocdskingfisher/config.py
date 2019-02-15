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
        self.server_url = None
        self.server_api_key = None

    def load_user_config(self):

        config = configparser.ConfigParser()

        if os.path.isfile(os.path.expanduser('~/.config/ocdskingfisher/old-config.ini')):
            config.read(os.path.expanduser('~/.config/ocdskingfisher/old-config.ini'))
        else:
            return

        self.data_dir = config.get('DATA', 'DIR', fallback=self.data_dir)

        self.server_url = config.get('SERVER', 'URL')
        self.server_api_key = config.get('SERVER', 'API_KEY')

# coding: utf-8
'''
Inspired from matplotlib __init__
Settings are stored in HOME/SETTINGS_DIR/SETTINGS_FILE
Note: The settings are just stored in a dictionary, self.settings. Just perform ordinary dict manipulation to change settings.
'''

import os, tempfile
from configparser import ConfigParser
from mylog import get_logger
logger = get_logger(__name__)
from pprint import pformat

SETTINGS_DIR = '.learnleadfast'
SETTINGS_FILE = 'settings.toml'  

import tomllib
import tomli_w

class ConfigManager():

    def __init__(self):
        self.configdir = ConfigManager.get_configdir() #home_path/SETTINGS_DIR
        self.filename = os.path.join(self.configdir, SETTINGS_FILE)

        #Read existing config file
        if os.path.exists(self.filename):
            logger.debug('Reading existing config file')
            with open(self.filename, "rb") as f:
                self.settings = tomllib.load(f)
                logger.debug(f"\n{pformat(self.settings)}")

        #Create new config file
        else:
            logger.debug('Creating new config file: {}'.format(self.filename))
            self.settings = {
                'Basic': {'last_load_dir': ''}, 
                'OptionChain': {'show_weekly': False, 'strikes_desc': True}, 
            }
            # self.save_settings()
            with open(self.filename, 'wb') as f:
                tomli_w.dump(self.settings, f)


    @staticmethod
    def _is_writable_dir(p):
        """
        p is a string pointing to a putative writable dir -- return True p
        is such a string, else False
        """
        try: p + ''  # test is string like
        except TypeError: return False
        try:
            t = tempfile.TemporaryFile(dir=p)
            t.write(b'123456')
            t.close()
        except OSError: return False
        else: return True
        
        
    @staticmethod
    def get_home():
        """Find user's home directory if possible.
        Otherwise raise error.

        :see:  http://mail.python.org/pipermail/python-list/2005-February/263921.html
        """
        path=''
        try:
            path=os.path.expanduser("~") 
        except:
            pass
        if not os.path.isdir(path):
            for evar in ('HOME', 'USERPROFILE', 'TMP'):
                try:
                    path = os.environ[evar]
                    if os.path.isdir(path):
                        break
                except: pass
        if path:
            return path
        else:
            raise RuntimeError('please define environment variable $HOME')


    @staticmethod
    def get_configdir():
        """
        Get the config dir or create it if it doesn't exist.
        """

        h = ConfigManager.get_home()
        p = os.path.join(h, SETTINGS_DIR)

        if os.path.exists(p):
            if not ConfigManager._is_writable_dir(p):
                raise RuntimeError("'%s' is not a writable dir; you must set %s/.matplotlib to be a writable dir.  You can also set environment variable MPLCONFIGDIR to any writable directory where you want matplotlib data stored "% (h, h))
        else:
            if not ConfigManager._is_writable_dir(h):
                raise RuntimeError("Failed to create %s/.matplotlib; consider setting MPLCONFIGDIR to a writable directory for matplotlib configuration data"%h)

            os.mkdir(p)
        return p


    def save_settings(self):
        '''
        Saves the settings dict to self.filename
        '''
        if os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                tomli_w.dump(self.settings, f)


if __name__ == '__main__':

    #Example usage
    config = ConfigManager()
    # config.settings['Sync'] = 'Testing123'
    config.settings['OptionChain']['strike_filter'] = [25,10]
    config.save_settings()

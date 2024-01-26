# config.py 

import yaml

# LOCAL IMPORTS
from config import PROJECT_PATH

class NotInConfigException(Exception):
    def __init__(self, key):
        self.message = f"Could not found the key `{key}` in the config file."
        super().__init__(self.message)  

class ConfigFileException(Exception):
    def __init__(self, message="Could not load the config file."):
        self.message = message
        super().__init__(self.message)  

class Config():
    def __init__(self):
        self.__read_config()
        
    def __read_config(self):
        try:
            with open(rf"{PROJECT_PATH}\config.yaml", "r") as f:
                self.__config = yaml.load(f, Loader=yaml.FullLoader)
        except:
            raise ConfigFileException
    
    def read(self, *args):
        """Read
        Reads a config param base on its location.
        The order of the arguments is the order of 
        the parameter location in the config.yaml file.

        Returns
        -------
        Any
            The value of the requested parameter or raises 
            an error if was not found.
        """
        res = self.__config
        key_not_found = None
        try:
            for a in args:
                key_not_found = a
                res = res[a]
        except:
            raise NotInConfigException(key=key_not_found)
        return res
  
# # DEBUGGING  
# if __name__ == "__main__":
#     c = Config()
#     print(c.read("text2speech", "male"))
#     print(c.read("auth"))
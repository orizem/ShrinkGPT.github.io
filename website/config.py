# config.py 

import yaml

class NotInConfigException(Exception):
    def __init__(self, message="Could not found in config file."):
        self.message = message
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
            with open("config.yaml", "r") as f:
                self.__config = yaml.load(f, Loader=yaml.FullLoader)
        except:
            ConfigFileException
    
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
        try:
            for a in args:
                res = res[a]
        except:
            raise NotInConfigException
        return res
  
# # DEBUGGING  
# if __name__ == "__main__":
#     c = Config()
#     print(c.read("text2speech", "male"))
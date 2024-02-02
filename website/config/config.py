# config.py

import yaml

# PROJECT IMPORTS
from config import WEBSITE_PATH


class __NotInConfigException(Exception):
    def __init__(self, key):
        self.message = f"Could not found the key `{key}` in the config file."
        super().__init__(self.message)


class __ConfigFileException(Exception):
    def __init__(self, message="Could not load the config file."):
        self.message = message
        super().__init__(self.message)


class __Config:
    def __init__(self):
        self.__read_config()

    def __read_config(self):
        try:
            with open(rf"{WEBSITE_PATH}\config\config.yaml", "r") as f:
                self.__config = yaml.load(f, Loader=yaml.FullLoader)
        except:
            raise __ConfigFileException

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
        list_keys_not_found = []
        for a in args:
            try:
                key_not_found = a
                res = res[a]
            except:
                list_keys_not_found.append(key_not_found)
                # raise __NotInConfigException(key=key_not_found)
        if len(list_keys_not_found) > 0:
            print(f"Keys not found: {', '.join(list_keys_not_found)}")
            return None
        return res


config = __Config()
# # DEBUGGING
# if __name__ == "__main__":
#     c = Config()
#     print(c.read("text2speech", "male"))
#     print(c.read("auth"))

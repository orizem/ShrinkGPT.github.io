# config.py

import yaml

# PROJECT IMPORTS
from config import WEBSITE_PATH


class __NotInConfigException(Exception):
    """Not In Config Exception

    This exception occurs when the key can not be found in the config.
    If you get this exception, try looking at the `config.yaml` file
    to see if you used the correct path.

    Parameters
    ----------
    Exception : Exception
        Base exception.
    """

    def __init__(self, key):
        self.message = f"Could not found the key `{key}` in the config file."
        super().__init__(self.message)


class __ConfigFileException(Exception):
    """Config File Exception

    This exception occurs when the config file can not be loaded.
    If you get this exception, try looking at the path of the `config.yaml` file.

    Parameters
    ----------
    Exception : Exception
        Base exception.
    """

    def __init__(self, message="Could not load the config file."):
        self.message = message
        super().__init__(self.message)


class __Config:
    """Config

    Class for reading the config yaml file and handles
    reading the values from the output.
    """

    def __init__(self):
        self.__read_config()

    def __read_config(self):
        """Read Config Summary

        Private method that reads the `config.yaml` file
        and stores it in a private variable.

        Raises
        ------
        __ConfigFileException
            This exception raises if no `config.yaml` file was found.
        """
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

        Args
        ----
        *param (str):
            Keys for reaching a value in the config,
            act like a path.

        Returns
        -------
        Any
            The value of the requested parameter or raises
            an error if was not found.
        """
        res = self.__config
        for a in args:
            # Trying to find the next key in the current path
            if a in res:
                res = res[a]
            else:
                # raise __NotInConfigException(key=key_not_found)
                print(f"Key not found: {a}")
                return None
        return res


config = __Config()
# # DEBUGGING
# if __name__ == "__main__":
#     c = Config()
#     print(c.read("text2speech", "male"))
#     print(c.read("auth"))

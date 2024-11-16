# config.py

import yaml

# PROJECT IMPORTS
from config import WEBSITE_PATH


class __NotInConfigException(Exception):
    """Not In Config Exception

    Raised when a specified key cannot be found in the configuration.
    This exception is used to signal that the requested key does not exist
    in the `config.yaml` file. If this exception occurs, ensure the correct
    key is being used and that the path is correct in the YAML file.

    Parameters
    ----------
    key : str
        The key that could not be found in the configuration file.
    """

    def __init__(self, key):
        self.message = f"Could not found the key `{key}` in the config file."
        super().__init__(self.message)


class __ConfigFileException(Exception):
    """Config File Exception

    Raised when there is an error loading the configuration file.
    This exception occurs if the `config.yaml` file cannot be found 
    or loaded from the specified path. Check the file path or permissions
    if this exception is encountered.

    Parameters
    ----------
    message : str, optional
        The error message to display. Defaults to 'Could not load the config file.'.
    """

    def __init__(self, message="Could not load the config file."):
        self.message = message
        super().__init__(self.message)


class __Config:
    """Config

    A class for reading and managing configuration data from a `config.yaml` file.
    This class handles the loading of the configuration file and provides
    functionality to access the configuration values through method calls.

    The configuration is expected to be in YAML format, with values that can
    be accessed through keys provided as arguments.

    Methods
    -------
    __init__() -> None
        Initializes the configuration by reading the config file.

    __read_config() -> None
        Private method that loads the configuration from the `config.yaml` file.
        Raises `__ConfigFileException` if the file cannot be found or loaded.

    read(\*args) -> Any
        Reads a configuration value based on the specified path in the YAML file.
        Arguments represent the keys in the YAML file, and the function navigates
        through the keys to return the corresponding value.
        
    Args
    ----
        Keys that represent the path to a value in the configuration file.

    Returns
    -------
    Any
        The value found at the specified path in the configuration file, or `None`
        if the key path does not exist.

    Raises
    ------
    __NotInConfigException
        If a key cannot be found in the configuration file during navigation.

    __ConfigFileException
        If the configuration file cannot be loaded.
    """

    def __init__(self):
        self.__read_config()

    def __read_config(self):
        """Read Config Summary

        Private method that attempts to read the `config.yaml` file and load
        its content into a private variable. Raises `__ConfigFileException`
        if the file cannot be loaded.

        Raises
        ------
        __ConfigFileException
            If no `config.yaml` file was found or there was an error loading it.
        """
        try:
            with open(f"{WEBSITE_PATH}/config/config.yaml", "r") as f:
                self.__config = yaml.load(f, Loader=yaml.FullLoader)
        except Exception:
            raise __ConfigFileException

    def read(self, *args):
        """Read

        Reads a configuration parameter based on the specified path in the `config.yaml` file.
        The arguments represent the keys to navigate through the file's structure.

        Args
        ----
            Keys for accessing the value in the `config.yaml` file, acting like a path.

        Returns
        -------
        Any
            The value of the requested parameter, or `None` if the key is not found.
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

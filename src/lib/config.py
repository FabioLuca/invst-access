"""Module for managing configurations which are stored in Json files.
"""

import json
import logging
import inspect
import glob
from pathlib import Path
from . import messages as M
from .invst_const import constants as C


class Config:
    """Loads the designated configuration file and parses the content into
    blocks of information (sub-dictionaries).

    Parameters
    ----------
        logger_name: string
            The name for the logger object. The recommendation is to keep a
            single name across the application, so pass here the same used in
            other parts of the application.

    Attributes
    ----------
        filename: `pathlib path`
            File path with the .json file where the configuration is stored. At
            initialization its content is `None`, and the value is updated
            after the call of the method `load_config`.
        json_file: `file object`
            File object where the configuration is stored. At initialization
            its content is `None`, and the value is updated after the call of
            the method `load_config`.
        json_data: `dictionary`
            Configuration dictionary. At initialization its content is `None`,
            and the value is updated after the call of the method `load_config`.

    """

    def __init__(self, logger_name):

        self.filename = None
        self.json_file = None
        self.json_data = None

        self.data = None

        self.data_source_fetch_name = None
        self.data_source_fetch_access_data = None
        self.data_source_fetch_user_data = None

        self.data_source_trade_name = None
        self.data_source_trade_access_data = None
        self.data_source_trade_user_data = None

        self.data_source_wapp_name = None
        self.data_source_wapp_access_data = None
        self.data_source_wapp_user_data = None

        self.data_source_mail_name = None
        self.data_source_mail_access_data = None
        self.data_source_mail_user_data = None

        self.data_source_comm_access_data = None
        self.data_source_comm_user_data = None

        self.local_config = None

        # ----------------------------------------------------------------------
        #   Defines the logger to output the information and also
        #   add an entry for the start of the class
        # ----------------------------------------------------------------------
        self.logger_name = logger_name + ".config"
        self.logger = logging.getLogger(self.logger_name)
        self.logger.info("Initializing configuration.")

    def assert_filename(self, filename):
        """Verifies if the file passed for the configuration exists. In case it
        doesn't exist, the application will search for a file with the same name
        and extension, starting from 1 folder above (not more). This is intended
        to support with some operations from the project, where the starting
        folder is different from the main application, for example, creating
        docs in Sphinx.
        """

        foundfiles = None
        if not filename.exists():
            for path in Path('..').rglob(filename.name):
                foundfiles = path
                break
            return foundfiles
        return filename

    def load_config(self, filename):

        filename = self.assert_filename(filename=filename)

        flag, level, message = M.get_status(
            self.logger_name, "Config_Load_Config", filename)

        self.filename = filename
        self.json_file = None
        self.json_data = None

        self.load_config_file()

        if filename.stem == "api-cfg":

            # # ----------------------------------------------------------------------
            # #   Configuration for logging parameters. All the parameters defined
            # #   in "logging" on the first level will added with the same name.
            # # ----------------------------------------------------------------------
            # for parameter in self.json_data["logging"]:
            #     vars(self)[parameter] = self.json_data["logging"][parameter]

            # # ----------------------------------------------------------------------
            # #   Configuration related to file paths
            # # ----------------------------------------------------------------------
            # for parameter in self.json_data["paths"]:
            #     vars(self)[parameter] = self.json_data["paths"][parameter]

            # ------------------------------------------------------------------
            #   Configuration related to the online data sources
            # ------------------------------------------------------------------
            self.data_source_fetch_name = self.json_data[
                "api"]["fetching"]["selection"]
            self.data_source_fetch_access_data = self.json_data[
                "api"]["fetching"][self.data_source_fetch_name]["access_data"]
            self.data_source_trade_name = self.json_data[
                "api"]["trading"]["selection"]
            self.data_source_trade_access_data = self.json_data[
                "api"]["trading"][self.data_source_trade_name]["access_data"]
            self.data_source_wapp_name = self.json_data[
                "api"]["communicating"]["whatsapp"]["selection"]
            self.data_source_wapp_access_data = self.json_data[
                "api"]["communicating"]["whatsapp"][self.data_source_wapp_name]["access_data"]
            self.data_source_mail_name = self.json_data[
                "api"]["communicating"]["email"]["selection"]
            self.data_source_mail_access_data = self.json_data[
                "api"]["communicating"]["email"][self.data_source_mail_name]["access_data"]

            self.data_source_comm_access_data = {
                "whatsapp": self.data_source_wapp_access_data,
                "email": self.data_source_mail_access_data
            }

        elif filename.stem == "api-cfg-access":

            if self.data_source_fetch_name is None:
                result = None
                flag, level, message = M.get_status(
                    self.logger_name,
                    "Config_Error_No_Source_Fetching",
                    inspect.currentframe().f_code.co_name)
                return result, flag, level, message

            if self.data_source_trade_name is None:
                result = None
                flag, level, message = M.get_status(
                    self.logger_name,
                    "Config_Error_No_Source_Trading",
                    inspect.currentframe().f_code.co_name)
                return result, flag, level, message

            # ------------------------------------------------------------------
            #   Configuration related to the online data sources
            # ------------------------------------------------------------------
            self.data_source_fetch_user_data = self.json_data[
                "api"]["fetching"][self.data_source_fetch_name]["user_data"]
            self.data_source_trade_user_data = self.json_data[
                "api"]["trading"][self.data_source_trade_name]["user_data"]
            self.data_source_wapp_user_data = self.json_data[
                "api"]["communicating"]["whatsapp"][self.data_source_wapp_name]["user_data"]
            self.data_source_mail_user_data = self.json_data[
                "api"]["communicating"]["email"][self.data_source_mail_name]["user_data"]

            self.data_source_comm_user_data = {
                "whatsapp": self.data_source_wapp_user_data,
                "email": self.data_source_mail_user_data
            }

        elif filename.stem == "local":
            # ------------------------------------------------------------------
            #   Configuration related to local paramters.
            # ------------------------------------------------------------------
            self.local_config = self.json_data

        result = None
        flag, level, message = M.get_status(
            self.logger_name, "Config_Load_Success", filename)
        return result, flag, level, message

    def get_dictionary(self):
        """Returns the complete dictionary of configuration"""
        return self.json_data

    def load_config_file(self):
        """Loads the Json file where the configuration is stored and returns
        the content in a dictionary format"""
        with open(self.filename, encoding="utf-8") as self.json_file:
            self.json_data = json.load(self.json_file)

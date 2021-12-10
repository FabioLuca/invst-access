"""Script for getting the current values from Comdirect and storing into Excel
files, to be used as a tracker.

"""
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from src.lib.config import Config
from src.session import Session
from src.lib.invst_const import constants as C

LOGGER_NAME = "invst.comdirect_status_update"

if __name__ == "__main__":

    # --------------------------------------------------------------------------
    #   Defines the logger configuration and start the logger. Add a few
    #   message to mark the start of the execution.
    # --------------------------------------------------------------------------
    logging.basicConfig(
        filename=Path.cwd().resolve() / "logs" / "logs.log",
        filemode="a",
        datefmt="%Y.%m.%d %I:%M:%S %p",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )

    logformat = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y.%m.%d %I:%M:%S %p",)

    logger_console = logging.StreamHandler()
    logger_console.setLevel(logging.INFO)
    logger_console.setFormatter(logformat)

    logging.getLogger(LOGGER_NAME).addHandler(logger_console)

    logger = logging.getLogger(LOGGER_NAME)

    logger.info("")
    logger.info("========================== NEW RUN ==========================")

    # --------------------------------------------------------------------------
    #   Defines the location of the files with configurations and load them.
    # --------------------------------------------------------------------------
    config_access_file = Path.cwd().resolve() / "cfg" / "api-cfg.json"
    config_access_userdata_file = Path.cwd().resolve() / "cfg" / \
        "api-cfg-access.json"

    config = Config(logger_name=LOGGER_NAME)
    config_dictionary = config.load_config(filename=config_access_file)

    config_access_userdata = config.load_config(
        filename=config_access_userdata_file)

    # --------------------------------------------------------------------------
    #   Example of accessing a Comdirect account and fetching information.
    # --------------------------------------------------------------------------
    comdirect = Session(access_config=config.data_source_trade_access_data,
                        access_userdata=config.data_source_trade_user_data,
                        logger_name=LOGGER_NAME,
                        )
    comdirect.connect()
    balance, flag, level, message = comdirect.get_accounts_balance()
    depots, flag, level, message = comdirect.get_depots()
    if flag == C.SUCCESS:
        for index, row in depots.iterrows():
            depot_position, flag, level, message = comdirect.get_depot_position(
                row["Depot ID"])
    comdirect.revoke_token()

    # --------------------------------------------------------------------------
    #   Store the results into an Excel files.
    # --------------------------------------------------------------------------
    today_string = datetime.today().strftime('%Y-%m-%d')
    file_export_trade = f"Export_Comdirect_{today_string}.xlsx"
    file_export_trade = Path.cwd().resolve() / "export" / file_export_trade
    writer_trade = pd.ExcelWriter(file_export_trade, engine='xlsxwriter')
    balance.to_excel(writer_trade, sheet_name='Balance')
    depots.to_excel(writer_trade, sheet_name='Depots')
    depot_position[0].to_excel(
        writer_trade, sheet_name='Depot Positions Aggregated')
    depot_position[1].to_excel(writer_trade, sheet_name='Depot Positions')
    writer_trade.save()

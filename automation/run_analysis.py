"""Script for sequence analysis of a list of symbols / tickers and providing
a report of the overall results for performance evaluation.

"""
import logging
import time
from pathlib import Path
from datetime import datetime
from src.communication import Communication
from src.lib.config import Config
from src.lib.invst_const import constants as C
from src.data_access import DataAccess
from src.analysis import Analysis
from src.lib import print_table as pt

LOGGER_NAME = "invst.run_analysis"

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
    config_base_path = Path.cwd().resolve() / "cfg"
    config_access_file = config_base_path / "api-cfg.json"
    config_access_userdata_file = config_base_path / "api-cfg-access.json"
    config_local_file = config_base_path / "local.json"

    config = Config(logger_name=LOGGER_NAME)
    config.load_config(filename=config_access_file)
    config.load_config(filename=config_access_userdata_file)
    config.load_config(filename=config_local_file)

    # --------------------------------------------------------------------------
    #   Starts the communication and send a message to notify.
    # --------------------------------------------------------------------------
    communication = Communication(
        access_config=config.data_source_comm_access_data,
        access_userdata=config.data_source_comm_user_data,
        logger_name=LOGGER_NAME
    )

    communication.send_message(
        body=f"Starting analysis of tickers.\nReference: {datetime.now().strftime('%H:%M:%S')}")

    communication.send_email(
        subject=f"Starting analysis of tickers ({datetime.now().strftime('%H:%M:%S')})",
        body_html=f"Starting analysis of tickers.\nReference: {datetime.now().strftime('%H:%M:%S')}")

    # --------------------------------------------------------------------------
    #   List of tickers and sequence analysis.
    # --------------------------------------------------------------------------
    symbols = [
        {"name": "Coca-Cola Co.", "symbol": "KO"},
        # {"name": "Alphabet Inc.", "symbol": "GOOG"},
        #    {"name": "Tesla, Inc.", "symbol": "TSLA"},
        #    {"name": "Boeing Co.", "symbol": "BA"},
        #    {"name": "Daimler AG", "symbol": "DAI.DE"},
        #    {"name": "Siemens AG", "symbol": "SIE.DE"},
        #    {"name": "Apple", "symbol": "AAPL"},
        #    {"name": "Amazon", "symbol": "AMZN"},
        #    {"name": "Bristol-Meyers Squibb", "symbol": "BMY"},
        #    {"name": "General Motors", "symbol": "GM"},
        #    {"name": "AbbVie Inc.", "symbol": "ABBV"},
        #    {"name": "AMERICAN EXPRESS CO.", "symbol": "AXP"},
        #    {"name": "3M CO.", "symbol": "MMM"},
        #    {"name": "CISCO INC.", "symbol": "CSCO"},
        #    {"name": "IBM CORP.", "symbol": "IBM"},
        #    {"name": "The Walt Disney Co.", "symbol": "DIS"},
        #    {"name": "Johnson & Johnson", "symbol": "JNJ"},
        #    {"name": "IDEX", "symbol": "IEX"},
        #    {"name": "Akamai Technologies, Inc.", "symbol": "AKAM"},
        #    {"name": "Telefonaktiebolaget LM Ericsson", "symbol": "ERIC"},
        #    {"name": "Thermo Fisher Scientific Inc.", "symbol": "TMO"},
        #    {"name": "Zscaler, Inc.", "symbol": "ZS"},
        #    {"name": "Meta", "symbol": "FB"},
    ]

    results_data = []
    results_analysis = []
    results_summary = []

    for symbol in symbols:

        # Short pause between requests to avoid over-request to AlphaVantage
        time.sleep(5)

        ticker = symbol["symbol"]

        result = DataAccess(ticker=ticker,
                            source=config.data_source_fetch_name,
                            access_config=config.data_source_fetch_access_data,
                            access_userdata=config.data_source_fetch_user_data,
                            logger_name=LOGGER_NAME,
                            )

        result_values, flag, level, message = result.update_values(
            type_series="TIMESERIES", period="DAILY"
        )

        if flag == C.SUCCESS:

            results_data.append(result)

            # --------------------------------------------------------------------------
            #   Perform analysis of the data.
            # --------------------------------------------------------------------------
            analysis = Analysis(symbol=ticker,
                                ohlc_data=result_values,
                                analysis_length=750,
                                initial_value=10000,
                                stopgain=1.4,
                                stoploss=0.85,
                                operation_cost=5,
                                tax_percentage=0.1,
                                logger_name=LOGGER_NAME,
                                display_analysis=False,
                                save_analysis=True)
            decision = analysis.analyze()

            results_analysis.append(analysis)
            results_summary.append({ticker: analysis.analysis_results})

            analysis = None
            result = None

    if len(results_summary) > 1 and len(results_summary) > 1:
        today_string = datetime.today().strftime('%Y-%m-%d')
        file_export_summary = f"Export_Summary_{today_string}.xlsx"
        folder = Path(config.local_config["paths"]["data_storage"])
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
        file_export_summary = folder / file_export_summary
        df_results_summary = pt.summary_table(
            results_summary, file_export_summary)

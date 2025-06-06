#!/usr/bin/env python3
"""
Constants used throughout app.
"""

import sys
from pathlib import Path
import logzero
from logzero import logger
from collections import namedtuple

#sys.path.append(Path('cbdc_scraper').absolute().as_posix() )
#from output import Output




# variables
emails_file = './config/emails.csv'
email_network_drive = r'\\hqfiles01\sec_edgar$\cbdc_tracker'

#report_dir = './result_output'
#report_copy_dir = './result_output'
logging_dir = './logs/process.log'


# logging
logzero.loglevel(logzero.INFO)                                           #set a minimum log level: debug, info, warning, error
logzero.logfile(logging_dir, maxBytes=1000000, backupCount=3)            #set rotating log file
logger.info('logger created, constants initialized')


# output
'''
output = Output(
    report_copy_dir = report_copy_dir,
    report_dir = report_dir,
    emails_file_or_dictlist = emails_file,
    email_network_drive = email_network_drive,
    logger = logger
    )
'''




country_record = namedtuple(
    "CountryRecord",
        ["Country",
        "Status",
        "StatusChange",
        "StatusLastQtr",

        "CentralBank",
        "NationalBankPresence",
        "BankNames",

        "CurrencyName",
        "Purpose",
        "PartnerFirm",
        "Software",
        "LedgerType",
        "BlockChainPermissions",

        "Technology",
        "Summary",
        ]
)

notable = ["China", "Jamaica", "Nigeria", "Russia"]
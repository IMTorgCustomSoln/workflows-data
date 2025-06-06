#!/usr/bin/env python3
"""
Main entrypoint
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

import sys
import argparse


#register here
from config import config_env
from workflows import (
    workflow_asr,
    workflow_site_scrape,
    workflow_ecomms,
    workflow_export_workspace,
    workflow_template
)
workflow_options = {
    'workflow_asr': workflow_asr.workflow_asr,
    'workflow_site_scrape': workflow_site_scrape.workflow_site_scrape,
    'workflow_ecomms': workflow_ecomms.workflow_ecomms,
    'workflow_template': workflow_template.workflow_template,
    'workflow_export_workspace': workflow_export_workspace.workflow_export_workspace
    }



def main(args):
    """..."""
    config_env.config()
    if args.workflow in workflow_options.keys():
        workflow = workflow_options[args.workflow]
        getattr(workflow, args.task)()
    sys.exit()





if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", 
                        help="Choose workflow from available files: `./workflows/workflow_*` ")
    parser.add_argument("task", 
                        help="Choose task workflow should perform")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
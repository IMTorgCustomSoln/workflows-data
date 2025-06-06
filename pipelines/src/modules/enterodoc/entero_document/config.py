#!/usr/bin/env python3
"""
Constants used for configuration of all classes
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"


from .utils import dotdict
from .record import DocumentRecord

import logzero
from logzero import logger
from dotmap import DotMap

import sys
from pathlib import Path
import json



class EnteroConfig:
    """Config for both Document and UniformResourceLocator classes.
    
    :param apply_logger: bool to use default Path() / 'logs' / 'process.log' (True), or simply print (False)

    Usage::
        Prefer the Singleton instantiated below this class
        >>> from entero_document.config import ConfigObj
        >>> ConfigObj.output_mapping_template_path = Path('tests/data/mapping_template.json')
        >>> ConfigObj.get_output_mapping_template()
        
        If you need different configurations for some objects, it is possible
        >>> config1 = EnteroConfig(apply_logger=True)
        >>> config2 = EnteroConfig(apply_logger=False)
    """

    def __init__(self, apply_logger=True):

        #constants
        self.MAX_PAGE_EXTRACT = None
        self.MAX_CONTENT_SIZE = 1e+8         #in bytes => 100MB
        self.ALLOWED_EXTENSIONS = {'.zip'}

        #output
        self.output_mapping_template_path = None
        self.output_mapping = None
        
        # dependencies
        self.applyRequestsRenderJs = False
        self.applySpacy = False
        self.applyPyMuPDF = True
        self.applyOCRmyPDF = False

        # logging
        if apply_logger:
            self.logging_dir = Path() / 'logs' / 'process.log'
            self.logger = logger
            logzero.loglevel(logzero.INFO)                                           #set a minimum log level: debug, info, warning, error
            logzero.logfile(self.logging_dir, maxBytes=1000000, backupCount=3)       #set rotating log file
            self.logger.info('logger created, constants initialized')
        else:
            '''TODO:cleanup
            tmp = {
                'info': self.print_info,
                'error': self.print_error
                }
            self.logger = dotdict( tmp )
            '''
            m = DotMap()
            m.info = self.print_info
            m.error = self.print_error
            self.logger = m

        # provisioning logic
        self.get_output_mapping_template()
        pass

    def print_info(self, msg): 
        sys.stdout.write(f'INFO: {msg}')
        
    def print_error(self, msg): 
        sys.stdout.write(f'ERROR: {msg}')

    def set_logger(self, path_to_logfile):
        """TODO"""
        pass

    def get_output_mapping_template(self):
        """TODO"""
        if self.output_mapping_template_path:
            if self.output_mapping_template_path.is_file():
                template = Path(self.output_mapping_template_path)
                mapping = ''
                try:
                    with open(template, 'r') as f:
                        mapping = json.load(f)
                    docrec = DocumentRecord()
                    result = docrec.validate_object_attrs(mapping)
                    check_mapping = result['target_attrs_to_remove']==[] and result['target_attrs_to_add']==[]
                except:
                    self.logger.error(f'There was a problem loading the json file.')
                    return False
                else:
                    if check_mapping:
                        self.output_mapping = mapping
                        return True
                    else:
                        return False
                


# default Singleton config across all Factories, instantiated once
ConfigObj = EnteroConfig(apply_logger=False)
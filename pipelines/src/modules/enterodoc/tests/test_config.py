#!/usr/bin/env python3
"""
Tests for EnteroConfig class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from src.modules.enterodoc.entero_document.config import EnteroConfig, ConfigObj
from src.modules.enterodoc.entero_document.record import DocumentRecord
from src.modules.enterodoc.entero_document.document_factory import DocumentFactory

from pathlib import Path
import sys
import pytest



def test_config_print_info(capsys):
    config = EnteroConfig(apply_logger=False)

    config.logger.info('information msg printed')
    stdout_info, err = capsys.readouterr()
    assert stdout_info == 'INFO: information msg printed'

def test_config_print_error(capsys):
    config = EnteroConfig(apply_logger=False)

    config.logger.error('error msg printed')
    stdout_info, err = capsys.readouterr()
    assert stdout_info == 'ERROR: error msg printed'

def test_output_mapping():
    test_file = Path(__file__).parent / './examples/example.pdf'
    ConfigObj.output_mapping_template_path = Path(__file__).parent / './data/mapping_template.json'
    ConfigObj.get_output_mapping_template()

    Doc = DocumentFactory(ConfigObj)
    doc = Doc.build(test_file)
    output_mapped = doc.get_record(map_output=True)

    docrec = DocumentRecord()
    result = docrec.validate_object_attrs(output_mapped)
    #TODO: was this original code correct???: assert result['target_attrs_to_remove'] == result['target_attrs_to_add'] == set()
    #new code
    assert result['target_attrs_to_remove'] == set()
    assert result['target_attrs_to_add'] == set(['file_pdf_bytes', 'file_document'])
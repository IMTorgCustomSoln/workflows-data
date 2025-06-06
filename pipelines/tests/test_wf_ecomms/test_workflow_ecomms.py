#!/usr/bin/env python3
"""
Test ecomms workflow
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from workflows.workflow_ecomms import workflow_ecomms

from pathlib import Path
import tempfile
import shutil


def test_prepare_models():
    check1 = workflow_ecomms.prepare_models()
    assert check1 == True

def test_prepare_workspace():
    with tempfile.TemporaryDirectory() as t_dir:
        input_dir = Path(t_dir) / 'extended_layout'
        source_dir = Path(__file__).parent / 'data_ediscovery' / 'extended_layout'
        shutil.copytree(source_dir, input_dir )
        source_dir = Path(__file__).parent / 'data_orgchart' / 'org1.csv'
        shutil.copy(source_dir, input_dir)

        workflow_ecomms.config['INPUT_DIR'] = input_dir
        check1 = workflow_ecomms.prepare_workspace()
    assert check1 == True

def test_run_individual_dats():
    '''Assumes pre-processing with the following:
    * run `script-combine_dats_to_pickle.py`
    * use `extended_layout/combined_dats.pickle`
    
    '''
    with tempfile.TemporaryDirectory() as t_dir:
        input_dir = Path(t_dir) / 'extended_layout'
        source_dir = Path(__file__).parent / 'data_ediscovery' / 'extended_layout'
        shutil.copytree(source_dir, input_dir )
        source_dir = Path(__file__).parent / 'data_orgchart' / 'org1.csv'
        shutil.copy(source_dir, input_dir)

        workflow_ecomms.config['INPUT_DIR'] = input_dir
        check1 = workflow_ecomms.prepare_workspace()
        check2 = workflow_ecomms.run()
    assert check2 == True

def test_run_combined_dats():
    '''Assumes pre-processing with the following:
    * run `script-combine_dats_to_pickle.py`
    * use `extended_layout/combined_dats.pickle`
    
    '''
    with tempfile.TemporaryDirectory() as t_dir:
        input_dir = Path(t_dir) / 'extended_layout'
        source_dir = Path(__file__).parent / 'data_ediscovery' / 'extended_layout'
        shutil.copytree(source_dir, input_dir )
        source_dir = Path(__file__).parent / 'data_orgchart' / 'org1.csv'
        shutil.copy(source_dir, input_dir)

        workflow_ecomms.config['INPUT_DIR'] = input_dir
        check1 = workflow_ecomms.prepare_workspace()
        check2 = workflow_ecomms.run()
    assert check2 == True

def test_report():
    check = workflow_ecomms.report()
    assert check == True
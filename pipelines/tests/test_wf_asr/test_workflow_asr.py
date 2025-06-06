#!/usr/bin/env python3
"""
Test workflow
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

import pytest

from workflows.workflow_asr import workflow_asr

@pytest.mark.skip(reason='training is too slow on local machine')
def test_workflow_asr_prepare_models():
    check = workflow_asr.prepare_models()
    assert check == True

def test_workflow_asr_prepare_workspace():
    check = workflow_asr.prepare_workspace()
    assert check == True

#@pytest.mark.skip(reason='TODO:fix soundfile, [ref](https://github.com/bastibe/python-soundfile/issues/324)')
def test_workflow_asr_run():
    check = workflow_asr.prepare_workspace()
    check = workflow_asr.run()
    assert check == True

"""
def test_workflow_asr_report_task_status():
    check = workflow_asr.report_task_status()
    assert check == True

def test_workflow_asr_report_map_batch_to_files():
    check = workflow_asr.report_map_batch_to_files()
    assert check == True

def test_workflow_asr_report_process_time_analysis():
    check = workflow_asr.report_process_time_analysis()
    assert check == True
"""
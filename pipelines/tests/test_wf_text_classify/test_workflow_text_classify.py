#!/usr/bin/env python3
"""
Test template (default) workflow

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from workflows.workflow_text_classify import workflow_text_classify


def test_instantiation():
    check1 = workflow_text_classify
    assert check1


def test_prepare_models():
    check1 = workflow_text_classify.prepare_models()
    assert check1 == True
 

def test_run():
    check1 = workflow_text_classify.prepare_workspace()
    check2 = workflow_text_classify.run()
    assert check2 == True
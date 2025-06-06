#!/usr/bin/env python3
"""
Test template (default) workflow

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from workflows.workflow_template import workflow_template


def test_prepare_models():
    check1 = workflow_template.prepare_models()
    assert check1 == True


def test_prepare_workspace():
    check1 = workflow_template.prepare_workspace()
    assert check1 == True


def test_run():
    check1 = workflow_template.prepare_workspace()
    check2 = workflow_template.run()
    assert check2 == True
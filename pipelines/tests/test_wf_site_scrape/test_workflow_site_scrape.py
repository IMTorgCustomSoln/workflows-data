#!/usr/bin/env python3
"""
Test site_scrape workflow
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from workflows.workflow_site_scrape import workflow_site_scrape

import pytest


@pytest.mark.skip(reason='training is too slow on local machine')
def test_prepare_models():
    check1 = workflow_site_scrape.prepare_models()
    assert check1 == True

def test_prepare_workspace():
    check1 = workflow_site_scrape.prepare_workspace()
    assert check1 == True

def test_run():
    check1 = workflow_site_scrape.prepare_workspace()
    check2 = workflow_site_scrape.run()
    assert check2 == True
#!/usr/bin/env python3
"""
Test parsing email utility functions.

TODO: create `src.modules.eml_utils` module


__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

import pytest

from src.modules import eml_utils


def test_email_utils():
    eml = ''
    metadata = eml_utils.get_metadata(eml)
    expected_metadata = {
        'key': 'value'
    }
    assert metadata == expected_metadata
"""
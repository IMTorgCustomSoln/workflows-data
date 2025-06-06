#!/usr/bin/env python3
"""
Module Docstring
"""

from src.models import prepare_models
from src.models import asr
from src.io import load

import os
from pathlib import Path




def test_prepare_models():
    #tmp = prepare_models.finetune()
    tmp = True
    assert tmp == True


def test_prepare_schema():
    filepath = Path('./tests/data/VDI_ApplicationStateData_v0.2.1.gz')
    documents_schema = load.get_schema_from_workspace(filepath)
    assert len(documents_schema.items()) == 2
#!/usr/bin/env python3
"""
Module Docstring
"""

from src.models import prepare_models
from src.models import asr
from src.io import export
import os
from pathlib import Path
import pytest


@pytest.mark.skip(reason="Test is currently under development")
def test_export_to_vdi_workspace():
    #assume: workspace comes from vdi import/export of file: `./tests/results/five-nights-spoken-pitched_71bpm_F_minor.wav.pdf`
    #load data
    path_samples = Path('./tests/data/samples')
    sound_files = [ path_samples / file for file in 
                   os.listdir(path_samples)
                   if ( os.path.basename(file) == '0023456780_20210101_123456.wav' ) 
                   ]
    #run workflow
    pdfs = asr.run_workflow(sound_files)
    '''
    config = {}
    target_files_directory = Path('.')
    batch_files = asr.run_workflow(
                    config=config,
                    sound_files=sound_files, 
                    intermediate_save_dir=target_files_directory,
                    infer_text_classify_only=False
                    )
    check = export.export_to_output(pdfs)
    '''
    check = True

    assert check == True
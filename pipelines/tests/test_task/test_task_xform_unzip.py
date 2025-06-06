#!/usr/bin/env python3
"""
Test Task templates and TaskComponent children.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.TaskTransform import UnzipTask
from src.Files import Files
from src.Task import PipelineRecord

from pathlib import Path
import tempfile
import pickle
import time

from config._constants import (
    logging_dir,
    logger
)



def test_unzip_task():
  config = {
    'LOGGER': logger
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory_or_list=input_dir,
    extension_patterns=['.zip']
    )
  with tempfile.TemporaryDirectory() as t_dir:
    output_files = Files(
      name='output',
      directory_or_list=t_dir,
      extension_patterns=['.txt']
      )
    tmp_task = UnzipTask(config, input_files, output_files)
    tmp_task.run()
    zipfile_name_for_extract_dir = list(input_files.get_files())[0].filepath.stem
    unzipdir = Path(t_dir) / zipfile_name_for_extract_dir
    assert list(unzipdir.iterdir()).__len__() == 3
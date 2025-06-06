#!/usr/bin/env python3
"""
Test Task templates and TaskComponent children.

Tasks support the following:
* get records: `get_next_run_files()`
* run logic: `run()`
* important error handling and logging
* using `log info()`
  - explain record processing steps
  - account for records
* notify logic failures with `error()` 


Tasks should fit one of four templates and be inter-changeable:
* import
  - collect from files
  - collect from external source
* export
  - to basic excel
  - to (interactive VDI client) Workspace
* pipe logic
  - individual records in/out
  - ???groups of records, TODO: review wf_site_scrape
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.Task import Task
from src.Files import Files

from pathlib import Path
import tempfile
import shutil

from config._constants import (
    logging_dir,
    logger
)


def test_task_template():
  #TODO:remainder_paths = tmp_task.get_next_run_files(type='update')
  #setup
  config = {
    'LOGGER': logger
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory_or_list=input_dir,
    extension_patterns=['.txt']
    )
  
  #case-1: all files should be processed
  with tempfile.TemporaryDirectory() as t_dir:
    output_files = Files(
      name='output',
      directory_or_list=t_dir,
      extension_patterns=['.txt']
      )
    name_diff = ''
    tmp_task = Task(config, input_files, output_files, name_diff)
    remainder_paths = tmp_task.get_next_run_file_from_directory(method='same')
    assert len(remainder_paths) == 4

    #case-2: some files previously processed
    with tempfile.TemporaryDirectory() as t_dir:
      for file_number in range(3,5):
        filename = f'test_file{file_number}.txt'
        src_file = input_dir / filename
        dest_file = Path(t_dir) / filename
        shutil.copy(src_file, dest_file)
      output_files = Files(
        name='output',
        directory_or_list=t_dir,
        extension_patterns=['.txt']
        )
      name_diff = ''
      tmp_task = Task(config, input_files, output_files, name_diff)
      remainder_paths = tmp_task.get_next_run_file_from_directory(method='same')
      assert len(remainder_paths) == 2

    #case-3: no files should not be processed
    with tempfile.TemporaryDirectory() as t_dir:
      for file_number in range(1,5):
        filename = f'test_file{file_number}.txt'
        src_file = input_dir / filename
        dest_file = Path(t_dir) / filename
        shutil.copy(src_file, dest_file)
      output_files = Files(
        name='output',
        directory_or_list=t_dir,
        extension_patterns=['.txt']
        )
      name_diff = ''
      tmp_task = Task(config, input_files, output_files, name_diff)
      remainder_paths = tmp_task.get_next_run_file_from_directory(method='same')
      assert len(remainder_paths) == 0
    assert True == True
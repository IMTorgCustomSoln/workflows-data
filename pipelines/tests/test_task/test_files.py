#!/usr/bin/env python3
"""
Test File and Files classes.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.Files import File, Files

import tempfile
from pathlib import Path
import copy


def test_file():
    filepath = Path(__file__).parent / 'data'
    ftypes = ['txt','json']#,'pickle']
    for ftype in ftypes:
        with tempfile.TemporaryDirectory() as t_dir:
            #import existing file
            outpath = Path(t_dir)
            filename = f'test_file1.{ftype}'
            test_file = File(filepath / filename, ftype)
            file_content1 = test_file.load_file(return_content=True)
            file_content2 = test_file.get_content()
            assert file_content1 == file_content2 == test_file.content
            #export content to new file
            new_test_file = copy.deepcopy(test_file)
            new_test_file.filepath = outpath / filename
            result = new_test_file.export_to_file()
            assert new_test_file.filepath.is_file() == result
            #check naming logic
            assert test_file.get_full_path().__str__() != new_test_file.filepath.__str__()
            assert test_file.get_name_and_suffix().__str__() == new_test_file.filepath.name.__str__()
            assert test_file.get_name_without_suffix().__str__() == new_test_file.filepath.stem.__str__()
            assert test_file.get_name_only().__str__() == new_test_file.filepath.name.split('.')[0]
            assert test_file.get_suffix().__str__() == new_test_file.filepath.suffix.__str__()

def test_files_using_files(): 
    results = []
    filepath = Path(__file__).parent / 'data'
    ftypes = ['.txt','.json']
    for ftype in ftypes:
        name = 'test_name'
        directory = filepath
        extension_patterns = [ftype]
        test_files = Files(name, directory, extension_patterns)
        file_generator = test_files.get_files(filetype='full_path')
        lst_files_small_to_large = list(file_generator)
    assert len(lst_files_small_to_large) == 4

def test_files_using_lists():
    name = 'test_name'
    directory_or_list = [
        {'id':'rec-1'},
        {'id':'rec-2'},
        {'id':'rec-3'},
        ]
    extension_patterns = None
    test_files = Files(name, directory_or_list, extension_patterns)
    file_generator = test_files.get_files(filetype='list')
    lst_files_in_order = list(file_generator)
    assert len(lst_files_in_order) == 3



import json
import yaml

def test_json():
    input = {
        "array": [1, 2, 3],
        "boolean": True,
        "color": "gold",
        "null": None,
        "number": 123,
        "object": {"a": "b", "c": "d"},
        "string": "Hello World",
    }
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as fp:
        json.dump(input, fp)
        fp.flush()
        input_file = File(filepath=fp.name, filetype="json")
        output_dict = input_file.load_file(return_content=True)
    assert output_dict == input

def test_yaml():
  input = {
        "array": [1, 2, 3],
        "boolean": True,
        "color": "gold",
        "null": None,
        "number": 123,
        "object": {"a": "b", "c": "d"},
        "string": "Hello World",
    }
  with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml") as fp:
    yaml.dump(input, fp)
    fp.flush()
    input_file = File(filepath=fp.name, filetype="yaml")
    output_dict = input_file.load_file(return_content=True)
    assert output_dict == input
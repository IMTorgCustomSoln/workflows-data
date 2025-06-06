#!/usr/bin/env python3
"""
Utility functions

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from pathlib import Path
import os
import datetime
import json
import gzip, zipfile
import shutil
from collections.abc import Iterable



date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else None
)


def remove_all_extensions_from_filename(filename):
    """Given a filename str, remove all `.*` substrings"""
    new_filename = filename
    ptrn = '.'
    while ptrn in new_filename:
        new_filename = filename.split(ptrn)[0]
    return new_filename


def get_next_batch_from_list(lst, batch_count):
    """...."""
    if type(lst)==list:
        final_idx = int(len(lst)/batch_count-1)
        index_list = list(range( final_idx + 1  ))
        remainder = len(lst)%batch_count
        for idx in index_list:
            init = idx * batch_count
            if remainder>0 and idx==final_idx:
                batch = lst[init: (idx+1) * batch_count+remainder]
            else:
                batch = lst[init: (idx+1) * batch_count]
            yield batch
    else:
        raise TypeError(f'arg lst {lst} is not of type list')


def get_next_batch_from_dict(dictn, batch_count):
    """...."""
    if type(dictn)==dict:
        key_count = len(list(dictn.keys()))
        keys_accumulator = []
        accumulator = []
        for idx, (k,v) in enumerate(dictn.items()):
            keys_accumulator.append(k)
            accumulator.extend( v )
            if len(accumulator)<batch_count and idx<(key_count-1):
                pass
            else:
                batch = {k:v for k,v in dictn.items() if k in keys_accumulator}
                keys_accumulator.clear()
                accumulator.clear()
                yield batch


def decompress_filepath_archives(filepath, extract_dir, target_extension=[]):
    """Return path of all decompressed files.
    
    Check if file is compressed.  Provide file path if it is not.  If it is, then decompress
    to directory, and return files of correct target extension.

    ref: https://stackoverflow.com/questions/3703276/how-to-tell-if-a-file-is-gzip-compressed
    
    def get_dirs_from_path(path):
        result = []
        for file in os.scandir(path):
            if os.path.isdir(file):
                if not any( [x in file.path for x in ['.DS_Store','__MACOSX']] ):
                    result.append(file)
        return result
    """

    #zip format options
    suffixes_archives = ['.gz', '.zip']
    def gz_file(filepath):
        with gzip.open(filepath, 'rb') as f_in:
            f_out_name = f'{filepath}.OUT'
            with open(f_out_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return f_out_name
    
    def zip_file(filepath, extract_dir):
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        files_to_keep = []
        p = extract_dir.rglob("*")
        files = [x for x in p if x.is_file()]
        for file in files:
            if file.suffix in ['.wav', '.mp3']:
                files_to_keep.append(file)
        return files_to_keep

    options = {
        b'\x1f\x8b': gz_file,
        b'PK': zip_file
    }

    #workflow
    filepath = filepath.resolve()
    if not filepath.is_file():
        return [None]
    check_compressed = (False, b'')
    with open(filepath, 'rb') as test_f:
        bytes = test_f.read(2)
        if (bytes == b'\x1f\x8b') or (bytes == b'PK'):
            check_compressed = (True, bytes)

    result = []
    if not check_compressed[0] and filepath.suffix in target_extension:
        result.append(filepath)
    elif not check_compressed[0] and not filepath.suffix in suffixes_archives:
        print(f'filepath bytes does not look like archive file, but contained suffix: {filepath.suffix}')
        result.append(None)
    else:
        if check_compressed[1] in options.keys():
            lst_of_filepaths = options[ check_compressed[1] ](filepath, extract_dir)
            result.extend( lst_of_filepaths)
        else:
            print('ERROR: not a recognized decompression format')
    return result
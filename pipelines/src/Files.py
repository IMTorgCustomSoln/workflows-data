#!/usr/bin/env python3
"""
Files class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from operator import itemgetter
import os
import sys
from pathlib import Path
import json
import gzip
import dill as pickle
import yaml


class File:
    """...
    Manipulate an individual file based upon its format.

    Usage
    ```
    >>> test_file = File(filepath / filename, 'txt')
    >>> file_content = test_file.load_file(return_content=True)
    >>> test_file.filepath = outpath / filename
    >>> result = test_file.export_to_file()
    ```
    """
    types = ['zip','mp3','mp4','wav',
             'txt','md','json','yaml','yml',
             'pickle','schema','workspace','gz'
             ]#TODO:,'archive']

    def __init__(self, filepath, filetype):
        filepath = Path(filepath).resolve()
        if not filepath.is_file():
            with open(filepath, 'w') as f_out:
                pass
        self.filepath = filepath
        if filetype in File.types:
            self.filetype = filetype
        else:
            raise TypeError
        self.content = None

    def __repr__(self):
        return str(self.filepath)

    def __str__(self):
        return self.__repr__()
    
    #naming logic
    def get_full_path(self):
        return self.filepath
    
    def get_name_and_suffix(self):
        return self.filepath.name
    
    def get_name_without_suffix(self):
        return self.filepath.stem
    
    def get_name_only(self):
        result = self.filepath.stem
        if '.' in result:
            result = result.split('.')[0]
        return result
    
    def get_suffix(self):
        return self.filepath.suffix

    #io logic
    def load_file(self, return_content=False):
        """Import from file"""
        #support functions
        def import_without_loading_content(filepath):
            return None
        def import_text(filepath):
            try:
                with open(filepath, 'r') as f_in:
                    text_content = f_in.readlines()
            except Exception as e:
                print(e)
                text_content = None
            return text_content

        def import_json(filepath):
            try:
                with open(filepath, 'r') as f:
                    json_content = json.load(f)
            except Exception as e:
                print(e)
                json_content = None
            return json_content
        
        def import_yaml(filepath):
            try:
                with open(filepath, 'r') as f:
                    yaml_content = yaml.safe_load(f)
            except Exception as e:
                print(e)
                yaml_content = None
            return yaml_content
        
        def import_pickle(filepath):
            try:
                with open(filepath, 'rb') as f:
                    content = pickle.load(f)
            except Exception as e:
                print(e)
                content = None
            return content
            
        def import_workspace(filepath):
            try:
                with gzip.open(filepath, 'rb') as f:
                    workspace_json = json.load(f)
            except Exception as e:
                print(e)
                workspace_json = None
            return workspace_json
        
        options = {
            'zip-.zip': import_without_loading_content,
            'mp3-.mp3': import_without_loading_content,
            'mp4-.mp4': import_without_loading_content,
            'wav-.wav': import_without_loading_content,
            'txt-.txt': import_text,
            'md-.md': import_text,
            'text-.txt': import_text,
            'json-.json': import_json,
            'yaml-.yaml': import_yaml,
            'yaml-.yml': import_yaml,
            'yml-.yml': import_yaml,
            'pickle-.pickle': import_pickle,
            'schema-.json': import_json,
            'workspace-.gz': import_workspace,
            'gz-.gz': import_workspace
        }

        #workflow
        ext = self.filepath.suffix
        key = f'{self.filetype}-{ext}'
        self.content = options[key](self.filepath)
        if return_content:
            return self.get_content()
        else:
            return True

    def get_content(self):
        return self.content
    
    def export_to_file(self):
        """Export to file"""
        #support functions
        def export_text(filepath):
            with open(filepath, 'w') as f_out:
                if type(self.content)==list:
                    for item in self.content:
                        f_out.write(f"{item}\n")
            return True
        
        def export_json(filepath):
            with open(filepath, 'w') as f:
                json.dump(self.content, f)
            return True
        
        def export_pickle(filepath):
            with open(filepath, 'wb') as f:
                pickle.dump(self.content, f)
            return True
        
        '''TODO:complete    
        def import_workspace(filepath):
            with gzip.open(filepath, 'wb') as f:
                workspace_json = json.load(f)
            return workspace_json
        '''
        options = {
            'txt-.txt': export_text,
            'text-.txt': export_text,
            'json-.json': export_json,
            'pickle-.pickle': export_pickle,
            #'schema-.json': import_json,
            #'workspace-.gz': import_workspace
        }
        #workflow
        ext = self.filepath.suffix
        key = f'{self.filetype}-{ext}'
        check = options[key](self.filepath)
        return check


    
    



class Files:
    """TODO: move methods into File class^^^^ and convert this to Factory pattern."""

    def __init__(self, name, directory_or_list, extension_patterns):
        self.name = name
        self.extension_patterns = extension_patterns
        self.directory = None
        self.list = None
        if type(directory_or_list) == list:
            self.list = directory_or_list
        elif Path(directory_or_list).is_dir()==True:
            self.directory = Path(directory_or_list)
        elif Path(directory_or_list).is_dir()==False:
            path = Path(directory_or_list)
            check = Path(path).mkdir()
            if check==False:
                raise ValueError(f'invalid directory path {directory_or_list}')
            self.directory = path

    def get_files(self, filetype='full_path'):
        """Using a generator, this function returns 
        files from smallest to largest by size
        from a directory, or items from list.

        TODO:do I still need filetype? maybe for list input
        """
        def get_list(record):
            return record
        
        #directory used as list (generator)
        if filetype == 'list' and self.list:
            for item in self.list:
                yield item
        #actual files
        else:
            files = [{'file': file, 'size':file.stat().st_size} 
                     for file in self.directory.rglob('*')
                     ]
            files_ascending_size = sorted(files, key=itemgetter('size'))
            files_sorted = [file['file'] for file in files_ascending_size]
            for file in files_sorted:
                check1 = '__MACOSX' not in str(file)
                suffixes = [ext for ext in self.extension_patterns 
                          if ext==file.suffix
                          ]
                check2 = len(suffixes)==1
                if all([check1, check2]):
                    if file.is_file():
                        #path_record = options[filetype](file)       #TODO:is this needed?
                        new_file = File(
                            filepath=file, 
                            filetype=file.suffix.replace('.','')
                            )
                        yield new_file
                    else:
                        raise Exception(f'file {file} is not found')
                else:
                    continue
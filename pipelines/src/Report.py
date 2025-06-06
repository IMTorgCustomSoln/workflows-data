#!/usr/bin/env python3
"""
Report class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"



import pandas as pd

import datetime
from pathlib import Path
import gzip
import shutil
import json


class Report:
    """..."""

    def __init__(self, config, files):
        self.config = config
        self.files = files

    def run(self):
        pass



class TaskStatusReport(Report):
    """...

    * count for each Files
    * remainder between Tasks
    * save list of counts
    """

    def run(self):
        dirpath = self.config['WORKING_DIR'] / 'Reports' 
        dirpath.mkdir(parents=True, exist_ok=True)
        now = datetime.datetime.now().isoformat().replace('T','_').replace(':','-')
        filepath = dirpath / f'report-task_status{now}.txt'

        with open(filepath, 'w') as report:
            next_task = None
            for idx, key in enumerate(self.files.keys()):
                files_1 = list(self.files[key].get_files())
                line = f'Files {key} contains {len(files_1)} files in directory {self.files[key].directory} of extension {self.files[key].extension_patterns}\n'
                self.config['LOGGER'].info(line)
                report.write(line)
                if idx+1 < len(self.files.keys()):
                    next_key = list(self.files.keys())[idx+1]
                    files_2 = list(self.files[next_key].get_files())
                    remaining_files = len(files_2) - len(files_1)
                    line = f'\tnext files {next_key} has {remaining_files} more files than {key}\n'
                    self.config['LOGGER'].info(line)
                    report.write(line)
                    if next_task==None and remaining_files>0:
                        next_task = line
            if next_task:
                report.write('\n\nNext task with remaining files:')
                report.write('\n'+line)
        return True
    

class MapBatchFilesReport(Report):
    """..."""

    def run(self):
        self.config['DIR_ARCHIVE'].mkdir(parents=True, exist_ok=True)
        dirpath = self.config['WORKING_DIR'] / 'Reports' 
        dirpath.mkdir(parents=True, exist_ok=True)
        now = datetime.datetime.now().isoformat().replace('T','_').replace(':','-')
        filepath = dirpath / f'report-batch_files{now}.csv'

        dirs = []
        for dir in self.config['OUTPUT_DIRS']:
            if dir.resolve().is_dir():
                dirs.append(dir.resolve())
            else:
                self.config['LOGGER'].info(f'config incorrectly stated {str(dir)} is a directory with output files')
        
        #copy zip file contents to one location
        output = []
        for dir in dirs:
            zip_files = [file.resolve() for file in dir.glob('**/*')
                         if ('.gz' in str(file) and file.is_file())
                         ]
            for gz in zip_files:
                with gzip.open(gz, 'rb') as f_in:
                    new_path = self.config['DIR_ARCHIVE']/ (gz.stem + '.json')
                    with open(new_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
        
        #collect workspace .json files and extract data
        files = [file for file in self.config['DIR_ARCHIVE'].glob('**/*') 
                 if '.gz' not in str(file) and file.is_file()
                 ]
        document_records = []
        for file in files:
            with open(file, 'rb') as f_in:
                content = json.load(f_in)
                lst = content['documentsIndex']['documents']
                for item in lst:
                    item['batch'] = str(file.name)
                document_records.extend(lst)

        #create records
        records = []
        for doc in document_records:
            result = {}
            result['filepath'] = doc['filepath']
            result['batch'] = doc['batch']
            result['time_asr'] = doc['time_asr']
            result['time_textmdl'] = doc['time_textmdl']
            result['file_size_mb'] = doc['file_size_mb']
            result['body_chars'] = sum(doc['body_chars'].values())
            records.append(result)

        #export to csv
        df = pd.DataFrame(records)
        df.to_csv(filepath, index=False)

        return True
    

class ProcessTimeAnalysisReport(Report):
    """TODO: what is this for, how does it work???"""

    def run(self):
        #find most-recent report
        dirpath = self.config['WORKING_DIR'] / 'Reports'
        if not dirpath.is_dir():
            raise Exception(f'no directory: {dirpath}')
        mx = (None, 0)
        for file in dirpath.glob('**/*'):
            if file.is_file() and 'report-batch_files' in file.stem:
                file_stem_split = file.stem.split('report-batch_files')
                filename_part = file_stem_split[1]
                dt_str = filename_part.split('_')[0] 
                tm_str = f"T{filename_part.split('_')[1].replace('-',':')}"
                dt = int( datetime.datetime.fromisoformat(dt_str+tm_str).timestamp() )
                if mx[1] < dt:
                    mx = (file, dt)

        #get distribution of times
        try:
            df = pd.read_csv(mx[0])
        except Exception as e:
            print(e)
            return False
        return True
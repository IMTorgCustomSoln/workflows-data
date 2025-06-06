#!/usr/bin/env python3
"""
TaskExport classes

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.io import utils
from src.Files import File
from src.Task import Task
from src.models.classification import TextClassifier

import pandas as pd

from pathlib import Path
import time
import copy
import shutil


class UnzipTask(Task):
    """Decompress archive files in a folder"""

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_folder = output.directory
        self.target_extension=['.wav','.mp3','.mp4']

    def run(self):
        sound_files_list = []
        for file in self.get_next_run_file_from_directory():
            extracted_sound_files = utils.decompress_filepath_archives(
                filepath=file.filepath,
                extract_dir=self.target_folder,
                target_extension=self.target_extension
                )
            sound_files_list.extend(extracted_sound_files)
        sound_files_list = [file for file in set(sound_files_list) if file!=None]
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(sound_files_list)} files matching {self.target_extension}")
        return True

class FlattenFileStructureTask(Task):
    """..."""
    def __init__(self, config, input, output):
        super().__init__(config, input, output)
    def get_next_run_file_from_directory(self):
        filelist = []
        for item in list(self.input_files.directory.iterdir()):
            if item.is_dir():
                for file in list(item.iterdir()):
                    if file.is_file():
                        filelist.append(file)
        return filelist
    def run(self):
        sound_files_list = []
        for file in self.get_next_run_file_from_directory():
            outfile_path = self.output_files.directory / file.name
            shutil.copy(file.__str__(), outfile_path)
            sound_files_list.append(outfile_path)
        return True
   
from src.Task import PipelineRecordFactory, PipelineRecord
from itertools import groupby

class CreateMultiUrlRecordTask(Task):
    """TODO:Create a PipelineRecord from a Multiple Urls.
    The pipeline record provides the metadata and final formatted presentation document 
    for application of text models.  The `.presentation_doc` is used for final export.
    """
    def __init__(self, config, input, output):
        super().__init__(config, input, output)

    def get_file_group_id(self, file):
        return file.filepath.stem.split('_')[0]
    
    def run(self):
        files = list(self.get_next_run_file_from_directory())
        files_sorted = [file for file in 
                        sorted(files, key=lambda x: self.get_file_group_id(x))
                        ]
        files_grouped = {key: list(group) for key, group in 
                         groupby(files_sorted, key=lambda x: self.get_file_group_id(x))
                         }
        factory = PipelineRecordFactory()
        for id_group, file_group in files_grouped.items():
            checks = [file.load_file(return_content=False) for file in file_group]
            source_type = 'multiple_files'
            record = factory.create_from_id(id_group, source_type)
            record.root_source = file_group[0].filepath
            record.added_sources = [file.filepath for file in file_group]
            docs = [file.get_content() for file in file_group]
            #TODO: this should be changed in the AsrTask logic
            for doc in docs: 
                doc['filetype']='audio'
                doc['filepath'] = doc['file_path']
                del doc['file_path']
                lines = [f"{chunk['timestamp']}: {chunk['text']}" for chunk in doc['chunks']]
                doc['body'] = '\n'.join(lines)
            record.collected_docs = docs
            check = record.populate_presentation_doc()
            self.pipeline_record_ids.append(record.id)
            filepath = self.export_pipeline_record_to_file(record)
            self.config['LOGGER'].info(f"exported processed file to: {filepath}")
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.pipeline_record_ids)} files matching {self.target_extension}")
        return True

class CreateMultiFileRecordTask(Task):
    """Create a PipelineRecord from a Multiple Files.
    The pipeline record provides the metadata and final formatted presentation document 
    for application of text models.  The `.presentation_doc` is used for final export.
    """
    def __init__(self, config, input, output):
        super().__init__(config, input, output)

    def get_file_group_id(self, file):
        return file.filepath.stem.split('_')[0]
    
    def run(self):
        files = list(self.get_next_run_file_from_directory())
        files_sorted = [file for file in 
                        sorted(files, key=lambda x: self.get_file_group_id(x))
                        ]
        files_grouped = {key: list(group) for key, group in 
                         groupby(files_sorted, key=lambda x: self.get_file_group_id(x))
                         }
        factory = PipelineRecordFactory()
        for id_group, file_group in files_grouped.items():
            checks = [file.load_file(return_content=False) for file in file_group]
            source_type = 'multiple_files'
            record = factory.create_from_id(id_group, source_type)
            record.root_source = file_group[0].filepath
            record.added_sources = [file.filepath for file in file_group]
            docs = [file.get_content() for file in file_group]
            #TODO: this should be changed in the AsrTask logic
            for doc in docs: 
                doc['filetype']='audio'
                doc['filepath'] = doc['file_path']
                del doc['file_path']
                lines = [f"{chunk['timestamp']}: {chunk['text']}" for chunk in doc['chunks']]
                doc['body'] = '\n'.join(lines)
            record.collected_docs = docs
            check = record.populate_presentation_doc()
            self.pipeline_record_ids.append(record.id)
            filepath = self.export_pipeline_record_to_file(record)
            self.config['LOGGER'].info(f"exported processed file to: {filepath}")
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.pipeline_record_ids)} files matching {self.target_extension}")
        return True


class CreateSingleFileRecordTask(Task):
    """Create a PipelineRecord from a Single File.
    The pipeline record provides the metadata and final formatted presentation document 
    for application of text models.  The `.presentation_doc` is used for final export.
    """
    def __init__(self, config, input, output):
        super().__init__(config, input, output)

    def run(self):
        for file in self.get_next_run_file_from_directory():
            check = file.load_file(return_content=False)
            record = file.get_content()
            check = record.populate_presentation_doc()
            self.pipeline_record_ids.append(record.id)
            filepath = self.export_pipeline_record_to_file(record)
            self.config['LOGGER'].info(f"exported processed file to: {filepath}")
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.pipeline_record_ids)} files matching {self.target_extension}")
        return True
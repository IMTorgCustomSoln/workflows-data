#!/usr/bin/env python3
"""
Task class


TODO: apply `get_next_run_files()` to new Tasks
  - but instead of simple review of files, apply to content of files
  - ensure it picks-up at last url - it is currently only designed for last file
  
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Files import File
from src.modules.enterodoc.entero_document.document_factory import DocumentFactory
from src.modules.enterodoc.entero_document.config import EnteroConfig

from pathlib import Path

config = EnteroConfig(apply_logger=False)
DocFactory = DocumentFactory()

class PipelineRecordFactory():
    """TODO: maybe later create different subclasses from PipelineRecords."""
    def __init__(self):
        """..."""
        pass

    def create_from_id(self, id, source_type, root_source=None):
        if source_type not in ['single_file', 'single_url', 'multiple_files']:
            return None
        return PipelineRecord(id, source_type, root_source)
    #def create_from_record(self, record):
    #    pass


class PipelineRecord():
    """..."""
    def __init__(self, id, source_type=None, root_source=None):
        """..."""
        self.id = id
        self.source_type = source_type              #['single_file', 'single_url', 'multiple_files']
        self.root_source = root_source              #grouping
        self.added_sources = []                     #filepaths for manually added documents
        self.collected_docs = []                    #manual and automated collection of docs
        self.presentation_doc = {}                  #combine collected_docs, added_docs into pdf Doc

    def populate_presentation_doc(self):
        """Populate presentation DocumentRecord from collected_docs."""
        if len(self.collected_docs)==0:
            return False
        #TODO: is this necessary? only if self.collected_docs[0] is a complete doc
        elif len(self.collected_docs)==1 and 'page_nos' in self.collected_docs[0].keys():
            self.presentation_doc = self.collected_docs[0]
            return True
        else:
            result = {}
            for key in self.collected_docs[0].keys():
                result[key] = ''
            #TODO:improve logic
            #result['filename_modified'] = f"{result['filename_modified']}, {docrec['filename_modified']}"
            #result['title'] = f"{result['title']}, {docrec['title'][:15]}"
            #result['date'] = min([result['date'], docrec['date']])
            result['filetype'] = ', '.join([doc['filetype'] for doc in self.collected_docs])
            doc = DocFactory.build_from_object(result)
            #doc.record.file_str = self.get_pdf_from_text_str(txt_str=result['clean_body'], type='bytes')
            #Txt = TxtExtracts(config)
            #pdf_bytes  = Txt.txt_string_to_pdf_bytes(txt_str=result['clean_body'])
            #doc.record.file_str = result['clean_body']
            doc.record.filetype = '.txt'
            doc.record.filepath = ', '.join([doc['filepath'] for doc in self.collected_docs])
            page_break = '\n'*5 + '-'*20 + 'END OF DOCUMENT' + '-'*20 + '\n'*2
            doc.record.body = page_break.join([doc['body'] for doc in self.collected_docs])
            doc.record.file_str = doc.record.body
            doc.populate_record()
            self.presentation_doc = doc.get_record()
        return True
    #def export_to_json(self):
    #    """TODO: this is too complicated because of the nested internal classes"""
    #    return True
    def export_to_vdi_workspace(self):
        """..."""
        return True
    def export_to_excel(self):
        """..."""
        return True



class Task:
    """..."""

    def __init__(self, config, input, output, name_diff=''):
        #standard inputs
        self.config = config
        self.input_files = None
        self.output_files = None
        #TODOif type(config) == Config:
        #    self.config = config
        if hasattr(input.directory, 'is_dir'):
            if input.directory.is_dir():
                self.input_files = input
        else:
            raise Exception(f'input not found: {input}')
        if hasattr(output.directory, 'is_dir'):
            if output.directory.is_dir():
                self.output_files = output
        #TODO: elif type(output.list) == list:
        #    self.output_files = output.list
        else:
            raise Exception(f'output not found: {output}')
        self.name_diff = name_diff

        #standard data
        self.target_extension=[]
        self.factory = PipelineRecordFactory()
        self.pipeline_record_ids = []

    def run(self):
        """Run processing steps on input Files"""
        pass

    def create_pipeline_record_from_file(self, file, source_type):
        """Create PipelineRecords from File.
        Typically, this is only needed for initial file import - not intermediate files.
        """
        record = self.factory.create_from_id(
            id=file.filepath.stem, 
            source_type=source_type, 
            root_source=file.filepath
            )
        return record

    def get_next_run_file_from_directory(self, method='same'):
        """Get the remaining files that should be provided to run()
        Each record is an file and they are processed, individually, as opposed
        to multiple records within a file.

        Typically:
        * get input files
        * get output files
        * get remainder files by comparing input to output

        TODO:add generator as output
        TODO:add as function to Files.py and ensure appropriate attr: .name, .stem, etc.
        """
        remainder_files = []
        #case-1:collect filenames in input that are not in output and run the task on unfinished files
        if method == 'same':
            Type = 'name_only'
            input_names = set([file.get_name_only() for file in self.input_files.get_files()])
            #processed_names = set([file.replace(self.name_diff,'') for file in self.output_files.get_files(filetype=Type)])
            processed_names = set([file.get_name_only() for file in self.output_files.get_files()])
            remainder_names = list( input_names.difference(processed_names) )
            if len(remainder_names)>0 and Type == 'name_only':
                remainder_files = [file for file in self.input_files.get_files()
                                    if file.get_name_only() in remainder_names
                                   #if utils.remove_all_extensions_from_filename(file.stem) in remainder_names    #TODO:possible error for workflow_site_scrape
                                   ]
            else:
                pass
        #case-2:a greater number of files in output as input means the task is complete
        elif method == 'update':
            input_count = len( list(self.input_files.get_files()) )
            output_count = len( list(self.output_files.get_files()) )
            if output_count >= input_count:
                pass
            else:
                remainder_files = list(self.input_files.get_files())
        """TODO:the below is archived
        elif method == 'update':      #TODO:improve this idea
            Type = 'name_only'
            input_names = set(self.input_files.get_files(filetype=Type))
            processed_names = set([file.replace(self.name_diff,'') for file in self.output_files.get_files(filetype=Type)])
            if len(processed_names) >= len(input_names):
                remainder_paths = []
            else:
                remainder_paths = list( self.input_files.get_files() )
            return remainder_paths
        """
        return remainder_files

    
    def export_pipeline_record_to_file(self, record, type='pickle'):
        """...
        
        NOTE: only 'pickle' is possible because of complicated structure
        """
        #TODO: add self.name_diff in-case a name change is needed
        filename = record.id
        filepath = self.output_files.directory / f'{filename}.pickle'
        new_file = File(filepath, type)
        new_file.content = record
        check = new_file.export_to_file()
        if check:
            return filepath
        else:
            return False
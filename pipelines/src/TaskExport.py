#!/usr/bin/env python3
"""
TaskExport classes

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Task import Task
from src.Files import File
from src.io import utils

import pandas as pd

from pathlib import Path
import json
import copy
import gzip
import json
from datetime import datetime as dt
import random


class ExportRecordsToReplTask(Task):
    """Export pipeline records to Python repl.  Use with terminal, notebook, etc.
    TODO:fix
    """

    def __init__(self, config, input):
        output = None
        super().__init__(config, input, output)

    def run(self):
        documents = []
        for idx,file in enumerate(self.get_next_run_file_from_directory()):
            check = file.load_file(return_content=False)
            record = file.get_content()
            documents.append(record)
        return documents


class ExportRecordsToFileTask(Task):
    """Export pipeline records to individual files."""

    def __init__(self, config, input, output):
        super().__init__(config, input, output)

    def run(self):
        for idx,file in enumerate(self.get_next_run_file_from_directory()):
            check = file.load_file(return_content=False)
            record = file.get_content()
            self.pipeline_record_ids.append(record.id)
            filepath = self.export_pipeline_record_to_file(record)
            self.config['LOGGER'].info(f"exported processed file to: {filepath}")
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.pipeline_record_ids)} files matching {self.target_extension}")
        return True


class ExportToLocalTableTask(Task):
    """Simple export to local .csv table by flattening pipeline records."""

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self._table_record_template = {
            'id': None,
            'source_type': None,
            'root_source': None,
            'added_sources': None,
            'doc': None
        }

    def add_collected_docs_to_table_record(self, pipeline_record):
        """Add the `.collected_docs` (not the combined `.presentation_doc`) to the table record."""
        records = []
        for doc in pipeline_record.collected_docs:
            temp = copy.deepcopy(self._table_record_template)
            temp['record_id'] = pipeline_record.id
            temp['source_type'] = pipeline_record.source_type
            temp['root_source'] = pipeline_record.root_source
            temp['added_sources'] = ', '.join(pipeline_record.added_sources)
            #TODO:add attributes as k,v to the dict: `.get_display_attr()`
            #these attributes should be selected for a flat file, as opposed to those needed for the VdiWorkspace, such as pdf array
            temp['doc'] = doc
            records.append(temp)
        return records

    def run(self):
        table_records = []
        for file in self.get_next_run_file_from_directory():
            check = file.load_file(return_content=False)
            record = file.get_content()
            table_row_records = self.add_collected_docs_to_table_record(record)
            table_records.extend(table_row_records)
            self.pipeline_record_ids.append(record.id)
        df = pd.DataFrame(table_records)
        #TODO: enable return of DataFrame and make dump to file optional (if no output_files)
        filename = f'export-{self.pipeline_record_ids.__len__()}'
        output_filepath = self.output_files.directory / f'{filename}.csv'
        df.to_csv(output_filepath, index=False)
        self.config['LOGGER'].info(f"end table creation file {output_filepath.__str__()} with {len(self.pipeline_record_ids)} files")
        
        """TODO:check and remove
        #self.target_folder = output.directory
        ....
        filename = 'export'
        unprocessed_files = self.get_next_run_file()
        if len(unprocessed_files)>0:                        #TODO: is this necessary?
            #process by batch of files
            if 'BATCH_COUNT' in list(self.config.keys()):    #TODO: add batch processing
                idx = 0
                for bidx, batch in enumerate( utils.get_next_batch_from_list(unprocessed_files, self.config['BATCH_COUNT']) ):   #TODO:should be added to Task() base class???
                    records = []
                    for fidx, file in enumerate( batch ):
                        record_content = File(filepath=file, filetype='json').load_file(return_content=True)
                        records.append(record_content)
                        self.config['LOGGER'].info(f'text-classification processing for file {idx} - {file.stem}')
                        idx += 1
                    df = pd.DataFrame(records)
                    df.to_csv(self.target_folder / f'{filename}-{bidx}.csv')
            #process by file
            else:
                records = []
                for fidx, file in enumerate( unprocessed_files ):
                    record_content = File(filepath=file, filetype='json').load_file(return_content=True)
                    records.append(record_content)
                    self.config['LOGGER'].info(f'text-classification processing for file {fidx} - {file.stem}')
                df = pd.DataFrame(records)
                df.to_csv(self.target_folder / f'{filename}-{fidx+1}.csv')
        """
        return True
    





class ExportToVdiWorkspaceTask(Task):
    """Export pipeline records to VDI Workspace file."""

    def __init__(self, config, input, output, vdi_schema):
        super().__init__(config, input, output)
        if not vdi_schema:
            vdi_schema = self.config['WORKING_DIR'] / 'workspace_schema_v0.2.1.json'
        self._vdi_schema = File(vdi_schema, filetype='json').load_file(return_content=True)

    #def convert_pipeline_record_to_table_record(self, pipeline_record):
    #    pass

    def run(self):
        workspace_schema = copy.deepcopy(self._vdi_schema)
        workspace_documents = []
        for idx,file in enumerate(self.get_next_run_file_from_directory()):
            check = file.load_file(return_content=False)
            record = file.get_content()
            workspace_document = map_record_presentation_doc_to_workspace_document(self._vdi_schema, record)
            workspace_document['id'] = str(idx)
            workspace_documents.append(workspace_document)
        workspace_schema['documentsIndex']['documents'] = workspace_documents
        filepath_export_wksp_gzip = self.output_files.directory / 'VDI_ApplicationStateData_vTEST.gz'
        with gzip.open(filepath_export_wksp_gzip, 'wb') as f_out:
            f_out.write( bytes(json.dumps(workspace_schema, default=utils.date_handler), encoding='utf8') )    #TODO: datetime handlder, ref: https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
        return True
    

class ExportBatchToVdiWorkspaceTask(Task):
    """Export batch of pipeline records to VDI Workspace file."""

    def __init__(self, config, input, output, vdi_schema):
        super().__init__(config, input, output)
        if not vdi_schema:
            vdi_schema = self.config['WORKING_DIR'] / 'workspace_schema_v0.2.1.json'
        self._vdi_schema = File(vdi_schema, filetype='json').load_file(return_content=True)

    #def convert_pipeline_record_to_table_record(self, pipeline_record):
    #    pass

    def run(self):
        workspace_schema = copy.deepcopy(self._vdi_schema)
        processed_files = self.get_next_run_file_from_directory()
        cnt = 0
        #for idx,file in enumerate(self.get_next_run_file()):
        for batch_id, batch in enumerate( utils.get_next_batch_from_list(processed_files, self.config['BATCH_RECORD_COUNT']) ):
            batch_span = f'{cnt+batch_id}-{len(batch)}'
            dtstamp = datetime.datetime.now().isoformat().split('T')[0].replace('-','')
            filepath_export_wksp_gzip = self.output_files.directory / f'VDI_ApplicationStateData_v0.2.1_{dtstamp}_{batch_span}.gz'
            workspace_documents = []
            for file_id, file in enumerate(batch):
                check = file.load_file(return_content=False)
                record = file.get_content()
                workspace_document = map_record_presentation_doc_to_workspace_document(self._vdi_schema, record)
                workspace_document['id'] = str(file_id)
                workspace_documents.append(workspace_document)
            workspace_schema['documentsIndex']['documents'] = workspace_documents
            with gzip.open(filepath_export_wksp_gzip, 'wb') as f_out:
                f_out.write( bytes(json.dumps(workspace_schema, default=utils.date_handler), encoding='utf8') )    #TODO: datetime handlder, ref: https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
            cnt = len(batch)
            self.config['LOGGER'].info(f"Data processed for batch-{batch_id+1}: {check}")
        return True


def map_record_presentation_doc_to_workspace_document(schema, record):
    """Map the `.presentation_doc` to k,v of workspace document:
    (`workspace_schema['documentsIndex']['documents']`)
    """
    workspace_schema = copy.deepcopy(schema)
    documents_schema = workspace_schema['documentsIndex']['documents']
    document_record = copy.deepcopy(documents_schema)
    doc = record.presentation_doc

    #TODO
    document_record['filetype'] = 'text'   #TODO: still wrong - where to put in code organization???
    document_record['length_lines'] = None   #TODO: utils.length_lines(???)
    #document_record['clean_body'] = ''.join(doc['clean_body'])    #TODO: utils.get_clean_text

    #raw
    document_record['id'] = None
    document_record['reference_number'] = str(random.randint(1000000001, 9999999999))
    document_record['body_chars'] = {}                          #{idx+1: len(page) for idx, page in enumerate(pdf_pages.values())}                 #{1: 3958, 2: 3747, 3: 4156, 4: 4111,
    document_record['body_pages'] = doc['body_pages']           #{1: 'Weakly-Supervised Questions for Zero-Shot Relation…a- arXiv:2301.09640v1 [cs.CL] 21 Jan 2023<br><br>', 2: 'tive approach without using any gold question temp…et al., 2018) with unanswerable questions<br><br>', 3: 'by generating a special unknown token in the out- …ng training. These spurious questions can<br><b
    dt_extracted = dt.strptime(doc['date'], '%Y-%m-%d')
    document_record['date_created'] = doc['date']+'T00:00:00'          #TODO:"2020-03-01T00:00:00"
    #document_record['length_lines'] = None    #0
    #document_record['length_lines_array'] = None    #[26, 26, 7, 
    document_record['page_nos'] = doc['page_nos']
    document_record['length_lines'] = doc['length_lines']

    #important
    document_record['dataArrayKey'] = None
    document_record['dataArray'] = {idx: item for idx,item in enumerate(doc['file_uint8arr'])}                     #TODO: {"0":37, "1": 80, ...   or [37, 80, ...]
    document_record['toc'] = doc['toc']
    document_record['pp_toc'] = ""
    document_record['clean_body'] = doc['clean_body']     #PREVIOUSLY WRONG:' '.join(doc['clean_body'])          #NOTE:created during workspace import

    #file info
    document_record['file_extension'] = doc['file_extension']
    document_record['file_size_mb'] = doc['file_size_mb']
    document_record['filename_original'] = doc['filename_original']                             #TODO:add suffix
    doc['title'] = doc['title'] if type(doc['title'])==str else ''
    document_record['title'] = doc['title'] if len(doc['title'])<50 else doc['title'][:50]
    document_record['filepath'] = doc['filepath']
    document_record['filetype'] = doc['filetype']
    document_record['author'] = doc['author']
    document_record['subject'] = doc['subject']

    #models
    if 'models' in doc.keys():
        highest_pred_target = max(doc['models'], key=lambda model: model['pred'] if 'pred' in model.keys() else 0 )
        hit_count = len([model for model in doc['models'] if model!={}])
        models = doc['models']
        time_asr = doc['time_asr']
        time_textmdl = doc['time_textmdl']
    else:
        highest_pred_target = {}
        hit_count = None
        models = None
        time_asr = None
        time_textmdl = None
    document_record['sort_key'] = highest_pred_target['pred'] if 'pred' in highest_pred_target.keys() else 0.0
    document_record['hit_count'] = hit_count
    document_record['time_asr'] = time_asr
    document_record['time_textmdl'] = time_textmdl

    #display
    document_record['snippets'] = []
    document_record['summary'] = "TODO:summary"
    document_record['_showDetails'] = False
    document_record['_activeDetailsTab'] = 0
    document_record['models'] = models
    return document_record







import sys
import datetime
from src.io import export

class ExportEcommsToVdiWorkspaceTask(Task):
    """Export files to a VDI Workspace file."""

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_folder = output.directory

    def run(self):
        #load schema
        workspace_filepath = self.config['WORKING_DIR'] / 'workspace_schema_v0.2.1.json'
        if workspace_filepath.is_file():
            self.config['WORKSPACE_SCHEMA'] = File(workspace_filepath, 'schema').load_file(return_content=True)
            self.config['LOGGER'].info(f"workspace schema loaded")
        else:
            self.config['LOGGER'].info(f"run prepare() to load workspace schema")
            sys.exit()

        #export by batch
        processed_files = self.get_next_run_file_from_directory()
        cnt = 0
        for idx, batch in enumerate( utils.get_next_batch_from_list(processed_files, self.config['BATCH_COUNT']) ):
            self.config['LOGGER'].info("begin export")
            batch_span = f'{cnt+idx}-{len(batch)}'
            dt = datetime.datetime.now().isoformat().split('T')[0].replace('-','')
            export_filepath = self.target_folder / f'VDI_ApplicationStateData_v0.2.1_{dt}_{batch_span}.gz'    #v0.2.1_YYYYMMDD_0-100.gz
            dialogues = [File(file, 'json').load_file(return_content=True)
                         for file in batch
                         ]
            check = export.export_ecomms_dialogues_to_output(
                schema=self.config['WORKSPACE_SCHEMA'], 
                dialogues=dialogues, 
                filepath=export_filepath, 
                output_type='vdi_workspace'
                )
            cnt = len(batch)
            self.config['LOGGER'].info(f"Data processed for batch-{idx+1}: {check}")
        return True
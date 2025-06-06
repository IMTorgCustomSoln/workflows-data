#!/usr/bin/env python3
"""
Document and DocumentFactory class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from .record import record_attrs, DocumentTemplate, DocumentRecord
from .extractor import Extractor
from .utils import bytes_to_megabytes

import shutil
import itertools
import copy



class Document:
    """Primary Document class for the module.  Built with DocumentFactory().build()
    :params documented in __init__()

    Determine file_type and apply appropriate extractions and processing to provision `_record` attributes.

    Usage::
        >>> Doc = DocumentFactory()
        >>> test_file = Path('tests/examples/example.pdf')
        >>> doc = Doc.build(test_file)
        >>> docrec = DocumentRecord()
        >>> result = docrec.validate_object_attrs(doc)
    
    TODO:I added attrs: {'file_document', 'file_str'}, where should these be organized?
    """
    _spacyNlp = None
    #TODO:add lists of extensions, i.e. `.doc` with `.docx`
    _useable_suffixes = {'.html': Extractor.extract_from_html,
                         '.pdf': Extractor.extract_from_pdf,
                         '.txt': Extractor.extract_from_txt,
                         '.md': Extractor.extract_from_txt,
                         '.ppt': None,
                         '.docx': None,
                         '.csv': None,
                         '.xlsx': None
                        }
    #TODO:_record_attrs = record_attrs
    _record_attrs = record_attrs

    #TODO: word_extensions = [".doc", ".odt", ".rtf", ".docx", ".dotm", ".docm"]
    #TODO: ppt_extensions = [".ppt", ".pptx"]
    #TODO: initialize all attributes before running methods

    def __init__(self, path_or_url_format, path_or_url_obj, logger, applySpacy, output_mapping):
        """Args:
                path_or_url_format - 'url', 'path'
                path_or_url_obj - <UniformResourceLocator>, <PosixPath>
                logger - EnteroConfig.logger
                applySpacy - EnteroConfig.applySpacy
                output_mapping - TODO

        private vars - `self._<name>`
        record vars - `self.record.<name>`
        """
        self._file_format = path_or_url_format
        self._obj = path_or_url_obj
        self._logger = logger
        self._applySpacy = applySpacy
        self._output_mapping = output_mapping
        self.record = DocumentTemplate()

        # set file indexing and raw attrs
        if self._file_format=='url':
            url = self._obj
            self.record.filepath = url
            self.record.filename_original = url.get_filename()
            self.record.file_extension = url.get_suffix()
            self.record.filetype = '.'+url.file_format
            self.record.file_str = url.file_str
            self.record.file_document = url.file_document      #TODO:add file_document to filepath as FileImitator, [ref](https://stackoverflow.com/questions/40391487/how-to-create-a-python-object-that-be-passed-to-be-open-as-a-file)
            self.record.file_size_mb = url.file_size_mb

        elif self._file_format=='path':
            path = self._obj
            self.record.filepath = path
            self.record.filename_original = path.stem
            self.record.file_extension = path.suffix
            self.record.file_str = None
            self.record.file_document = None
            self.record.filetype, self.record.file_size_mb = self.determine_file_info()

        elif self._file_format=='object':
            path = self._obj
            self.record.filepath = None
            self.record.filename_original = None
            self.record.file_extension = '.pdf'
            self.record.file_str = None
            self.record.file_document = None
            self.record.filetype, self.record.file_size_mb = '.pdf', None

    def build_new(self):
        """Build new Document from arguments."""
        # process inferred metadata
        self.set_filename_modified()
        if self.record.filetype == None:
            self._logger.info(f"Document `{self.record.filename_original}` attributes could not be populated because filetype {self.record.filepath.suffix} is not supported")
            return None
        record_extracts = self.run_extraction_pipeline()
        self.update_record_attrs(record_extracts, replace=False)

        # process searchable text
        self._docs = None
        if self.record.body and self._applySpacy:
            self.run_spacy_pipeline(body=self.record.body)
        
        # compare current and template attrs
        missing_attr = self.get_missing_attributes()
        cnt = missing_attr.__len__()
        self._logger.info(f"Document `{self.record.filename_original}` populated with {cnt} missing (None) attributes: {missing_attr}")

    def build_from_record(self, record):
        """Populate new Document from attribute record from a different Document."""
        d = self.__dict__
        missing = []
        for k,v in d.items():
            if hasattr(record, k):
                d[k] = record[k]
            else:
                missing.append(k)
        #TODO:is this doing what I want it to???
        self._logger.info(f'While `build_from_record()` the following keys were missing from the previous record: {missing}')

    def populate_record(self):
        """Populate empty Document from `self.extraction_pipeline()`."""
        record_extracts = self.run_extraction_pipeline()
        self.update_record_attrs(record_extracts, replace=False)
        return True

    def __eq__(self, other) :
        """Provide `==` operator, 
        ref: https://stackoverflow.com/questions/6423814/is-there-a-way-to-check-if-two-object-contain-the-same-values-in-each-of-their-v
        """
        copy_self = copy.deepcopy(self.record.__dict__)
        copy_other = copy.deepcopy(other.record.__dict__)
        return copy_self == copy_other

    def _asdict(self):
        """Return dict of record attributes."""
        result = {}
        for attr in self._record_attrs:
            val = getattr(self, attr)
            result[attr] = val
        return result

    def determine_file_info(self):
        """Determine file system information for the file.

        The format (extension) of the filepath is important 
        to determine what extraction method to use.  Additional
        information is also included.
        """
        path = self.record.filepath
        if not self.record.filetype:
            if path.suffix in list(self._useable_suffixes.keys()):
                filetype = path.suffix
            else:
                filetype = None
        else:
            filetype = self.record.filetype

        if not self.record.file_size_mb:
            size_in_mb = int(path.stat().st_size) * 1e-6
            filesize = round(size_in_mb, ndigits=3)
        else:
            filesize = self.record.file_size_mb
        return filetype, filesize
    
    def set_filename_modified(self):
        """Determine `self.filename_modified` for the new file name."""
        file_extension = '' if self.record.file_extension == None else self.record.file_extension
        if self.record.title:
            self.record.filename_modified = self.record.title + file_extension
        else:
            self.record.filename_modified = self.record.filename_original + file_extension
        return 1
    
    def update_record_attrs(self, record_extracts, replace=True):
        """Update the Document's record attributes.
        Use `replace` to select whether to overwrite current
        attribute values.
        """
        for k,v in record_extracts.items():
            if hasattr(self.record, k):
                if replace==False:
                    current_value = getattr(self.record,k)
                    if not current_value:
                        setattr(self.record, k, v)
                if replace==True:
                    setattr(self.record, k, v)

    def run_extraction_pipeline(self):
        """Apply extractions appropriate for the format.

        Don't throw exception if not an available 
        filetype.  Instead, fail gracefully with result
        of only None values.
        """
        result = {}
        check0 = self.record.filetype in self._useable_suffixes.keys()
        check1 = True if self._useable_suffixes[self.record.filetype] and check0 else None
        if check1:
            fun_call = self._useable_suffixes[self.record.filetype]
            result = (fun_call)(self.record)
            #TODO:improve logic
            #result["file_text"] = self.record["file_document"].text
            #result["page_nos"] = len(rdr.pages)
            #result["body_pages"] = [rdr.pages[idx].extract_text() for idx in range(len(rdr.pages))]
            result['pp_toc'] = self.pretty_print_toc( result['toc'] )
            result['body_chars'] = {k:len(v) for k,v in result['body_pages'].items()}
            result['file_size_mb'] = bytes_to_megabytes(len(result['file_pdf_bytes']))
            result['length_lines'] = 0    #TODO:utils.length_lines(???)
        else:
            self._logger.info("filetype (extension) is not one of the supported suffixes")
            result['pp_toc'] = ''
        return result

    def run_spacy_pipeline(self, body):
        """Run nlp pipeline to apply tags.
        
        Get the number of sentences (`length_lines`) for the excerpts made,
        which is based on `utils.MAX_PAGE_EXTRACT`.
        """
        docs = self._spacyNlp.pipe(body)
        docs, gen1 = itertools.tee(docs)
        self._docs = docs
        length_lines = 0
        for doc in gen1:
            length_lines += len(list(doc.sents))
        self.length_lines = length_lines
        return 1

    def get_missing_attributes(self):
        """Count the number of attributes not populated after initialization
        pipelines are run."""
        result = {}
        missing = []
        for attr in self._record_attrs:
            val = getattr(self.record, attr)
            result[attr] = val
            print(f'{attr}-{val}')
            if val == None: 
                missing.append(attr)
        return missing
    
    def get_record(self, map_output=False, json_ready=True):
        """Get record as DocumentRecord or (json-ready) dict
        
        Notes:
        * filetype - '.html','.pdf'
        * file_str - raw string
        * file_document - bs4, pdf
        * file_text - visible text
        * file_pdf_bytes - converted to pdf, then bytes
        * file_uint8arr - pdf_bytes to js uInt8Array
        """
        #create dict
        output = {}
        for k,v in self.record.items():
            if map_output and self._output_mapping:
                newKey = self._output_mapping[k]        #TODO:need mapping
                output[newKey] = v
            else:
                output[k] = v
        #prepare for json
        if json_ready==True:
            output['filepath'] = str(output['filepath'])
            output['date'] = str(output['date'])
            output["file_str"] = str(output["file_str"])
            del output['file_document']
            del output['file_pdf_bytes'] 
        return output

    def save_modified_file(self, filepath_modified):
        """Copy the original file with the modified name.
        
        This is the only method not automatically performed on initialization
        because it is making modification outside the object.
        """
        filepath_dst = filepath_modified / self.record.filename_modified
        shutil.copy(src=self.record.filepath,
                    dst=filepath_dst
        )
        return 1

    def pretty_print_toc(self, toc, file_or_screen='file'):
        """Print table of contents (toc) in human-readable manner."""
        outlines = toc
        if outlines:
            if file_or_screen == 'screen':
                #TODO:for(level,title,dest,a,se) in outlines:
                for(level,title,dest) in outlines:
                    print( ' '.join(title.split(' ')[1:]) )

            elif file_or_screen=='file':              
                outline_lst = []
                for(level,title,dest) in outlines:
                    item = f'{title}'
                    outline_lst.append(item)
                outline_html_str = ('<br>').join(outline_lst)
                return outline_html_str

            else:
                return 0
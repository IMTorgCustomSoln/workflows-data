#!/usr/bin/env python3
"""
Extractor class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from .config import ConfigObj
from .extracts_pdf import PdfExtracts
from .extracts_html import HtmlExtracts
from .extracts_txt import TxtExtracts
#from .office_extracts import OfficeExtracts



class ExtractsSuite:
    """Singleton of all `extracts_*.py` logic.
    :param config: object of type EnteroConfig

    Tightly-coupled to Document attributes through `parent` variable.

    Usage::
        Selected from within Document and applied for use with each file_type
        _useable_suffixes = {'.html': Extractor.extract_from_html,
                             '.pdf': Extractor.extract_from_pdf,
                             '.txt': Extractor.extract_from_txt,
                             '.ppt': None,
                             '.docx': None,
                             '.csv': None,
                             '.xlsx': None
                            }
    """

    def __init__(self, config):
        self.Pdf = PdfExtracts(config)
        self.Html = HtmlExtracts(config)
        self.Txt = TxtExtracts(config)


    def extract_from_pdf(self, record):
        pdf_stream = ''
        if not record.file_str:
            with open(record.filepath, 'rb') as f:
                pdf_stream = f.read()
        else:
            pdf_stream = record.file_str
        result_record = self.Pdf.extract_from_pdf_string(pdf_stream)
        if result_record["file_pdf_bytes"]:
            result_record["file_uint8arr"] = [x for x in result_record["file_pdf_bytes"]]
        else: 
            result_record["file_uint8arr"] = None
        return result_record


    def extract_from_html(self, record):
        """..."""
        #get html_str
        html_str = ''
        if record.file_str:
            html_str = record.file_str
        else:
            with open(record.filepath, 'r') as f:
                html_str = f.read()
        #html_string to pdf
        pdf_bytes = self.Html.html_string_to_pdf_bytes(html_str=html_str, 
                                                        url_path=None, 
                                                        record=record
                                                        )
        if not pdf_bytes:
            from src.io.export import text_to_pdf
            pdf_bytes = text_to_pdf(record.file_document.text)

        #get record attributes from pdf
        result_record = self.Pdf.extract_from_pdf_string(pdf_stream=pdf_bytes)
        result_record["file_uint8arr"] = [x for x in result_record["file_pdf_bytes"]]
        return result_record
    

    def extract_from_txt(self, record):
        """Extract information from filetype 'text'
        Note: convert text to pdf, then apply `extract_from_pdf()` where possible.
        """
        #get txt_str
        txt_str = ''
        if record.file_str:
            txt_str = record.file_str    #TODO: txt_str = io.StringIO(record.file_str)
        else:
            with open(record.filepath, 'r') as f:
                txt_str = f.read()
        #txt_string to pdf
        pdf_bytes = self.Txt.txt_string_to_pdf_bytes(txt_str=txt_str, record=record)
        if not pdf_bytes:
            from src.io.export import text_to_pdf
            pdf_bytes = text_to_pdf(record.file_document.text)

        #get record attributes from pdf
        result_record = self.Pdf.extract_from_pdf_string(pdf_stream=pdf_bytes)
        result_record["file_uint8arr"] = [x for x in result_record["file_pdf_bytes"]]
        result_record['filetype'] = 'text'
        return result_record


# export
#config = Config(apply_logger=False)
Extractor = ExtractsSuite(ConfigObj)
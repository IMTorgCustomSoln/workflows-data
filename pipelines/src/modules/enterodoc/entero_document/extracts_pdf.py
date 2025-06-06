#!/usr/bin/env python3
"""
Extraction functions for each file type to be used with Document class

Notes on getting text:
* assume docs are max 100 pages - only get N bytes of string to conserve memory
* `text_lst` itesms should be in batches, such as doc pages or paragraphs (don't mess up sentenceizer)
* `docs = spacy.pipe(text_lst, n_process=-1)`   #as many processes as CPUs
* resulting docs is a generator, but return as list `list(docs)`, currently
* then Document performs text processing

TODO:minor tasks
* convert all file types to pdf, then extract using pdf.miner
* limit retrieval to N excerpts
* use optimal storage: `from collections import namedtuple`   #ref: https://stackoverflow.com/questions/1336791/dictionary-vs-object-which-is-more-efficient-and-why

#TODO:review PyMuPDf
#PyMuPDF is AGPL
#PyMuPDF is faster than pdfminer, [ref](https://medium.com/social-impact-analytics/comparing-4-methods-for-pdf-text-extraction-in-python-fd34531034f)
#PyMuPDF extracts ToC if the PDF consists of Bookmarks. Otherwise it only results in an empty list.
#PyMuPDF appears to extract ToC better, but look into open-license methods: https://stackoverflow.com/questions/54303318/read-all-bookmarks-from-a-pdf-document-and-create-a-dictionary-with-pagenumber-a
#pikepdf may be an alternative for getting ToC => it gets bookmarks, but sometimes not page_location

#TODO:add ocr
#OCRmyPDF uses pikepdf, but is MPL-2.0 license (pikepdf also), which requires commercial sales to be open-sourced if files are distributed
#in server SAAS solution, no files are distributed - so probably good [ref](https://opensource.stackexchange.com/questions/9407/do-i-have-to-disclose-changes-made-to-mpl-2-0-licensed-code-running-on-server#:~:text=For%20server-side%20software%20offered%20in%20a%20SaaS%20setting%2C,the%20source%20code%20available%20alongside%20any%20binary%20distribution.)
#madmaze/pytesseract is Apache-2.0 license
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from .record import record_attrs, DocumentTemplate
from .utils import timeout, get_clean_text

#pdf
import pypdf
import pdftitle                                                                 #uses pdfminer
from pdfminer.high_level import extract_text as pdf_extract_text                #uses pdfminer.six, problem TODO???
from pdfminer.high_level import extract_pages as pdf_extract_pages
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1

import fitz
from pikepdf import Pdf

import datetime
import io
import time


class PdfExtracts:
    """Singleton of extract logic for pdf format.
    
    """

    def __init__(self, config):
        self.config = config

    def extract_from_pdf_string(self, pdf_stream):
        """TODO"""
        time0 = time.time()
        record = DocumentTemplate()
        if len(record.keys())==0:
            for key in record_attrs:
                record[key] = None
        #pymupdf
        try:
            with fitz.open(stream = pdf_stream) as ingest:
                if not record['author']:
                    meta = ingest.metadata
                    record['title'] = meta['title']
                    record['author'] = meta['author']
                    record['subject'] = meta['subject']
                    record['keywords'] = meta['keywords']
                    record['page_nos'] = len(ingest)
                    if 'D:' in meta['creationDate']:
                        Ymd = meta['creationDate'].split('D:')[1][:8] 
                        record['date'] = datetime.datetime.strptime(Ymd, "%Y%m%d").date()
                    else:
                        record['date'] = None
                #pdf.miner
                if not record['title']:
                    record['title'] = self.get_pdf_title(pdf_stream)
                if not record['toc']:
                    record['toc'] = ingest.get_toc()

                page_list_length = record['page_nos'] - 1
                if self.config.MAX_PAGE_EXTRACT:
                    if page_list_length <= self.config.MAX_PAGE_EXTRACT: 
                        number_of_pages_to_extract_text = page_list_length
                    else: 
                        number_of_pages_to_extract_text = self.config.MAX_PAGE_EXTRACT 
                else:
                    number_of_pages_to_extract_text = page_list_length

                
                record["file_pdf_bytes"] = pdf_stream
                #pymupdf
                if not record['body']:
                    record['body'], record["body_pages"] = self.get_pdf_raw_text(pdf_stream=ingest, 
                                                            mode='pymupdf', 
                                                            number_of_pages_to_extract_text=number_of_pages_to_extract_text, 
                                                            )
                #pdf.miner
                if not record['body']:
                    record['body'], record["body_pages"] = self.get_pdf_raw_text(pdf_stream=pdf_stream, 
                                                            mode='pdf.miner', 
                                                            number_of_pages_to_extract_text=number_of_pages_to_extract_text,  
                                                            )
            record['clean_body'] = get_clean_text(record['body'])
        except:
            self.config.logger.info('there was an error extract_from_pdf_string()')
            
        self.config.logger.info(f'Convert stream to pdf took: {time.time() - time0} secs')
        return record


    def get_pdf_title(self, pdf_stream,):
        """Try different methods to extract the title from the pdf."""
        title = None
        tmp = io.BytesIO(pdf_stream)
        #pdf.miner
        try:
            with timeout(seconds=5):
                title = pdftitle.get_title_from_io(tmp)
        except Exception:
            self.config.logger.info("`pdftitle` module threw error getting title")
            pass
        
        #pypdf
        if not title:
            try:
                with timeout(seconds=5):
                    pdfReader = pypdf.PdfReader(tmp)
                    title = pdfReader.metadata['/Title']
            except Exception:
                self.config.logger.info("`pypdf` module threw error getting title")
                pass

        return title


    def get_pdf_raw_text(self, pdf_stream, mode, number_of_pages_to_extract_text):
        """Get raw text from pdf.
        Ensure only a limited number of pages are extracted.
        """
        raw_text = ''
        body_pages = {}

        #pymupdf
        if mode == 'pymupdf':
            ingest = pdf_stream
            try:
                #with fitz.open(pdf_stream) as doc:
                pg_idx = 0
                for page in ingest:
                    if pg_idx <= number_of_pages_to_extract_text:
                        page_text = page.get_text()
                        raw_text += page_text
                        body_pages[pg_idx + 1] = page_text
                        pg_idx += 1
            except Exception:
                pass    

        #pdf.miner
        if raw_text == '' and mode == 'pdf.miner':
            tmp = io.BytesIO(pdf_stream)
            try:
                with timeout(seconds=self.config.MAX_TIME_SEC):
                    raw_text = pdf_extract_text(pdf_file=tmp,
                                                maxpages=number_of_pages_to_extract_text
                                                )
                    #TODO: body_pages = ???
            except Exception:
                self.config.logger.info(f'It took more than {self.config.MAX_TIME_SEC}sec to extract text')
            if not raw_text=='':
                raw_text = pdf_extract_text(pdf_file=tmp,
                                            maxpages=1
                                            )
        return raw_text, body_pages        

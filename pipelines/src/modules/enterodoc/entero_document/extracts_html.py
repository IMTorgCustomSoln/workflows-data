#!/usr/bin/env python3
"""
Extraction functions for each file type to be used with Document class

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"


from .record import record_attrs, DocumentTemplate

#html
import bs4
#from xhtml2pdf import pisa 
import weasyprint
#import pypdf

import io
import time


class HtmlExtracts:
    """Singleton of extract logic for pdf format.
    
    TODO:check html_str is bs4 compliant
    TODO:check with url_path
    """

    def __init__(self, config):
        self.config = config


    def html_string_to_pdf_bytes(self, html_str, url_path=None, record=DocumentTemplate()):
        """Generate a pdf:str and associated record metadata (title, toc, ...) 
        from html string content.
        """
        time0 = time.time()

        context = {}
        pdf_bytes = None
        result = io.BytesIO()
        if len(record.keys())==0:
            for key in record_attrs:
                record[key] = None
        meta_attrs = ["title", "author", "subject", "keywords"]

        html = io.StringIO(html_str) 
        """
        try:
            context = pisa.pisaDocument(src=html,
                                     dest=result,
                                     path=url_path)
            if not context.err:
                print("xhtml2pdf created PDF")
                if context:
                    for key in meta_attrs:
                        record[key] = context.meta[key]
                        pdf_bytes = result.getvalue()
                
        except:
            print("Error: unable to create the PDF")
        """
        if not pdf_bytes:
            pdf_bytes = weasyprint.HTML(html).write_pdf()
        
        time1 = time.time()
        self.config.logger.info(f'Convert html to pdf took: {time1 - time0} secs')
        #return context, pdf_bytes
        return pdf_bytes
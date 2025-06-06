#!/usr/bin/env python3
"""
Extraction functions for each file type to be used with Document class

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"


from .record import record_attrs, DocumentTemplate

import textwrap
from fpdf import FPDF

import io
import time


class TxtExtracts:
    """Singleton of extract logic for txt format.
    
    """

    def __init__(self, config):
        self.config = config


    def txt_string_to_pdf_bytes(self, txt_str, record=DocumentTemplate()):
        """Generate a pdf:str and associated record metadata (title, toc, ...) 
        from text string content.
        """
        time0 = time.time()

        context = {}
        pdf_bytes = None
        result = io.BytesIO()
        if len(record.keys())==0:
            for key in record_attrs:
                record[key] = None
        meta_attrs = ["title", "author", "subject", "keywords"]

        text = txt_str.encode('ascii', 'ignore').decode('ascii')
        if not pdf_bytes:
            a4_width_mm = 210
            pt_to_mm = 0.35
            fontsize_pt = 10
            fontsize_mm = fontsize_pt * pt_to_mm
            margin_bottom_mm = 10
            character_width_mm = 7 * pt_to_mm
            width_text = a4_width_mm / character_width_mm

            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.set_auto_page_break(True, margin=margin_bottom_mm)
            pdf.add_page()
            pdf.set_font(family='Courier', size=fontsize_pt)
            if '\n' in text:
                splitted = text.split('\n')
            else:
                splitted = [text]
            for line in splitted:
                try:
                    lines = textwrap.wrap(line, width_text)
                except Exception as e:
                    print(e)
                    lines = [line[:int(width_text)]]
                if len(lines) == 0:
                    pdf.ln()
                for wrap in lines:
                    pdf.cell(0, fontsize_mm, wrap, ln=1)
            #pdf_bytes = weasyprint.HTML(html).write_pdf()
            pdf_bytes = pdf.output("output_file.pdf", 'S').encode('latin-1')
        
        time1 = time.time()
        self.config.logger.info(f'Convert text to pdf took: {time1 - time0} secs')
        return pdf_bytes
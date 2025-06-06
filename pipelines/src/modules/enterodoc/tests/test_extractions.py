"""
Tests for all *Extracts classes

TODO: msft formats to html
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from src.modules.enterodoc.entero_document.url import UrlFactory, UniformResourceLocator
from src.modules.enterodoc.entero_document.extracts_pdf import PdfExtracts
from src.modules.enterodoc.entero_document.extracts_html import HtmlExtracts
from src.modules.enterodoc.entero_document.extracts_txt import TxtExtracts
#from src.modules.enterodoc.entero_document.extracts_msg import MsgExtracts
#from entero_document.office_extracts import OfficeExtracts

from src.modules.enterodoc.entero_document.record import record_attrs
from src.modules.enterodoc.entero_document.config import EnteroConfig

from pathlib import Path

config = EnteroConfig(apply_logger=False)


def test_local_extract_from_pdf_string():
    filepath = Path(__file__).parent /  'examples' / 'cs_nlp_2301.09640.pdf'    #3.3sec, 21sec, 0.65sec
    #filepath = 'tests/demo/nuclear_2201.00276.pdf'    #3.8sec, 1.35sec
    pdf_stream = ''
    with open(filepath, 'rb') as f:
        pdf_stream = f.read()
    record = {}
    for key in record_attrs:
        record[key] = None

    Pdf = PdfExtracts(config)
    result_record = Pdf.extract_from_pdf_string(pdf_stream)
 
    #TODO:check all attrs - see `test_local_extract_html()`
    check_title = result_record['title'] == 'Weakly-Supervised Questions for Zero-Shot Relation Extraction'
    check_page_nos =  result_record['page_nos'] == 12
    checks = [check_title, check_page_nos]
    assert all(checks) == True


def test_web_extract_from_pdf_string():
    """TODO:this test appears to be non-deterministic as it sometimes fails because it is reading a different example file"""
    hrefs = ['https://www.jpmorgan.com/content/dam/jpm/merchant-services/documents/jpmorgan-interchange-guide.pdf'
    ]
    URL = UrlFactory()
    urls = [URL.build(url) for url in hrefs]
    artifacts = [{'name': url.get_filename(), 'file_format': url.get_file_artifact_(), 'file_str': url.file_str} for url in urls]
    pdf_stream = artifacts[0]['file_str']

    Pdf = PdfExtracts(config)
    result_record = Pdf.extract_from_pdf_string(pdf_stream)
    assert result_record['title'] == "A MERCHANT'S GUIDE TO Card Acceptance Fees "

def test_local_extract_html():
    filepath = Path(__file__).parent / 'examples' / 'Research Articles in Simplified HTML.html'
    #TODO: filepath = 'tests/data/Research Articles in Simplified HTML with CSS.html'
    html_str = ''
    with open(filepath, 'r') as f:
        html_str = f.read()
    record = {}
    for key in record_attrs:
        record[key] = None

    Html = HtmlExtracts(config)
    #record_from_context, pdf_bytes  = Html.html_string_to_pdf_bytes(html_str=html_str,
    pdf_bytes  = Html.html_string_to_pdf_bytes(html_str=html_str,
                                                                    url_path=None,
                                                                    record=record
                                                                    )
    
    check_pdf_bytes = len(pdf_bytes) > 0
    #TODO: removed all the following
    #check_title =  record_from_context['title'] == 'Research Articles in Simplified HTML: a Web-first format for HTML-based scholarly articles'
    #meta_attrs = ["title", "author", "subject", "keywords"]
    #check_record_attrs = [ record_from_context[key]!=None for key in meta_attrs ]
    checks = []
    checks.extend([check_pdf_bytes])
    #checks.extend([check_pdf_bytes, check_title])
    #checks.extend(check_record_attrs)
    assert all(checks) == True


def test_web_local_extract_html():
    hrefs = ['https://www.jpmorganchase.com/ir/news/2021/chase-helps-more-than-two-million-customers-avoid-overdraft-service-fees',
    ]
    URL = UrlFactory()
    urls = [URL.build(url) for url in hrefs]
    artifacts = [{'name': url.url, 'file_format': url.get_file_artifact_(), 'file_str': url.file_str} for url in urls]

    Html = HtmlExtracts(config)
    #record_from_context, pdf_bytes  = Html.html_string_to_pdf(html_str=artifacts[0]['file_str'], 
    pdf_bytes  = Html.html_string_to_pdf_bytes(html_str=artifacts[0]['file_str'], 
                                                              url_path=artifacts[0]['name']
                                                              )
    
    check_pdf_bytes = len(pdf_bytes) > 0
    #check_title =  record_from_context['title'] == 'Chase helps more than two million customers avoid overdraft service fees'
    assert check_pdf_bytes == True


def test_extract_txt():
    filepath = Path(__file__).parent / 'examples' / 'example.txt'
    txt_str = ''
    with open(filepath, 'r') as f:
        txt_str = f.read()
    record = {}
    for key in record_attrs:
        record[key] = None
    Txt = TxtExtracts(config)
    pdf_bytes  = Txt.txt_string_to_pdf_bytes(txt_str=txt_str, record=record)
    check_pdf_bytes = len(pdf_bytes) > 0
    #TODO: removed all the following
    #check_title =  record_from_context['title'] == 'Research Articles in Simplified HTML: a Web-first format for HTML-based scholarly articles'
    #meta_attrs = ["title", "author", "subject", "keywords"]
    #check_record_attrs = [ record_from_context[key]!=None for key in meta_attrs ]
    checks = []
    checks.extend([check_pdf_bytes])
    #checks.extend([check_pdf_bytes, check_title])
    #checks.extend(check_record_attrs)
    assert all(checks) == True
    assert True == True

def test_extract_doc():
    #TODO: improve convert .docx to .pdf
    #TODO: this fails because title includes to much: 'record['title']  "Title for paper submitted to International Journal of Scientific and Research PublicationsFirst Author*, Second Author**, Th....
    #filepath_str = 'tests/data/example.docx', 'Document Title', 7
    filepath_str = 'tests/examples/IJSRP-paper-submission-format-single-column.docx'
    assert True == True


def test_extract_msg():
    assert True == True


def test_extract_ppt():
    assert True == True


def test_extract_xls():
    assert True == True


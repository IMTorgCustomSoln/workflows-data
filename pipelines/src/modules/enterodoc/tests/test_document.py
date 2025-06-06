#!/usr/bin/env python3
"""
Tests for Document class


TODO: IS THIS REALLY THE PATTERN I WANT (below)???
* factory makes document
* document populates attributes
* document exports record to save to intermediate file
* import then create new document from previous record

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from src.modules.enterodoc.entero_document.record import DocumentRecord
from src.modules.enterodoc.entero_document.document_factory import DocumentFactory
from src.modules.enterodoc.entero_document.document import Document

from pathlib import Path
import pytest
import dill

doc_factory = DocumentFactory()


def test_document_build_new():
    test_file = Path(__file__).parent / './examples/example.pdf'
    doc = doc_factory.build(test_file)
    assert type(doc) == Document

def test_document_build_from_record():
    test_file = Path(__file__).parent / './examples/example.pdf'
    doc1 = doc_factory.build(test_file)
    record = doc1.get_record()
    doc2 = doc_factory.build_from_json_record(record)
    assert doc1 == doc2

def test_document_record_serialization():
    test_file = Path(__file__).parent / './examples/example.pdf'
    doc = doc_factory.build(test_file)
    record = doc.get_record()
    new_doc = dill.loads(dill.dumps(record))
    assert type(new_doc) == dict

def test_document_serialization_FAILS():
    test_file = Path(__file__).parent / './examples/example.pdf'
    doc = doc_factory.build(test_file)
    #new_doc = dill.loads(dill.dumps(doc))
    #assert type(new_doc) == DocumentRecord
    try:
        tmp = dill.dumps(doc)
    except:
        tmp = None
    assert tmp == None

def test_document_attributes():
    test_file = Path(__file__).parent / './examples/example.pdf'
    doc = doc_factory.build(test_file)
    docrec = DocumentRecord()
    result = docrec.validate_object_attrs(doc)
    assert result['target_attrs_to_remove'] == result['target_attrs_to_add'] == set()

def test_document_populated():
    test_file = Path(__file__).parent / './demo/econ_2301.00410.pdf'
    doc = doc_factory.build(test_file)
    docrec = DocumentRecord()
    result = docrec.validate_object_attrs(doc)
    check1 = len(result['target_attrs_to_remove']) == 0
    check2 = not bool(result['target_attrs_to_add'])
    check3 = doc.get_missing_attributes() == ['id', 'reference_number', 'file_str', 'file_document', 'length_lines', 'readability_score', 'tag_categories', 'summary']
    assert not False in [check1, check2, check3]

def test_document_creation_fail():
    test_file = Path(__file__).parent / './examples/no_file.docx'
    '''previous flow:
    with pytest.raises(Exception) as e_info:
        doc = Doc.build(test_file)
    assert type(e_info) == pytest.ExceptionInfo
    '''
    doc = doc_factory.build(test_file)
    assert doc == None

def test_document_determine_filetype_fail():
    """Filetypes that fail: .doc, .rtf, .tif, .docm, .dot
    This tests that file exists, but is not supported by 
    method `Document.run_extraction_pipeline()`.  So, attr
    are None, and not empty string ''.
    """
    test_file = Path(__file__).parent / './examples/unavailable_extension.doc'
    doc = doc_factory.build(test_file)
    assert doc.record.file_document == None

def test_document_extraction():
    """TODO: create separate tests using pytest."""
    #TODO:currently these fail to capture actual title
    lst = { '.txt': ['./examples/example.txt', 'Text File Title'],
            '.docx': ['./examples/example.docx', 'Document Title'],
            '.html': ['./examples/example.html', 'The Website Title'],
            '.pdf': ['./examples/example.pdf', 'The Website Title'],
            '.csv': ['./examples/example.csv', 'Document Title'],
            '.xlsx': ['./examples/example.xlsx', 'Document Title'],
            }
    checks = []
    for k,v in lst.items():
        filepath = v[0]
        title = v[1]
        test_file = Path(__file__).parent / filepath
        doc = doc_factory.build(test_file)
        check = hasattr(doc.record, 'title') == True
        checks.append(check)
    assert all(checks) == True

def test_get_record():
    test_file = Path(__file__).parent / './demo/econ_2301.00410.pdf'
    doc = doc_factory.build(test_file)
    record = doc.get_record()
    assert list(record.keys()).__len__() == 25
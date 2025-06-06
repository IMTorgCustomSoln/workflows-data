#!/usr/bin/env python3
"""
Test PipelineRecord for atomic record for Tasks.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.Task import PipelineRecordFactory, PipelineRecord
import pytest
    


def test_pipeline_record_creation_single_file():
    id = '12345'
    source_type = 'single_file'
    factory = PipelineRecordFactory()
    record = factory.create_from_id(id, source_type)
    assert type(record) == PipelineRecord

@pytest.mark.skip(reason="Test is currently under development")
def test_pipeline_record_creation_multiple_file():
   assert True == True


@pytest.mark.skip(reason="Test is currently under development")
def test_pipeline_record_populate_presentation_doc():
  #TODO:test `populate_presentation_doc()` with differetn Document types: pdf, html, ecomms,...
  assert False == True
#!/usr/bin/env python3
"""
Test estimate processing time
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from .estimate_processing_time import ProcessTimeQrModel

def test_estimate_model():
    mdl = ProcessTimeQrModel()
    mdl.estimate_model()
    check = mdl.save_models()
    assert check==True

def test_predict_processing_time():
    file_size_bytes_lst = [1000]
    mdl = ProcessTimeQrModel()
    mdl.load_models()
    time = mdl.predict_processing_time(file_size_bytes_lst)
    assert True==True
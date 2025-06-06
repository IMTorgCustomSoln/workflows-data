#!/usr/bin/env python3
"""
Test ecomms scripts
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from tests.test_wf_ecomms.scripts import combine_dats_to_pickle

from pathlib import Path


def test_combine_dats_to_pickle():
    result = combine_dats_to_pickle()
    mdats_for_deletion = [
        Path('/workspaces/spa-vdi-2/pipelines/tests/test_wf_ecomms/data_ediscovery/extended_layout/12345_VOL02/VOL02/DATA/new_utf8_file.mdat'),
        Path('/workspaces/spa-vdi-2/pipelines/tests/test_wf_ecomms/data_ediscovery/extended_layout/12345_VOL01/VOL01/DATA/new_utf8_file.mdat')
    ]
    [file.unlink() for file in mdats_for_deletion]
    assert result == True
#!/usr/bin/env python3
"""
Test parsing orgchart
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"



from src.modules.parse_orgchart.orgchart import OrgChartParser

from pathlib import Path


file_path_csv = Path(__file__).parent / 'data_orgchart/org1.csv'
file_path_json = Path(__file__).parent / 'data_orgchart/org.json'


def test_validate_orgchart():
    orgchart_parser = OrgChartParser(file_path=file_path_csv)
    check = orgchart_parser.validate()
    assert check == True

def test_load_orgchart():
    orgchart_parser = OrgChartParser(file_path=file_path_csv)
    csv = orgchart_parser.parse(
        office_fields=['LineOfBusiness','SubLOB-1','SubLOB-2','SubLOB-3'],
        office_asc=False,
        manager_fields=['ImmediateManager','HigherMgr-1','HigherMgr-2'],
        manager_asc=True
    )
    #orgchart_parser = OrgChartParser(file_path=file_path_json)
    #json = orgchart_parser.parse()
    assert csv.columns.tolist() == ['Name', 'Role', 'ImmediateManager', 'Title']
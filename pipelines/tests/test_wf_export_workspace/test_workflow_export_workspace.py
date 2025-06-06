"""
Test exporting records to vdi workspace file workflow

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from workflows.workflow_export_workspace import workflow_export_workspace


def test_prepare_workspace():
    check1 = workflow_export_workspace.prepare_workspace()
    assert check1 == True


def test_run():
    check1 = workflow_export_workspace.prepare_workspace()
    check2 = workflow_export_workspace.run()
    assert check2 == True
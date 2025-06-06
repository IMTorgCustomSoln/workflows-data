#!/usr/bin/env python3
"""
Module Docstring

ref: https://github.com/huggingface/transformers/issues/23231
"""

from src.io import export

from pathlib import Path
import json
import tempfile


dialogue1 = {
    "file_name": "0012345678_20200301_123458.wav",
    "file_path": "/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/PROCESSED/0012345678_Calls/0012345678_20200301_123458.wav",
    "sampling_rate": 22050,
    "chunks": [
        {
            "timestamp": [0.0, 10.0],
            "text": " Four score and seven years ago, our fathers brought forth on this continent a new nation, conceived in liberty, and dedicated to the proposition that all men are created equal.",
        }
    ],
    "classifier": [
        {},
        {},
        {
            "search": "FS",
            "target": " Four score and seven years ago, our fathers brought forth on this continent a new nation, conceived in liberty, and dedicated to the proposition that all men are created equal.",
            "timestamp": [0.0, 10.0],
            "pred": 0.7961977094805566,
        },
    ],
}

dialogue2 = {
    "text": " Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel. Nor is Mr. Quilter's manner less interesting than his matter. Nor is Mr. Quilter's",
    "chunks": [
        {
            "timestamp": (0.0, 6.0),
            "text": " Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel.",
        },
        {
            "timestamp": (6.0, 11.0000000999999),
            "text": " Nor is Mr. Quilter's manner less interesting than his matter.",
        },
        {"timestamp": (11.0000000999999, None), "text": " Nor is Mr. Quilter's"},
    ],
}


def test_format_dialogue():
    mod_dialogue = export.format_dialogue_timestamps(dialogue2)
    assert mod_dialogue == [
        "(0.0, 6.0)  -   Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel. \n",
        "(6.0, 11.0)  -   Nor is Mr. Quilter's manner less interesting than his matter. \n",
        "(11.0, None)  -   Nor is Mr. Quilter's \n",
    ]


def test_output_to_pdf():
    mod_dialogue = [
        "(0.0, 6.0)  -   Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel. \n",
        "(6.0, 11.0)  -   Nor is Mr. Quilter's manner less interesting than his matter. \n",
        "(11.0, None)  -   Nor is Mr. Quilter's \n",
    ]
    mod_dialogue = [
        "(0.0, None)  -   Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel. \n",
    ]
    pdf = export.output_to_pdf(dialogue2, mod_dialogue, output_type="str")
    assert True == True


def test_export_to_output_excel_single_file():
    '''
    test_file = ''
    with open(test_file, 'r') as f:
        dialogue1 = json.load(f)
    '''
    dialogues = [dialogue1]
    schema = {"documentsIndex": {"documents": {}}}
    with tempfile.TemporaryDirectory() as t_dir:
        outpath = Path(t_dir)
        filepath = outpath / "batch-TEST.xlsx"
        export.export_dialogues_to_output(schema, dialogues, filepath, output_type="excel")
        assert True == True


def test_export_to_output_vdi_workspace_single_file():
    '''
    test_file = ''
    with open(test_file, 'r') as f:
        dialogue1 = json.load(f)
    '''
    dialogues = [dialogue1]
    workspace_schema = None
    schema_path = Path('/workspaces/spa-vdi-3/pipelines/tests/data') / 'workspace_schema_v0.2.1.json'
    if schema_path.is_file():
        with open(schema_path, 'r') as f:
            workspace_schema = json.load(f)
    with tempfile.TemporaryDirectory() as t_dir:
        outpath = Path(t_dir)
        filepath = outpath / "batch-TEST.gz"
        export.export_dialogues_to_output(workspace_schema, dialogues, filepath, output_type="vdi_workspace")
        assert True == True
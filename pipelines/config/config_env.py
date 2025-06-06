#!/usr/bin/env python3
"""
Module Docstring

"""

import os

def config():
    """..."""

    #configure env
    #os.chdir('')
    from dotenv import load_dotenv
    load_dotenv()

    print(f"'HF_TOKEN' in os.environ: {'HF_TOKEN' in os.environ}")
    print(f"'HF_HOME' in os.environ: {'HF_HOME' in os.environ}")
    print(f"'CURL_CA_BUNDLE' in os.environ: {'CURL_CA_BUNDLE' in os.environ}")

    return True
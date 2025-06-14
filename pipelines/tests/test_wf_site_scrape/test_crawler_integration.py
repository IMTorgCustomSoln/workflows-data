#!/usr/bin/env python3
"""
Test Crawler: Integration Tests

TODO: add keys for:
* urls found by google, but not useful
* urls found to be useful, but not part of base_url
TODO: export as string or URL-class

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.modules.enterodoc.entero_document.url import UrlFactory, UniformResourceLocator
from src.web.crawler import Crawler, empty_scenario, example_udap_search_terms

import time
import copy
import pytest


urls = ['https://www.jpmorgan.com']
URL = UrlFactory()
Url_list = [URL.build(url) for url in urls]



def test_crawler_generate_href_chain_without_base_url():
    """`base_url` is not necessary for any aspect of code, 
    but `scenario._valid_urls` must be populated by validating
    the provided `url_list`."""
    start_time = time.time()
    #setup
    scenario = copy.deepcopy(empty_scenario)
    scenario.base_url = None
    scenario.urls = Url_list
    scenario.list_of_search_terms = example_udap_search_terms
    scenario.depth = 0
    crawler = Crawler(
                scenario=scenario,
                logger=None,
                exporter=''
                )
    #usage
    valid_urls = crawler._check_urls_are_valid()
    result_urls = crawler.generate_href_chain()
    key = Url_list[0].url
    duration_sec = time.time() - start_time
    assert list(result_urls.keys())[0] == key
    assert len(result_urls[key]) > 1
    assert duration_sec < 180

def test_crawler_generate_href_chain_with_base_url():
    start_time = time.time()
    #setup
    scenario = copy.deepcopy(empty_scenario)
    scenario.base_url = Url_list[0]
    scenario.urls = Url_list
    scenario.list_of_search_terms = example_udap_search_terms
    scenario.depth = 0
    crawler = Crawler(
                scenario=scenario,
                logger=None,
                exporter=''
                )
    #usage
    valid_urls = crawler._check_urls_are_valid()
    result_urls = crawler.generate_href_chain()
    key = Url_list[0].url
    duration_sec = time.time() - start_time
    assert list(result_urls.keys())[0] == key
    assert len(result_urls[key]) > 1
    assert duration_sec < 180
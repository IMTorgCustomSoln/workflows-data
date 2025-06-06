#!/usr/bin/env python3
"""
Test crawler

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
import pytest


urls = ['https://www.jpmorgan.com']
URL = UrlFactory()
Url_list = [URL.build(url) for url in urls]


def test_crawler_check_urls_are_valid_correct():
    """Url_list is the target of the method, base_url may not be available."""
    #setup
    empty_scenario.base_url = None
    empty_scenario.urls = Url_list
    empty_scenario.list_of_search_terms = example_udap_search_terms
    empty_scenario.depth = 0
    crawler = Crawler(
                scenario=empty_scenario,
                logger=None,
                exporter=''
                )
    #usage
    valid_urls = crawler.check_urls_are_valid()
    assert valid_urls.__len__() == 1
    
def test_crawler_check_urls_are_valid_fail():
    """base_url is not necessary, Url_list is always necessary."""
    #setup
    empty_scenario.base_url = Url_list[0]
    empty_scenario.urls = []
    empty_scenario.list_of_search_terms = example_udap_search_terms
    empty_scenario.depth = 0
    crawler = Crawler(
                scenario=empty_scenario,
                logger=None,
                exporter=''
                )
    #usage
    valid_urls = crawler.check_urls_are_valid()
    assert valid_urls.__len__() == 0

def test_crawler_generate_href_chain_without_base_url():
    """`base_url` is not necessary for any aspect of code, 
    but `scenario._valid_urls` must be populated by validating
    the provided `url_list`."""
    start_time = time.time()
    #setup
    empty_scenario.base_url = None
    empty_scenario.urls = Url_list
    empty_scenario.list_of_search_terms = example_udap_search_terms
    empty_scenario.depth = 0
    crawler = Crawler(
                scenario=empty_scenario,
                logger=None,
                exporter=''
                )
    #usage
    valid_urls = crawler.check_urls_are_valid()
    result_urls = crawler.generate_href_chain()
    key = Url_list[0].url
    duration_sec = time.time() - start_time
    assert list(result_urls.keys())[0] == key
    assert len(result_urls[key]) > 1
    assert duration_sec < 180

def test_crawler_generate_href_chain_with_base_url():
    start_time = time.time()
    #setup
    empty_scenario.base_url = Url_list[0]
    empty_scenario.urls = Url_list
    empty_scenario.list_of_search_terms = example_udap_search_terms
    empty_scenario.depth = 0
    crawler = Crawler(
                scenario=empty_scenario,
                logger=None,
                exporter=''
                )
    #usage
    valid_urls = crawler.check_urls_are_valid()
    result_urls = crawler.generate_href_chain()
    key = Url_list[0].url
    duration_sec = time.time() - start_time
    assert list(result_urls.keys())[0] == key
    assert len(result_urls[key]) > 1
    assert duration_sec < 180

@pytest.mark.skip(reason="Test is currently under development")
def test_crawler_get_hrefs_within_depth():
    assert True == True

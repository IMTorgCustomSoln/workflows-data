#!/usr/bin/env python3
"""
Test Crawler: Unit Tests
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



def test_crawler_scenario():
    base_scenario = copy.deepcopy(empty_scenario)
    assert base_scenario.base_url == None
    assert base_scenario.depth == 0
    assert base_scenario.stopping_criteria == {
            'search_engine_timeout': 10,
            'number_of_search_results': 5,
            'attempts_until_abort': 5,
            'minimum_retry_delay_secs': 5,
        }

def test_crawler__prepare_search_terms():
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
    check = crawler._prepare_search_terms()
    assert check == True
    assert crawler.scenario._stringified_lists == ['creditcard`, `fees terms conditions', 'terms conditions creditcard`, `fees']

def test_crawler_add_scenario():
    """..."""
    #setup
    crawler = Crawler(
                scenario=empty_scenario,
                logger=None,
                exporter=''
                )
    #usage
    scenario = copy.deepcopy(empty_scenario)
    scenario.base_url = None
    scenario.urls = Url_list
    scenario.list_of_search_terms = example_udap_search_terms
    scenario.depth = 0
    scenario = crawler.add_scenario(scenario)
    assert type(scenario.urls[0]) == UniformResourceLocator
    assert scenario._stringified_lists == []
    assert scenario._valid_urls == []

def test_crawler__check_urls_are_valid_correct():
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
    valid_urls = crawler._check_urls_are_valid()
    assert valid_urls.__len__() == 1
    
def test_crawler__check_urls_are_valid_fail():
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
    valid_urls = crawler._check_urls_are_valid()
    assert valid_urls.__len__() == 0

@pytest.mark.skip(reason="Test is time-consuming, ~20sec")
def test_crawler__get_initial_url_list():
    """..."""
    #setup
    empty_scenario.base_url = None
    empty_scenario.urls = Url_list
    empty_scenario.list_of_search_terms = example_udap_search_terms
    empty_scenario.depth = 0
    empty_scenario.stopping_criteria['number_of_search_results'] = 0
    crawler = Crawler(
                scenario=empty_scenario,
                logger=None,
                exporter=''
                )
    valid_urls = crawler._check_urls_are_valid()
    #usage
    initial_list_of_valid_urls = crawler._get_initial_url_list(
        base_url = Url_list[0],
        url = valid_urls[0],
        stringified_lists = crawler.scenario._stringified_lists[:1],
        stopping_criteria = empty_scenario.stopping_criteria
    )
    assert initial_list_of_valid_urls.__len__() >= 1


@pytest.mark.skip(reason="Test is currently under development")
def test_crawler_get_hrefs_within_depth():
    assert True == True

@pytest.mark.skip(reason="Test is currently under development")
def test_crawler_export():
    assert True == True
#!/usr/bin/env python3
"""
Crawler class to discover web sites that meet criteria.


TODO: use framework for the following
* frameworks
  - [crawlee](https://crawlee.dev/python/)
  - [scrapy](https://scrapy.org/)
* concurrent requests, retries, 
* remove duplicate urls => cache all read urls, even across roots
* improve speed => only limit speed to same domain
* limit depth crawl => collect branches up to limit, prevent from running forever
* prevent blocks => 
  - rotate `User-Agent`
  - run during off-peak hours
  - respect robots.txt
  - avoid honeypot urls
* prioritize urls
* frequency control => read `crawl-delay` in `robots.txt`
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"


from src.modules.enterodoc.entero_document.url import UrlFactory, UniformResourceLocator
#from ..services._constants import logger

#import googlesearch
from duckduckgo_search import DDGS

from pathlib import Path
import itertools
import time



#argument templates
class BaseLogger:
    """Base class for the Crawler's logger.
    Use for non-production purposes.
    """
    def __init__(self):
        pass

    def info(self, msg):
        print('INFO: {msg}')

    def error(self, msg):
        print('ERROR: {msg}')


class BaseSearchScenario:
    """Base class for the Crawler's search scenario conditions.
    The following are added by the Crawler:
        * self._stringified_lists
        * self._valid_urls
    """
    def __init__(self, base_url, urls, list_of_search_terms):
        self.base_url = base_url
        self.urls = urls
        self.list_of_search_terms = list_of_search_terms
        self.depth = 0
        self.number_of_search_results = 5

    #the following is necessary to perform copy.deepcopy(), 
    # ref: https://stackoverflow.com/questions/10618956/copy-deepcopy-raises-typeerror-on-objects-with-self-defined-new-method
    def __copy__(self):
        return self
    def __deepcopy__(self, memo):
        return self


class BaseExporter:
    """Base class for the Crawler's exporter."""
    def __init__(self):
        pass

    def export(self, url_list):
        return url_list



#example_udap_search_terms = ['creditcard`, `fees', 'terms conditions', 'overdraft', 'non insufficient funds']
example_udap_search_terms = ['creditcard`, `fees', 'terms conditions']
empty_scenario = BaseSearchScenario(base_url=None,
                                    urls=[],
                                    list_of_search_terms=[],
                                    )




#primary class
class Crawler:
    """Crawl sites specific to a Scenario's urls and search
    terms to produce a list of url references that meet the
    Scenario criteria.

    This is an 'opportunistic' crawler in that it only 
    accepts an initial domain and search scenario, then
    leverages google search to find target pages.
    
    Usage::
    UrlCrawl = Crawler(logger, exporter, scenario)
    """

    def __init__(self, scenario, logger, exporter):
        if not logger:
            self.logger = BaseLogger()
        else:
            self.logger = logger
        self.exporter = exporter
        self.url_factory = UrlFactory()
        self.scenario = self.add_scenario(scenario)
        self._prepare_search_terms()
        self.min_delay = 5
        self.attempts = 1
        
    def __repr__(self):
        return f'Crawler with scenario: depth - {self.scenario.depth}, urls ({len(self.scenario.urls)}) - {self.scenario.urls}'
    
    def _ensure_url_class(self, url):
        """Provide url of class UniformResourceLocator if not one already."""
        result = url if type(url) == UniformResourceLocator else self.url_factory.build(url)
        return result
    
    def _prepare_search_terms(self):
        """Transform the provided `list_of_search_terms` which is necessary, 
        but not sufficient, input for google search.
        """
        for term in empty_scenario.list_of_search_terms:
            assert type(term) == str
            term_permutations = list(itertools.permutations(empty_scenario.list_of_search_terms, r=2))
            search_terms_list = []
            for tup in term_permutations:
                tmp = list(tup)
                search_terms_list.append(tmp)
            stringified_lists = [' '.join(terms) for terms in search_terms_list]
            empty_scenario._stringified_lists = stringified_lists
        return True
    
    def add_scenario(self, scenario):
        """Add scenario to Crawler if it meets requirements."""
        if scenario.base_url:
            scenario.base_url = self._ensure_url_class(scenario.base_url)
        if type(scenario.urls) == list:
            url_list = scenario.urls
            scenario.urls = [self._ensure_url_class(url) for url in url_list]
        scenario._stringified_lists = []
        scenario._valid_urls = []
        return scenario

    def check_urls_are_valid(self, url_list=None, base_url=None):
        """Basic checks on list of targeted urls
        * ensure proper url formatting
        * consistent domain owner (if base_domain provided)
        """
        if not url_list:
            url_list = self.scenario.urls
        if not base_url:
            base_url = self.scenario.base_url
        failed_urls = []
        validated_urls = []
        #BaseUrl = self._ensure_url_class(base_url)
        if base_url:
            base_url.check_valid_format()
        for url in url_list:
            try: 
                Url = self._ensure_url_class(url)
                check_scheme = Url.check_scheme()
                if base_url:
                    check_owner = Url.has_same_url_owner_(base_url) 
                else:
                    check_owner = True
                if check_scheme and check_owner:
                    validated_urls.append(Url)
                else:
                    failed_urls.append(url)
                    print(f'errored url: {url}')
            except Exception as e:
                failed_urls.append(url)
                print(f'failed url: {url}')
        self.logger.info(f'validated {len(validated_urls)} urls: {validated_urls}')
        self.scenario._valid_urls = validated_urls
        return validated_urls

    def generate_href_chain(self):
        """Given a domain name, collects the appropriate
        href links."""
        if empty_scenario._stringified_lists.__len__() < 1:
            raise Exception('cannot `generate_href_chain()` because `scenario._stringified_lists` is not populated')
        if self.scenario._valid_urls.__len__() < 1:
            raise Exception('cannot `generate_href_chain()` because `scenario._valid_urls` is not populated')
        result_urls = {}
        for url in self.scenario._valid_urls:
            initial_list = self.get_initial_url_list(base_url = self.scenario.base_url,
                                                     url = url, 
                                                     stringified_lists = self.scenario._stringified_lists,
                                                     number_of_search_results = self.scenario.number_of_search_results
                                                     )
            hrefs = self.get_hrefs_within_depth(base_url = self.scenario.base_url,
                                                depth = self.scenario.depth,
                                                initial_url_list = initial_list
                                                )
            url_str = url.url
            hrefs_str = hrefs    #[href.url for href in hrefs]
            result_urls[url_str] = hrefs_str
            self.logger.info(f"result of `generate_href_chain()` is {len(hrefs)} result_urls for root {url} listed as: {hrefs}")
        return result_urls

    def get_initial_url_list(self, base_url, url, stringified_lists, number_of_search_results):
        """Get initial list of urls from google given search terms."""
        NumberOfSearchResults = number_of_search_results
        #BaseUrl = self.url_factory.build('https://www.jpmorgan.com')
        #BaseUrl = url
        '''
        domain = url.get_domain()
        term_permutations = list(itertools.permutations(list_of_search_terms, r=2))
        search_terms_list = []
        for tup in term_permutations:
            tmp = list(tup)
            tmp.append(domain)
            search_terms_list.append(tmp)
        stringified_lists = [' '.join(terms) for terms in search_terms_list]
        '''
        domain = url.get_domain()
        result_url_list = []
        for terms in stringified_lists:
            terms = terms.replace('`','').replace(',','') + ' ' + domain
            try:
                '''
                search_results = googlesearch.search(term = terms, 
                                                     num_results = NumberOfSearchResults,
                                                     sleep_interval = 5 
                                                     )
                '''
                search_results = DDGS(timeout=20).text(
                    keywords = terms,
                    max_results = NumberOfSearchResults
                    )                
                self.logger.info(f'request made to search engine using terms: {terms}')
                str_result_url_list = [str(url) for url in result_url_list]
                unique_urls = [url['href'] for url in search_results if url['href'] not in str_result_url_list]
                SearchUrls = [self.url_factory.build(result) for result in unique_urls]
                result_url_list.extend(SearchUrls)
                time.sleep(self.min_delay)
            except Exception as e:
                self.logger.error(f'ERROR: {e}')
                self.logger.error('ERROR: there was a problem making the request to the search engine')
                if "Ratelimit" in str(e):
                    wait_time = self.min_delay + (self.attempts * 2)
                    self.attempts += 1
                    time.sleep(wait_time)
                if self.attempts >= 10:    #TODO:place in configuration
                    break
        ValidUrls = self.check_urls_are_valid(url_list = result_url_list, 
                                              base_url = base_url
                                              )
        return ValidUrls


    def get_hrefs_within_depth(self, base_url=None, depth=1, initial_url_list=[]):
        """Get all hrefs from a page, within a depth, and certain criteria.

        This is similar to `wget --recursive http://site.com`, but it removes 
        links that are out of scope.
        """
        #BaseUrl_JPM = self.url_factory.build('https://www.jpmorgan.com')
        searched_hrefs = set()
        BaseUrl = None
        if base_url:
            BaseUrl = self._ensure_url_class(base_url)
        #if len(initial_url_list) == 0:
        #    hrefs = BaseUrl.get_hrefs_within_hostname_(searched_hrefs = searched_hrefs)
        #    #searched_hrefs = add_list_to_set(searched_hrefs, hrefs)
        #else:
        #    hrefs = initial_url_list
        hrefs = initial_url_list
        while depth > -1:
            level_hrefs = []
            for url in hrefs:
                try:
                    Url = self._ensure_url_class(url)
                    check_owner = True
                    if BaseUrl:
                        check_owner = Url.has_same_url_owner_(BaseUrl)
                    if not (Url.url in searched_hrefs) and check_owner:
                        new_hrefs = Url.get_hrefs_within_hostname_(searched_hrefs = searched_hrefs)
                        valid_hrefs = self.check_urls_are_valid(url_list = new_hrefs, 
                                                                base_url = BaseUrl
                                                                #base_url = BaseUrl_JPM
                                                           )
                        searched_hrefs.add(Url.url)
                        level_hrefs.extend(valid_hrefs)
                except Exception as e:
                    self.logger.info(f'the following html extract could not be converted to class url: {url}')
                    self.logger.error(e)
            str_level_hrefs = [Url.url for url in level_hrefs]
            hrefs = list(set(str_level_hrefs))
            depth = depth - 1

        return searched_hrefs
    

    def export(self, urls):
        """Export urls through customization of BaseExporter class.

        The result is typically one of the following:
        * bool - result of process
        * [bool] - list of bools for result of multiple processes
        * [f(url)] - transformation of the urls
        
        """
        result_urls = self.exporter.export(urls)
        return result_urls
#!/usr/bin/env python3
"""
UniformResourceLocator (URL) and UrlFactory classes
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from .config import ConfigObj
#from src.io.jsonable import JSONAble

import tldextract
import whois
from requests_html import HTMLSession
import bs4
import pypdf

import urllib
from pathlib import Path
import io
import time
import sys
#import json
import copy



'''
class UrlEncoder(json.JSONDecoder):
    """Used in json.dumps()."""
    def default(self, obj):
            return obj.__repr__()
'''



class UrlFactory:
    """Builder pattern with config.
    :param config: object of type EnteroConfig
    
    Usage::
        >>> hrefs = ['https://www.jpmorgan.com']
        >>> URL = UrlFactory()
        >>> urls = [URL.build(url) for url in hrefs]
    """

    def __init__(self, config=None):
        if config:
            self.config = config
        else:
            self.config = ConfigObj

    def build(self, url):
        """Build UniformResourceLocator objects from 
        url strings and the EnteroConfig.
        """
        if type(url) == UniformResourceLocator:
            return url
        elif url in [None, '', False]:
            return None
        else:
            return UniformResourceLocator(
                url,
                self.config.logger,
                self.config.applyRequestsRenderJs
                )



class UniformResourceLocator():
    """Describe class

    The URL could point to one of many options:
    * web page (ie. )
    * html or pdf file (ie. )
    * json or other data format (ie. )

    Usage::
        >>> hrefs = ['https://www.jpmorgan.com']
        >>> URL = UrlFactory()
        >>> urls = [URL.build(url) for url in hrefs]
        >>> urls[0].get_hostname() == 'www.jpmorgan.com'
    """

    _possible_schemes = ['http://', 'https://']
    _possible_suffixes = {'html': ['html','com','org','gov','md'],   #map url_type to suffix
                          'pdf': ['pdf'],
                          'data': ['json','jsonl','xml','csv','sql','txt'],
                          'msft': ['doc','ppt','xlsx']
                          }
    _possible_suffixes_list = []

    def __init__(self, url, logger, applyRequestsRenderJs):
        self.url = None
        self.logger = logger
        self.applyRequestsRenderJs = applyRequestsRenderJs

        if type(url) == str:
            self.url = url  #url.lower()
        elif type(url) == UniformResourceLocator:
            self.logger.error(f'url is already of type {UniformResourceLocator}')
            raise Exception
        else:
            raise TypeError
        

        #components   
        self.scheme = ''                #initialize with empty string, if not available, then populate with None
        self.suffix = ''
        self.valid_url = ''
        self.filename = ''
        self.url_type = ''              #from suffix in  _possible_suffixes

        #metadata
        self.whois_account = ''
        self.owner = ''

        #artifacts
        self.file_type = ''             #from url content-type
        self.file_format = ''           #inferred from document
        self.file_str = ''              #document string
        self.file_document = ''         #document
        self.file_size_mb = ''
        self.file_visible_text = ''

        self.run_checks()

        
    #basic
    def __repr__(self):
        return str(self.url)
    
    def __eq__(self, other) :
        """Provide `==` operator, 
        ref: https://stackoverflow.com/questions/6423814/is-there-a-way-to-check-if-two-object-contain-the-same-values-in-each-of-their-v
        """
        if (not type(self) == type(other)) or (not hasattr(other, '__dict__')):
            return False
        copy_self = copy.deepcopy(self.__dict__)
        if 'logger' in list(copy_self.keys()):
            del copy_self['logger']
        copy_other = copy.deepcopy(other.__dict__)
        if 'logger' in list(copy_other.keys()):
            del copy_other['logger']
        return copy_self == copy_other
            
    def get_metadata_(self):
        """Return basic information about the URL."""
        return (
            f'URL: {self.url}\n'
            f'Domain: {self.get_domain()}\n'
            f'Name: {self.get_filename()}\n'
            f'Owner: {self.owner}\n'
            f'Type: {self.url_type}\n'
            f'File Format: {self.file_format}\n'
            f'Length File: {len(self.file_str)}\n'
        )
    
    def _populate_possible_suffixes_list(self):
        self._possible_suffixes_list = []
        for val in self._possible_suffixes.values():
            self._possible_suffixes_list.extend(val)


    #checks
    def run_checks(self):
        """Run all checks."""
        self.check_scheme()
        self.check_suffix_and_url_type()
        self.check_valid_format()
        return True

    def check_scheme(self):
        """Check for valid scheme, populate `self.scheme`."""
        check_scheme = [scheme in self.url for scheme in self._possible_schemes]
        result = any(check_scheme)
        if result:
            self.scheme = self._possible_schemes[check_scheme.index(True)]
        return result

    def check_suffix_and_url_type(self):
        """Check for suffixes that are possible to parse, 
        populate `self.suffix` and `self.url_type`.
        """
        if not self._possible_suffixes_list:
            self._populate_possible_suffixes_list()
        result = ''
        psl = tldextract.extract(self.url).suffix
        split = self.url.split('.')
        endpt = split[len(split)-1]
        suffix = psl if (psl in endpt) else endpt

        check_suffix = [suffix_val in suffix for suffix_val in self._possible_suffixes_list]
        result = any(check_suffix)
        if result:
            self.suffix = suffix
            self.url_type = [k for k,v in self._possible_suffixes.items() if suffix in v][0]
        return result

    def check_valid_format(self):
        """Check if complete url is valid."""
        try:
            result = urllib.parse.urlparse(self.url)
            if result:
                return True
        except:
            return False

    
    #getters
    def get_fqdn(self):
        """Get Fully Qualified Domain Name (FQDN).
        Usually used for landing page.
        fqdn = <hostname> and <domain>
        """
        return None

    def get_hostname(self):
        """Get hostname.
        Network or system used to deliver a user to a certain address.
        schema: hostname = <www>.<internal_network>.<suffix>
        """
        return urllib.parse.urlparse(self.url).hostname
    
    def get_domain(self):
        """Get domain name.
        Site or project the user is accessing.  This is typically used
        to ensure url is within same site.
        schema: <subdomain>.<domain>.<suffix>
        """
        return tldextract.extract(self.url).domain

    def get_suffix(self):
        """Get actual suffix which might not align
        with PSL."""
        return self.suffix
    
    def get_scheme(self):
        """Get actual suffix which might not align
        with PSL."""
        return self.scheme
    
    def get_filename(self):
        """Get general file name.
        schema: <domain>/<filename>.<suffix>
        """
        #available
        if self.filename and self.filename != '':
            return self.filename
        #check for existence
        tmp = urllib.parse.urlparse(self.url).path.split('/')
        if len(tmp) < 2 and self.get_suffix():
            self.filename = f'{self.get_domain()}.{self.url_type}'
            return self.filename
        elif not self.get_suffix():
            return None
        #make best attempt
        stem = ''
        if not stem:
            try:
                stem = Path(self.url.__str__()).stem
            except:
                pass
        if not stem:
            try:
                tmp = urllib.parse.urlparse(self.url).path.split('/')
                if len(tmp) > 1:
                    stem = tmp[len(tmp)-1]
            except:
                pass
        if stem:
            self.filename = f'{stem}.{self.url_type}'
        else:
            self.filename = None
        return self.filename
    
    def get_subdomain(self):
        return tldextract.extract(self.url).subdomain

    def get_domain_with_suffix(self):
        return f'{self.get_domain()}.{self.suffix}'

    def get_domain_with_scheme(self):
        return f'.{self.scheme}{self.get_subdomain()}{self.get_domain()}'
    
    def get_file_document(self):
        """Get the file in whatever file type is supported."""
        if not all([self.file_format, self.file_document]):
            self.logger.error(f"no data try calling `self.get_file_artifact_()")
        elif self.file_format == None:
            self.logger.error(f"`self.get_file_artifact_() called, but no data")
        return (self.file_type ,self.file_document)


    #getters requiring requests
    def run_data_requests_(self):
        """Run all methods that require http requests."""
        try:
            self.get_owner_()
            self.get_file_artifact_()
        except:
            self.logger.error('there was a problem making requests.')
        return True
    
    def get_owner_(self):
        """Request the owner from ICANN WHOIS.

        Without 1sec delay ICANN will reject the request.  However, there
        are continued difficulties with not getting the owner.
        TODO:replace python-whois with custom lib that can: 
            - parse owner from text
            - improve error handling (too many errors)
        """
        ATTEMPTS = 2

        def request_iteration():
            try:
                self.whois_account = whois.whois(self.url)
                self.logger.info(f'request made to whois for url {self.url}')
                self.owner = self.whois_account.text.split('Organization:')[1].split('\n')[0].strip()
            except:
                self.logger.error(f'ICANN WHOIS gave no response for url: `{self.url}`')
            time.sleep(3)
            return self.owner

        while ATTEMPTS > 0:
            if not self.owner:
                request_iteration()
            ATTEMPTS =- 1
            
        return self.owner
    
    def has_same_url_owner_(self, comparison_url):
        """Compare this url owner with another url's owner."""
        if not type(comparison_url) == UniformResourceLocator:
            Url = UrlFactory()
            ComparisonUrl = Url.build(comparison_url)
        else:
            ComparisonUrl = comparison_url

        #case-1: check domains
        if self.get_domain() == comparison_url.get_domain():
            result = True
            return result

        #case-2: check icann owners
        if not self.owner:
            self.get_owner_()
        if not ComparisonUrl.owner:
            ComparisonUrl.get_owner_()

        if self.owner and ComparisonUrl.owner:
            result = self.owner == ComparisonUrl.owner
        else:
            result = False
        if not result:
            self.logger.info(f'WARNING: Different Owners:\n'
                        f'current url: `{self.url}`'
                        f'    owner [{self.owner}]\n' 
                        f'comparison url: `{comparison_url.url}`' 
                        f'    owner [{comparison_url.owner}]'
                        )
        return result
    
    def get_file_artifact_(self):
        """Determine if url is page, file, data, etc., then populate the
        artifact and associated attributes.
        
        In the process this will use (`self.url_type` mapping from `self.suffix`) 
        to provision:
        * `self.file_type`
        * `self.file_format`
        * `self.file_str`
        * `self.file_document`
        * `self.file_size_mb`

        note: Failing to parse the file will provision with a None.  This is used
        over empty string ('') to document that parsing was attempted.
        """
        def _get_artifact():
            """Get url artifact and verify self.url_type is correct, then populate self.file_str if possible."""
            resp = None
            try:
                session = HTMLSession()
                resp = session.get(self.url)
                self.logger.info(f'request made to url {self.url}')
                if resp.status_code == 200:
                    content_type = resp.headers.get('content-type')
                    self.file_type = content_type
                    if 'text/html' in content_type:
                        if self.url_type != 'html':
                            self.logger.error('ERROR: `self.url_type` does not match content-type')  
                            raise Exception
                        if self.applyRequestsRenderJs:
                            resp.html.render()
                            txt = resp.html.text
                        else:
                            txt = resp.text
                        if len(txt) < 100:
                            self.logger.error('ERROR: HTML content length is insignificant')  
                            raise Exception
                        self.file_str = txt
                    elif 'application/pdf' in content_type:
                        if self.url_type != 'pdf':
                            self.logger.error('ERROR: `self.url_type` does not match content-type') 
                            raise Exception
                        bytes = resp.content
                        if len(bytes) < 100:
                            self.logger.error('ERROR: PDF content length is insignificant')  
                            raise Exception
                        self.file_str = bytes        #output as bytes for binary file (PDF file, audio, image, etc.)
                    else:
                        self.logger.error(f'ERROR: unaddressed content-type: {content_type}')
                        raise Exception
                else:
                    self.logger.error(f'ERROR: when requesting url, got status-code: {resp.status_code}')
                    raise Exception
            except Exception:
                self.logger.error(f'ERROR: in request for url: {self.url}')
            return resp

        def _parse_artifact_from_suffix(resp):
            """Parese file and provision file attributes."""
            result = ''
            #html
            if resp and self.url_type == 'html':
                try: 
                    soup = bs4.BeautifulSoup(self.file_str, 'html.parser')
                    if soup:
                        result = 'html'
                        self.file_format = result
                        self.file_document = soup
                except:
                    self.logger.error(f'ERROR: file for url {self.url} is invalid HTML')
                    result = None
            #pdf
            elif resp and self.url_type == 'pdf':
                try:
                    file_stream = io.BytesIO(self.file_str)
                    pdf_file = pypdf.PdfReader(file_stream)     #purpose:to validate pdf format
                    if pdf_file:
                        result = 'pdf'
                        self.file_format = result
                        self.file_document = pdf_file
                    else:
                        raise Exception
                except Exception:    #pypdf.errors.PdfReadError:
                    self.logger.error(f'ERROR: file for url {resp.url} is invalid PDF')
                    result = None
            #if no url (no file)
            else:
                result = None
                self.file_format = result
                self.file_document = result
            size_in_mb = int( sys.getsizeof(self.file_document) )  * 1e-6
            self.file_size_mb = round(size_in_mb, ndigits=3)
            return result
        
        #workflow
        result = ''
        resp = _get_artifact()
        result = _parse_artifact_from_suffix(resp)
        time.sleep(1)
        return result
    
    def get_hrefs_under_criteria_(self, detailed_data=False):
        """Get all anchors from a `resp.text` html file under 
        specific criterion.
        """
        REMOVE = ['sign','login']

        anchors_with_stem = None
        if self.file_document and self.url_type == 'html':
            tmp =  self.get_hostname()     #urllib.parse.urlparse(resp.url).hostname    #Path(resp.url).stem.split('.')
            stem = tmp[len(tmp)-1] if len(tmp) > 1 else tmp[0]
            soup = self.file_document

            #anchors
            anchors = soup.find_all('a')
            if detailed_data:
                """TODO: should this be implement??? , if so, then improve performance"""
                anchors_with_hrefs = [anchor for anchor in anchors if anchor.has_attr('href')]
                anchors_with_www_hrefs = [anchor for anchor in anchors_with_hrefs if 'https://' in anchor['href']]
                anchors_without_removed = [anchor for anchor in anchors_with_www_hrefs 
                                           if not any(x in anchor['href'].lower() for x in REMOVE)
                                           ]
                anchors_with_stem = list(set([anchor['href'] for anchor in anchors_without_removed if stem in anchor['href']]))
            else:
                anchors_with_stem = anchors
        return anchors_with_stem

    def get_hrefs_within_hostname_(self, searched_hrefs=set(), additional_scope=[]):
        """Get hrefs from html document that are within the scope of target hostnames.

        TODO: add additional_scope
        """
        hrefs = []
        #pre-checks
        if not (self.file_document or self.file_format):
            self.get_file_artifact_()

        #checks
        if (self.file_document and self.file_format == 'html'):
            tmp_hrefs = self.get_hrefs_under_criteria_(detailed_data=False)
            hrefs = [href for href in tmp_hrefs if href not in searched_hrefs]

        return hrefs

    def get_visible_text_(self):
        """Get visible text from html.

        ref: https://stackoverflow.com/questions/1936466/how-to-scrape-only-visible-webpage-text-with-beautifulsoup
        """
        def tag_visible(element):
            if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
                return False
            if isinstance(element, bs4.element.Comment):
                return False
            return True

        if self.file_document and self.url_type == 'html':
            soup = self.file_document
            texts = soup.findAll(text=True)
            visible_texts = filter(tag_visible, texts)
            self.file_visible_text = visible_texts
            return u" ".join(t.strip() for t in visible_texts)
        else:
            return False
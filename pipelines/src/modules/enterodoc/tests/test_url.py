"""
Test the URL class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from src.modules.enterodoc.entero_document.url import UrlFactory, UniformResourceLocator

import dill


hrefs = [
    'https://www.jpmorgan.com',
    'https://chase.com',
    'https://www.jpmorgan.com/content/dam/jpm/merchant-services/documents/jpmorgan-interchange-guide.pdf',
    'https://www.consumerfinance.gov/credit-cards/agreements/issuer/jpmorgan-chase-bank-national-association/',
    'htt://somedomain.com',
    'http://domain.xml'
]
URL = UrlFactory()
urls = [URL.build(url) for url in hrefs]



def test_check_scheme():
    result = [url.check_scheme() for url in urls]
    schemes = [url.scheme for url in urls]
    check1 = result == [True, True, True, True, False, True]
    check2 = schemes == ['https://', 'https://', 'https://', 'https://', '', 'http://']
    assert all([check1,check2]) == True

def test_check_serialize():
    for url in urls:
        d = dill.dumps(url)
        l = dill.loads(d)
        assert l == url

def test_check_suffix_and_url_type():
    result = [url.check_suffix_and_url_type() for url in urls]
    suffixes = [(url.url_type, url.suffix) for url in urls]
    check1 = result == [True, True, True, True, True, False]
    check2 = suffixes == [('html', 'com'), ('html', 'com'), ('pdf', 'pdf'), ('html', 'gov'), ('html', 'com'), ('', '')]
    assert all([check1,check2])

def test_check_valid_format():
    result = [url.check_valid_format() for url in urls]
    assert all(result) == True


def test_get_hostname():
    result = [url.get_hostname() for url in urls]
    assert result == ['www.jpmorgan.com', 
                      'chase.com', 
                      'www.jpmorgan.com', 
                      'www.consumerfinance.gov', 
                      'somedomain.com', 
                      'domain.xml'
                      ]

def test_get_domain():
    result = [url.get_domain() for url in urls]
    assert result == ['jpmorgan', 
                      'chase',
                      'jpmorgan', 
                      'consumerfinance', 
                      'somedomain', 
                      'xml'
                      ]

def test_get_suffix():
    result = [url.get_suffix() for url in urls]
    assert result == ['com', 'com', 'pdf', 'gov', 'com', '']

def test_get_scheme():
    result = [url.get_scheme() for url in urls]
    assert result == ['https://', 'https://', 'https://', 'https://', '', 'http://']    

def test_get_filename():
    result = [url.get_filename() for url in urls]
    assert result == ['jpmorgan.html',
                      'chase.html',
                      'jpmorgan-interchange-guide.pdf',
                      'jpmorgan-chase-bank-national-association.html',
                      'somedomain.html',
                      None
                      ] 

def test_get_subdomain():
    result = [url.get_subdomain() for url in urls]
    assert result == ['www', '', 'www', 'www', '', 'domain']

def test_get_owner_():
    BaseUrl = URL.build('https://www.jpmorgan.com')
    owner = BaseUrl.get_owner_()
    assert owner == 'JPMorgan Chase & Co.'

def test_get_file_artifact_():
    artifact_types = [(url.get_file_artifact_(), len(url.file_str)) for url in urls]
    check1 = check2 = []
    expected = [('html', 130000), ('html', 27524), ('pdf', 437960), ('html', 95464), ('NA', 0), ('NA', 0)]
    for idx, item in enumerate(artifact_types):
        check1.append( item[0] == expected[idx][0] )
        check2.append( item[1] >= expected[idx][1] )
    assert all([check1, check2])

def test_has_same_url_owner_():
    base_url = 'https://www.jpmorgan.com'
    urls = ['https://chase.com',
            'https://www.jpmorganchase.com/ir/news/2021/chase-helps-more-than-two-million-customers-avoid-overdraft-service-fees',
            'https://www.valuepenguin.com/jp-morgan-reserve-card-chase-palladium',
            'https://www.lendingtree.com/credit-cards/review/jp-morgan-reserve/',
            'https://www.cnbc.com/2021/12/01/capital-one-says-its-ditching-all-consumer-overdraft-fees.html'
    ]

    #test-1
    BaseUrl = URL.build(base_url)
    check_owners_1 = []
    for url in urls:
        Url = URL.build(url)
        result = Url.has_same_url_owner_(BaseUrl)
        check_owners_1.append(result)
    check_owners_1 == [True, True, False, False, False]

    #test-2
    check_owners_2 = []
    for url in urls:
        result = URL.build(url).has_same_url_owner_(URL.build(base_url))
        check_owners_2.append(result) 
    check_owners_2 == [True, True, False, False, False]

    assert check_owners_1 == check_owners_2

def test_get_hrefs_under_criteria_():
    pass

def test_get_hrefs_within_hostname_():
    pass

def test_get_visible_text_():
    pass
#!/usr/bin/env python3
"""
Test Crawler: Regression Tests
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

duplicates = [
    {
        'doc': 'CP-Agreement.pdf',
        'urls': [
            'https://www.creditonebank.com/content/dam/creditonebank/corporate-transactional/pdf/CP-Agreement.pdf',
            'https://www.creditonebank.com/content/dam/cob-corp-acquistion/pdfs/acquisitions/CP-Agreement.pdf',
            'https://rollout01aem.creditone.com/content/dam/creditonebank/corporate-transactional/pdf/CP-Agreement.pdf',
            'https://www.creditonebank.com/assets/pdf/cp-agreement.pdf'
            ]
    },
    {
        'doc': 'credit-protection-agreement.pdf',
        'urls': [
            'https://www.creditonebank.com/content/dam/creditonebank/corporate-transactional/pdf/credit-protection-agreement.pdf',
            'https://rollout01aem.creditone.com/content/dam/creditonebank/corporate-transactional/pdf/credit-protection-agreement.pdf',
            'https://www.creditonebank.com/assets/pdf/cp-agreement.pdf'
        ]
    },
    {
        'doc': 'RewardsRedeptionTerms.pdf',
        'urls': [
            'https://www.creditonebank.com/content/dam/cob-corp-acquisition/pdfs/RewardsRedemptionTerms.pdf',
            'https://www.creditonebank.com/content/dam/cob-corp-acquisition/pdfs/X5RewardsRedemptionTerms.pdf'
        ]
    }
]
logins = [
    {
        'doc': 'login',
        'urls': [
            'https://sit-portalapi-ext.creditone.com/accounts/login',
            'https://www.creditonebank.com/transactional/authorize',
            'https://www.creditonebank.com/transactional/authenticate'
        ]
    }
]
validation_failures = [
    {
        'base_url': 'umb.com',
        'urls': [
            'https://www.cardcenterdirect.com/',
            'https://www.umb.edu/media/umassboston/editor-uploads/research/research-amp-sponsored-programs/Cost-Transfer-Policy--Procedures.pdf'
            ]
    }
]
rendering_failures = [
    {
        'base_url': 'creditonebank',
        'urls': [
            'https://www.creditonebank.com/faqs/disputing-charges',
            'https://www.creditonebank.com/faqs/disputing-charges/provisional-or-conditional-credit',
            'https://www.creditonebank.com/articles/7-common-credit-card-fees-why-banks-charge-them-and-how-to-avoid-them',
            'https://www.creditonebank.com/mobile',
            'https://www.creditonebank.com/card-benefits'
        ],
        'url_text_lengths': [
            2041,
            1167,
            0,
            0,
            0
        ],
        'file_size_mb': [
            0.00190,
            0.00157,
            0.00470,
            0.00482,
            0.00094
        ]
    }
]



def test_url_get_file_artifact():
    """..."""
    for idx, url in enumerate( rendering_failures[0]['urls'] ):
        tgt_url = URL.build(url)
        check_inferred_type = tgt_url.get_file_artifact_()
        assert check_inferred_type == 'html'
        tgt_url_text_length = rendering_failures[0]['url_text_lengths']
        assert tgt_url.get_visible_text_().__len__() == tgt_url_text_length[idx]

def test_url_run_data_requests():
    """..."""
    for idx, url in enumerate( rendering_failures[0]['urls'] ):
        tgt_url = URL.build(url)
        check = tgt_url.run_data_requests_()
        tgt_url_text_length = rendering_failures[0]['url_text_lengths']
        assert tgt_url.get_visible_text_().__len__() == tgt_url_text_length[idx]

from src.web.crawler import BaseLogger
from src.modules.enterodoc.entero_document.config import ConfigObj
from src.modules.enterodoc.entero_document.document_factory import DocumentFactory
from src.modules.enterodoc.entero_document.record import DocumentRecord

def test_url_build_doc():
    """..."""
    logger = BaseLogger()
    ConfigObj.set_logger(logger)
    Doc = DocumentFactory(ConfigObj)
    for idx, url in enumerate( rendering_failures[0]['urls'] ):
        tgt_url = URL.build(url)
        check = tgt_url.run_data_requests_()
        doc = Doc.build(tgt_url)
        pdf_file_size_mb = rendering_failures[0]['file_size_mb']
        assert doc.record['file_size_mb'] >= pdf_file_size_mb[idx]

@pytest.mark.skip(reason="Test is currently under development")
def test_url__parse_artifact_from_suffix():
    """..."""
    assert True == True
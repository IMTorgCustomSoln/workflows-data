#!/usr/bin/env python3
"""
DocumentFactory class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from .config import ConfigObj
from .url import UniformResourceLocator
from .document import Document

from pathlib import Path, PosixPath



class DocumentFactory:
    """"Factory to build Documents from PosixPath or UniformResourceLocator
    :param config: object of type EnteroConfig or use default (None)

    Usage::
        The `.build()` method takes `path_or_url` as input
        >>> from entero_document.document_factory import DocumentFactory
        >>> from entero_document.document import Document
        >>>
        >>> Doc = DocumentFactory()
        >>> test_file = Path('tests/examples/example.pdf')
        >>> doc = Doc.build(test_file)
        >>> assert type(doc) == Document
    """

    def __init__(self, config=None):
        if config:
            self.config = config
        else:
            self.config = ConfigObj
        if self.config.applySpacy:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            Document._spacyNlp = nlp
        
    def build(self, path_or_url):
        """Create Document object with path or url."""
        validation_dict = self._validate(path_or_url=path_or_url)
        if validation_dict:
            doc = Document(path_or_url_format = validation_dict[0],
                            path_or_url_obj = validation_dict[1],
                            logger = self.config.logger,
                            applySpacy = self.config.applySpacy,
                            output_mapping = self.config.output_mapping
                            )
            doc.build_new()
            return doc
        else:
            return None
        
    def build_from_json_record(self, record):
        """Build Document previously exported from json record."""
        doc = Document(path_or_url_format = 'path',    #TODO:enable for url also (url is pickle serializable)
                            path_or_url_obj = Path(record['filepath']),
                            logger = self.config.logger,
                            applySpacy = self.config.applySpacy,
                            output_mapping = self.config.output_mapping
                            )
        doc.build_from_record(record)
        return doc
    
    def build_from_object(self, record):
        """Build Document previously exported from json record."""
        doc = Document(path_or_url_format = 'object',
                            path_or_url_obj = None,
                            logger = self.config.logger,
                            applySpacy = self.config.applySpacy,
                            output_mapping = self.config.output_mapping
                            )
        doc.build_from_record(record)
        return doc
        
    def _validate(self, *args, **kwargs):
        """Validate input or fail object creation and return None."""
        try:
            assert not args
            assert list(kwargs.keys()) == ['path_or_url']
        except AssertionError:
            return False
        path_or_url = kwargs['path_or_url']
        cond0 = type(path_or_url) == UniformResourceLocator
        cond1 = type(path_or_url) == PosixPath
        if cond0:
            if path_or_url.file_document:
                url = path_or_url
                return ('url', url)
            else:
                self.config.logger.error(f"Error: no artifact associated with {path_or_url} ")
                #raise TypeError
                return False
        elif cond1:
            if path_or_url.is_file():
                path = path_or_url
                return ('path', path)
            else:
                self.config.logger.info(f"arg `path` {path_or_url} must be a file")
                #raise TypeError
                return False
        else:
            self.config.logger.info(f"TypeError: arg `path` {path_or_url} must be of type {Path} or {UniformResourceLocator}")
            #raise TypeError
            return False
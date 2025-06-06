#!/usr/bin/env python3
"""
Attributes / Keys and Record classes for use with Document

Primary vars::
* record_attrs - all attributes to populate for each file, maintained in a record
* class DocumentTemplate - schema for records
* class DocumentRecord(DocumentBase) - record filled with file metadata, text, and other values
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"

from .utils import dotdict

from faker import Faker

from collections import namedtuple
import copy
import inspect



fake = Faker()
Faker.seed(0)



#TODO: this list drives the extractions and workflow, it should be: i) loaded from file, ii)organized in groups by prefix, i.e. ref_, file_, text_, ...
record_attrs = [
        #file indexing
        "id",
        "reference_number",
        "filepath",
        "filename_original",
        "filename_modified",

        #raw / meta
        "file_extension",
        "filetype",           #- '.html','.pdf'
        "file_str",           #- raw string
        "file_document",      #- bs4, pdf
        #"file_text",          #- visible text => 'body_pages' is same
        "file_pdf_bytes",     #-converted to pdf, then bytes
        "file_uint8arr",      #-pdf_bytes to js uInt8Array

        "page_nos",
        "length_lines",
        "file_size_mb",
        "date",

        #inferred / searchable
        "title",
        "author",
        "subject",
        "toc",
        "pp_toc",

        "body_pages",
        "body",
        "clean_body",
        "readability_score",
        "tag_categories",
        "keywords",
        "summary"
]



DocumentBase = namedtuple("DocumentBase", record_attrs)



class DocumentTemplate:
     """Dotdict template to hold Document class attributes.

     Allows values to be changed after instantiation.
     """

     def __init__(self):
          pass

     def __new__(self):
          tmp = {}
          for key in record_attrs:
               tmp[key] = None
          newTmp = dotdict(tmp)
          return newTmp




class DocumentRecord(DocumentBase):
     """Extended functionality of namedtuple.

     Does NOT allow values to be changed after instantiation.
     """

     _count = 0
     _inherited_attrs = ['count','index']

     def __new__(cls, **kwargs):
          """Create new DocumentRecord object.  Ensure the 
          record maintains the correct attributes and an 
          original index number.

          Usage::
          empty_doc = DocumentRecord()
          typical_doc = DocumentRecord(title='title', author='name')
          fake_doc = DocumentRecord(id='FAKE')
          """
          idx = 'id'
          base_attrs = record_attrs
          if idx in kwargs.keys():
               if kwargs[idx] == 'FAKE':
                    new_kwargs = cls._create_fake_record(cls)
          else:
               new_kwargs = {}
               for k in base_attrs:
                    if k==idx: 
                         new_kwargs[k] = cls._get_next_index(cls)
                    elif k not in kwargs.keys(): 
                         new_kwargs[k] = None
                    else: 
                         new_kwargs[k] = kwargs[k]
          super_self = super(DocumentRecord, cls).__new__(cls, **new_kwargs)
          return super_self
     
     def _get_next_index(cls):
          """Control class index values."""
          original_count = copy.deepcopy(cls._count)
          cls._count = original_count + 1
          return original_count

     def _create_fake_record(cls):
          """Create a realistic but fake record."""
          title = 'Document Title'+str(fake.random_int())
          toc = [str(idx+1) + ') ' + fake.text(max_nb_chars = 20) for idx in range(7)]
          tmp = fake.text(max_nb_chars = 5000)
          body = ' '.join(tmp.split()).replace('\n',' ')
          summary = body[:100]
          record_values = {
               'id': cls._get_next_index(cls),
               'filepath': fake.file_path(),
               'filename_original': fake.file_name(),
               'filename_modified': title,
               'file_extension': fake.file_extension(),
               'filetype': fake.random_choices(elements=('.pdf','docx')),
               'page_nos': fake.random_int(),
               'length_lines': fake.random_int(),
               'file_size_mb': str(fake.random_int())+'KB',
               'date': fake.date_time(),
               'reference_number': fake.random_int(),
               'title': title,
               'author': fake.name(),
               'subject': fake.safe_color_name(),
               'toc': toc,
               'pp_toc': ' <br>'.join(toc),
               'body': body,
               'tag_categories': fake.random_choices(elements=('astronomy','biology','math')),
               'keywords': fake.text(max_nb_chars = 20),
               'summary': summary
          }
          check_attrs = set(record_values.keys()).difference(set(record_attrs))
          if check_attrs: 
               raise TypeError
          return record_values
     
     def validate_object_attrs(self, target):
          """Validate that an object has the same attributes
          as DocumentRecord.

          TODO: check types also

          :param target - document object
          :return result(dict[str,str]) - which attributes should be added / removed from target
          """
          from .document import Document

          if type(target) == DocumentRecord:
               lst0 = target._asdict().keys()
          elif type(target) == Document:
               lst0 = target.record.keys()
          #elif type(target) == Document:
          #     pairs = inspect.getmembers(target.record, lambda a:not(inspect.isroutine(a)))
          #     lst0 = [a[0] for a in pairs if not(a[0].startswith('_')) ]               #not(a[0].startswith('__') and a[0].endswith('__'))] )
          elif type(target) == dict:
               pairs = target.keys()
               lst0 = list(pairs)
          else:
               print(f"There was a problem with target: {target}")
               raise TypeError
          target_attrs = set( lst0 )
          docrec_attrs = set( self._asdict().keys() )
          docrec_attrs_missing = target_attrs.difference(docrec_attrs)
          target_attrs_missing = docrec_attrs.difference(target_attrs)
          result = {'target_attrs_to_remove': docrec_attrs_missing,
                    'target_attrs_to_add': target_attrs_missing,
                    }
          return result
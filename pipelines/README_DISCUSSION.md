# Discussion on foundation Task class

### Functionality:

* `get_next_run_files()`
* ~~`run_logic_on_individual_file(func)`~~
* ~~`run_logic_on_file_batches(func)`~~
* `run_logic_on_indexed_files(func)`
* `run_logic_on_batch_of_indexed_files(func)`

TODO: index = [{idx-1:['path/to/single/file.txt']}]

### Crux: 

* from many different input formats
  - individual files
  - single file with many files grouped in an index
* create a single pipeline
  - handles logging, errors, batching, ...
  - ???
* of sequenced, interchangeable task-components that work on individual records

this was the problem with spacy: not very flexible in data format and shape


### Explanation:

Text is often worked on (processed), individually.  There is a nice CS term: ridiculously parallel.  Unfortunately, that assumes all text chunks are independent.  So, if you want to break that independence, such as working on a document, or maybe information from a group of documents, then things start to get messy.  To fix this, you can add metadata for each chunk.  But, there are still many complications.





* discussion on foundation Task class
* ~~single parent class for workflow
  - just provide i) list of tasks and ii) shape of records
  - all Files and intermediate objects created for you
  - automated validation, logging, error handling, and failover
  - use pickle to preserve objects, until task penultimate to output
  - each record should be intermediary file
* record structure for Task i/o and provisioning output
  ```urls.json
  {
  'indexed group': {
    'source': 'one_of_many',
    'root_url: 'https://www...',
    'given_urls: [Url1, Url2, ...],
    'added_docs': [DocPath1, DocPath2, ...],
    'documents': [DocumentRecord, DocumentRecord, ...]
    }
  }
  ```
* indexed group | (output format) file_field | doc_display
  - wf_site_scrape-tgt: bank_name | (vdi client) Url,DocPath | Doc
  - wf_site_scrape-multi: bank_name | (table) Url | reference to docpath
  - wf_asr: acct_num | (vdi client) acct_num | {audio file-date}\n asr_text
  - wf_ecomms: msg_chain_subject | (vdi client) msg_chain_subject-msg_count | {msg file-date}\n msg_text
  - wf_text_classify: indv_file | (indv_file) indv_file | Doc
  - wf_default: indv_file | (vdi client) indv_file | Doc
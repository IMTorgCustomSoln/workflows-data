


## Usage

### All Workflows

* add `.env` file with the following variables: 
    - HF_TOKEN - huggingface account
    - HF_HOME - models dir
    - CURL_CA_BUNDLE - public key (.pem)
* ensure folders are populated:
    - `logs/`
    - `models_pretrained/`
    - `models_data/`
* set the following in `workflows/workflow_*.py`
    - `CONFIG['INPUT_DIR']` - location of input files
    - `CONFIG['WORKING_DIR']` - location for all files produced
* choose the workflow file from the `workflows/` directory.
* register it in the `main.py` file at `#register here`

```
python main.py workflow_* prepare_workspace
python main.py workflow_* run
```


### Automatic speech recognition, `-asr`

...


### Identifying and scraping websites, `-site_scrape`

* delete `tests/test_site_scrape/tmp/`
* set list of initial urls (one for each bank) in: `urls.txt`


### eComms discovery, `-ecomms`

...


### Text classification, `-text_classify`

...



## Create New Workflow

* use `template` workflow as guide (copy-paste the `tests/test_wf_*/` dir and `workflows/workflow_*.py` file)
* create new `workflows/workflow_*.py`
  - setup `test/test_wf_*/`
* config directories
* TODO: determine ingest with i) individual records, ii) record batches, or iii) indexed records
* add pipeline task components
  - review `tests/test_task/*` to fit class templates
* ensure current workspace output format: `tests/data/VDI_ApplicationStateData_v*.*.*.gz`
* build and test


## Install

Manage python versions with [pyenv](https://github.com/pyenv/pyenv).  Ensure your python version matches with Pipfile.  Create your venv with `pipenv install`.

Some external modules are maintained within this repo to enable quick editing: `src/modules/`.




## TODO: Project-level

* improve multi-model topics and Classification() class
  - ~~fix vdiworkspace export so it runs with client search: pre-run models~~
  - ~~move pretrained_models/ to models/~~ => ERRORS, can't add .env to vscode pytest
  - ~~move src/data/ to models_data/~~
  - design so that multiple models can be selected, independently, on the frontend
  - but can it still be compatible with old vdiworkspace?
* improve interactive mode with notebook.ipynb
  - enable lists, instead of Files to be used with Tasks
  - test_workflow > test_task > test_files
* update EnteroDoc module to use msft markitdown: https://github.com/microsoft/markitdown


### Wf-Ecomms

* ~~output to .json~~
* ingest data
  - create proper eDiscovery class with config (include col names)
  - ~~enable mapping provided .dat column names to default set~~
  - add text msg parse to ediscovery
  - (later)setup ediscovery with .msg parse
  - ~~improve validation rules~~
  - test
  - add to Task
* orgchart
  - ~~load orgchart~~
  - integrate org chart file: just get titles
  - add to Task
* ~~prepare models~~
* export to VDI client
* (later) add visual message display


### ASR

* create .csv list of files that are in each batch .gz
* perform analysis on log files to estimate processing time
* integrate tests/
  - ~~test_workflow_asr.py~~
  - test_prepare_config.py
  - test_export.py
  - test_export_to_vdi_workspace.py
  - test_main.py
* maybe integrate improved whisper? english-only!, [ref: whisper-medusa](https://huggingface.co/aiola/whisper-medusa-v1)
* ~~ensure multi-lingual whisper, [ref: multilingual](https://huggingface.co/openai/whisper-large-v3)~~


### Site_Scrape

* Record
  ```urls.json
  {
  'bank_name': {
    'root_url: 'https://www...',
    'given_urls: [url1,url2, ...],
    }
  }
  ```
* add more configuration items to Scenario
  - depth
  - search engine tries until timeout
* add more Crawler tests
  - check why following are validated:
    + https://www.cardcenterdirect.com/
    + https://www.umb.edu/media/umassboston/editor-uploads/research/research-amp-sponsored-programs/Cost-Transfer-Policy--Procedures.pdf
    + ...
  - check why the following error:
    + https://www.creditonebank.com/faqs/disputing-charges, 'you need to have javascript enabled to use this app'
    + ...
* documentation
  - explain configuration adjustments
* create reports
  - urls collected, validated, selected(reason)
  - document text results: hits, counts, snippets => VDI b-table export to excel, [ref](https://stackoverflow.com/questions/71465593/exporting-bootstrap-table-to-excel-or-pdf)
* compress pdf size with [`pdfsizeopt](https://github.com/pts/pdfsizeopt), but must update for py3.*, first
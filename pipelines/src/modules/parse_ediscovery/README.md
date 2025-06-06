
# Parse eDiscovery Export



## Notes on eDiscovery Files

* DATA/

  _load data_
  - .dat - load file with metadata from each document, per row
  - email from, to, subject
  - link to attachments
  - cols: `Control Number|Custodian|Date Created|Date Last Modified|Date Received|Date Sent|Document Extension|Email BCC|Email CC|Email From|Email Subject|Email To|Extracted Text|Filename|Filesize|Folder Path|Group Identifier|MD5 Hash|number of attachments|Parent Document ID|Subject|Title|FILE_PATH`
  - ascii code: þ(254)

  _options data_
  - .opt - load file mapping each image to a document
  - instance, docid, volume lable, image file path
  - cols: `Control Number, Volume, Path, ...`

  _rdo load file_
  - cols: `^Name^|^Artifact ID^|^Domains (Email BCC)^|^Domains (Email CC)^|^Domains (Email From)^|^Domains (Email To)^`

* TEXT/
  - .txt - extracted text from each document, per file
* IMAGES/
  - .tif - image files
* NATIVES/
  - original 'native' format, ie Word, Excel, etc.
  - .msg with the email text may be included


## References

* [ediscovery file types](https://www.linkedin.com/pulse/how-deal-dats-txts-opts-ediscovery-productions-goldfynch)
* [file delimiters](https://help.relativity.com/RelativityOne/Content/Relativity/Import_Export/Import_Export_Load_file_specifications.htm#:~:text=Default%20delimiters&text=Newline%E2%80%94Unicode%20174%20(ASCII%20174,ASCII%20092%20in%20the%20application))
* [data samples](https://github.com/relativitydev/relativity-import-samples/tree/main/SampleDataSources)
* [load files](https://goldfynch.com/blog/2024/05/23/the-essential-guide-to-load-files-in-ediscovery-for-legal-professionals.html)
* [checklist
](https://goldfynch.com/blog/2023/08/24/the-expert-approved-ediscovery-production-checklist.html)
* [ediscovery steps of data load](https://www.reddit.com/r/ediscovery/comments/1ajedos/what_are_the_steps_of_a_data_load/)
* [docs: relativity](https://help.relativity.com/RelativityOne/Content/Relativity/Import_Export/Import_Workflows/Document_load_file_import.htm)
* [useful parsers for common datatypes in eDiscovery workflows (Concordance, Opticon, IDX)](https://github.com/alexemorris/ED-Tools/tree/master)
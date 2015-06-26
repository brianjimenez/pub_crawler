## About
This script, papers_crawler.py, it is a simple Python script which connects to the Entrez Pubmed database (http://www.ncbi.nlm.nih.gov/pubmed) and fetches the articles published by the different specified users.

## Usage
Fetch the articles for the different users and save them in XML files:

`papers_crawler.py fetch` 

Parse and show the articles from the XML files:

`papers_crawler.py parse` 

## Dependencies
- ElementTree
- BioPython (there is a bug in many biopython packaged versions at the time of parsing the XML file, that is the reason the read function is not used)

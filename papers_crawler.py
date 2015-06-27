#!/usr/bin/env python

__author__ = 'Brian Jimenez <brian.jimenez@bsc.es>'


from Bio import Entrez
import xml.etree.ElementTree as ET
import sys


# Needed in order to let Pubmed to notify you instead of blocking your IP
crawler_contact = 'your_email@here'


def search(query):
    """Searches the query in Entrez"""
    Entrez.email = crawler_contact
    handle = Entrez.esearch(db='pubmed', 
                            sort='date', 
                            retmode='xml', 
                            term=query)
    results = Entrez.read(handle, validate=False)
    return results


def fetch_article_details(id_list):
    """Fetches the details of the articles given its pubmed ids"""
    ids = ','.join(id_list)
    Entrez.email = crawler_contact
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    lines = handle.readlines()
    return ''.join(lines)


class Article(object):
    """Represents an article"""
    def __init__(self, pmid='', title='', authors=None, published='', abstract='', journal='', iso_journal='', doi=''):
        self.pmid = pmid
        self.title = title
        if authors:
            self.authors = authors
        else:
            self.authors = []
        self.published = published
        self.abstract = abstract
        self.journal = journal
        self.iso_journal = iso_journal
        self.doi = doi

    def __str__(self):
        return '<pmid="%s", title="%s", authors="%s", journal="%s", doi="%s">' % (self.pmid, self.title, self.authors, self.journal, self.doi)


def parse_articles(xml_file_name):
    """Parses the XML found in xml_file_name

    It expects to find a set of PubmedArticle as a root node
    """
    tree = ET.parse(xml_file_name)
    root = tree.getroot()
    articles = []
    for pubmed_article in root.findall('PubmedArticle'):
        try:
            article = Article()
            for citation in pubmed_article.findall('MedlineCitation'):
                article.pmid = citation.find('PMID').text
                medline_article = citation.find('Article')
                article.title = medline_article.find('ArticleTitle').text
                journal = medline_article.find('Journal')
                article.journal = journal.find('Title').text
                article.iso_journal = journal.find('ISOAbbreviation').text
                article.abstract = medline_article.find('Abstract').find('AbstractText').text
                date_created = citation.find('DateCreated')
                year = date_created.find('Year').text
                month = date_created.find('Month').text
                day = date_created.find('Day').text
                article.published = '%s.%s.%s' % (year, month, day)

                authors_list = medline_article.find('AuthorList')
                for author in authors_list.findall('Author'):
                    last_name = author.find('LastName').text
                    initials = author.find('Initials').text
                    article.authors.append('%s,%s.' % (last_name, initials))

            pubmed_data = pubmed_article.find('PubmedData')
            article_id_list = pubmed_data.find('ArticleIdList')
            for article_id in article_id_list.findall('ArticleId'):
                type = article_id.get('IdType')
                if type == 'doi':
                    article.doi = article_id.text
        
            articles.append(article)
        except Exception, e:
            print 'Error: can not parse article. Reason: %s' % str(e)
    return articles


def usage():
    """Prints the usage of this script"""
    print 'Usage: %s action[fetch|parse]' % sys.argv[0]


if __name__ == '__main__':

    # Here more users can be defined with their alternative names in case they have
    users = {
             'bjimenez': ['jimenez-garcia b', 'jimenez, brian', 'jimenez-garci b']
    }

    if len(sys.argv[1:]) != 1:
        usage()
        raise SystemExit('Wrong command line')

    action = sys.argv[1]
    
    if action == 'fetch':
        # Fetch the articles from Entrez
        for user, names in users.iteritems():
            for id, name in enumerate(names):
                print 'Looking for %s' % name
                results = search(name)
                id_list = results['IdList']
                print id_list
                print '%d articles found for %s' % (len(id_list), name)
                papers = fetch_article_details(id_list)
                output = open('%s_%d.xml' % (user, id), 'w')
                output.write(papers)
    elif action == 'parse':
        # Parses and shows the articles
        for user, names in users.iteritems():
            for id, name in enumerate(names):
                articles = parse_articles('%s_%d.xml' % (user, id))
                for article in articles:
                    print article

    else:
        raise SystemExit('Wrong action')


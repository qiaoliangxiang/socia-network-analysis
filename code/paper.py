from datetime import date
import HTMLParser
from os import path
import re
import urllib
from xml.etree import ElementTree as ET

'''
The Paper class stores the following information for each paper: 
year of submission, month of submission, URL of the abstract, title, author list, 
and subject list.

The papers submitted in a given year and a given month are listed at an arXiv page.
The HTML class is used to fetch HTML from arXiv, store it into a local file, 
load it from a local file, and get the paper list by parsing the HTML.

The HTML contains many other unnecessary information, so the XML class is used 
to store the extracted information of a paper into a well-formated file, which
can be used for further processing.
'''
        
class Paper(object):
    
    def __init__(self):
        self.year = ''
        self.month = ''
        self.url = '' 
        self.title = '' 
        self.authors = []
        self.subjects = []
        
    def __str__(self):
        return '\nyear: {y} \nmonth: {m} \nurl: {u} \ntitle: {t}\
                \nauthors: {a} \nsubjects: {s}'\
                .format(y=self.year, m=self.month, u=self.url, t=self.title, 
                        a=self.authors, s=self.subjects)
                    
class HTML(object):
    
    'The HTML file of papers submitted in a given year and a given month.'
    
    def __init__(self, year, month, folder='.'):
        assert(type(year) == int)
        assert(type(month) == int and 1 <= month <= 12)
        assert(type(folder) == str and folder)
    
        self.year = year
        self.month = month
        self.file_path = path.join(folder, '{y}{m}.html'.format(y=year, m=month))
        self.html = ''
        
    def fetch(self):
        'Fetches the HTML content from arXiv.'
        self.html = ''
        day = date(self.year, self.month, 1).strftime('%y%m')
        url = 'http://arxiv.org/list/gr-qc/{0}?show=1000'.format(day)
        self.html = urllib.urlopen(url).read()
        return self
    
    def save(self):
        'Saves the HTML content to the HTML file.'
        assert(self.file_path and self.html)
        with open(self.file_path, 'w') as f:
            f.write(self.html)
    
    def load(self):
        'Loads the HTML content from the HTML file.'
        assert(self.file_path)
        self.html = '' # clear it
        with open(self.file_path, 'r') as f:
            self.html = f.read()
        return self
        
    def get(self):
        'Returns a list of Paper objects.'
        assert(self.html) # make sure HTML is fetched or loaded
        
        papers = list()
        num_papers = None # used for double checking
        state = -2 # used for checking the order of the elements of a paper
        
        tag = re.compile(r'<[^>]+>')
        def remove_tags(text):
            return tag.sub('', text)

        parser = HTMLParser.HTMLParser()
        def unescape(s):
            return parser.unescape(s) 
        
        paper = Paper()
        for line in self.html.splitlines():
           
            # total papers: the beginning and the end
            if 'total of ' in line and ' entries' in line:
                if num_papers is None:
                    pattern = 'total of (\d+) entries'
                    num_papers = int(re.search(pattern, line).group(1))
                else:
                    assert(len(papers) == num_papers) 
                    break 
    
            # abstract id as the URL
            if '<span class="list-identifier"><a href="' in line:
                line = line[line.find('<a href="')+9:]
                url = line[:line.find('"')].strip()
                paper.url = 'http://arxiv.org/{u}'.format(u=url)
                assert(state == -2)
                state = -1 
                
            # title
            if '<span class="descriptor">Title:</span>' in line:
                line = remove_tags(line)
                paper.title = unescape(line[line.find(':')+1:].strip())
                assert(state == -1)
                state = 0
                
            # authors     
            if '<a href="/find/'  in line:
                line = line[:line.find('</a>')] # remove everything after </a>
                paper.authors.append(unescape(line[line.rfind('">')+2:].strip()))
                state += 1
                assert(state == len(paper.authors))
                
            # subjects   
            if '<span class="descriptor">Subjects:</span>' in line:    
                line = remove_tags(line)
                line = line[line.find(':')+1:].strip()
                paper.subjects = [unescape(s.strip()) for s in line.split(';')]
                assert(state == len(paper.authors))
                
                # reset
                paper.year = self.year
                paper.month = self.month
                papers.append(paper) # save
                paper = Paper()
                state = -2
                
        return papers

    def __str__(self):
        return self.html

class XML(object):
        
    'The XML file of papers submitted in a given year and a given month.'
        
    def __init__(self, year, month, folder='.'):
        assert(type(year) == int)
        assert(type(month) == int and 1 <= month <= 12)
        assert(type(folder) == str and folder)
        
        self.year = year
        self.month = month
        self.file_path = path.join(folder, '{y}{m}.xml'.format(y=year, m=month))
        self.tree = None
        
    def set(self, papers):
        'Sets the papers.'
        assert(type(papers) == list)
        
        self.tree = None # clear it
        
        root = ET.Element('papers')
        root.set('count', str(len(papers)))
        for paper in papers:
            assert(type(paper) == Paper)
            assert(paper.year == self.year)
            assert(paper.month == self.month)
            
            p = ET.SubElement(root, 'paper')
            p.set('year', str(paper.year))
            p.set('month', str(paper.month))
            p.set('url', paper.url)
            
            t = ET.SubElement(p, 'title')
            t.text = paper.title
            
            aes = ET.SubElement(p, 'authors', {'count': str(len(paper.authors))})
            for author in paper.authors:
                ae = ET.SubElement(aes, 'author')
                ae.text = author
                
            ses = ET.SubElement(p, 'subjects', {'count': str(len(paper.subjects))})
            for subject in paper.subjects:
                se = ET.SubElement(ses, 'subject')
                se.text = subject

        self.tree = ET.ElementTree(root)
    
    def save(self):
        'Saves data to the XML file.'
        self.tree.write(self.file_path, xml_declaration=True, encoding='utf-8')
            
    def load(self):
        'Loads data from the XML file.'    
        self.tree = ET.parse(self.file_path)
        
    def get(self):
        root = self.tree.getroot()
        assert(root.tag == 'papers')
         
        papers = list()
        for p in root:
            paper = Paper()
        
            paper.year = int(p.get('year'))
            paper.month = int(p.get('month'))
            paper.url = p.get('url').strip()
            paper.title = p.find('title').text.strip()
            paper.authors = [e.text.strip() for e in p.findall('authors/author')]
            paper.subjects = [e.text.strip() for e in p.findall('subjects/subject')]
         
            papers.append(paper)
            
        return papers

    def __str__(self):
        return ET.tostring(self.tree.getroot())

def example_create_html_xml_files():

    # save to a HTML file 
    html = HTML(1993,1)
    html.fetch()
    html.save()
    
    # save to an XML file    
    xml = XML(1993,1)
    xml.set(html.get())
    xml.save()

def example_read_from_files():
    
    # read HTML file
    html = HTML(1993,1)
    html.load()
    papers = html.get()
    print(papers[0])
    
    # read XML file    
    xml = XML(1993,1)
    xml.load()
    papers = xml.get()
    print(papers[0])
                
if __name__ == '__main__':
    example_create_html_xml_files()
    example_read_from_files()
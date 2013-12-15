# -*- coding: utf-8 -*- 
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from datetime import date, timedelta
import os
from paper import HTML, XML
from paper_cleaner import clean_paper

'''
Dataset.

The papers are organized according to the year and month when they were submitted
to arXiv.
All the papers submitted in the same year and month are stored in the same file.  
There are three datasets:
    1. html: stores the original HTML content fetched from arXiv.
    2. raw_xml: stores the extracted information of papers from HTML content. 
    3. clean_xml: stores the clean information of papers from raw XML.   
'''
class Dataset(object):
    
    def __init__(self, start_date, end_date, folder='.'):
        '''Dataset.
            
        Args:
            start_date (date): the start date (inclusive)
            end_date (date): the end date (exclusive)
            folder (str): data folder 
        '''
        assert(type(start_date) == date and type(end_date) == date)
        assert(start_date < end_date)
        assert(type(folder) == str)
        
        self.start_date = start_date
        self.end_date = end_date
        self.folder = folder
        
        self.html_folder = os.path.join(self.folder,'html')
        self.raw_xml_folder = os.path.join(self.folder,'raw_xml')
        self.clean_xml_folder = os.path.join(self.folder,'clean_xml')
        
        self.__create_folder(self.html_folder, self.raw_xml_folder, 
                             self.clean_xml_folder)

    def __create_folder(self, *folders):
        for folder in folders: 
            if not os.path.exists(folder): 
                os.makedirs(folder)
    
    def __generate_year_month(self): 
        'Generates a series of valid tuples (year, month).'
        sy, sm = self.start_date.year, self.start_date.month
        ey, em = self.end_date.year, self.end_date.month
        y, m = sy, sm
        while True:
            yield (y, m) # year, month
            m += 1
            if m > 12: # increase year
                y += 1
                m = 1
            if y >= ey and m >= em: # stop
                break
                    
    def create_html(self):
        'Creates an HTML dataset.'
        for year, month in self.__generate_year_month():
            print(year, month)
            HTML(year, month, self.html_folder).fetch().save()
    
    def create_raw_xml(self):
        'Creates a raw XML dataset from the HTML dataset.'
        for year, month in self.__generate_year_month():
            papers = HTML(year, month, self.html_folder).load().get()
            XML(year, month, self.raw_xml_folder).put(papers).save()
    
    def create_clean_xml(self):
        '''Creates a clean XML dataset from the raw XML dataset.
        
        Duplicate papers are removed.
        '''
        paper_set = set()
        for year, month in self.__generate_year_month():
            new_papers = list()
            for paper in XML(year, month, self.raw_xml_folder).load().get():
                clean_paper(paper)
                key = paper.key()
                if key not in paper_set:
                    paper_set.add(key)
                    new_papers.append(paper)
            if new_papers:        
                XML(year, month, self.clean_xml_folder).put(new_papers).save()
                
    def get_clean_papers(self):
        'Returns a list of Paper instances from the clean XML dataset.'
        papers = list()
        for year, month in self.__generate_year_month():
            for paper in XML(year, month, self.clean_xml_folder).load().get():
                papers.append(papers)
        return papers
            
if __name__ == '__main__':
    
    ds = Dataset(date(1992,7,1), date(2013,12,1), os.path.join('..','data'))
#    ds.create_html() # it takes around 30 minutes to fetch the HTML 
#    ds.create_raw_xml() # generate the raw XML from HTML
#    ds.create_clean_xml() # generate clean XML from raw XML
    papers = ds.get_clean_papers()
    print(len(papers))
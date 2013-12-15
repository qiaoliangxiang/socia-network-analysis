# -*- coding: utf-8 -*-
import re
from paper import Paper

_MAP = { 
         'a': ['á','ã','ä','à','æ','å','ă'],
         'i': ['í','ï','ì','ı'],
         'o': ['ó','ö','ô','ø','ò','ő'],
         'u': ['ü','ü','ú','u','ū','u','u'],
         'e': ['é','ë','è','ê','ě','ě','ę','ȩ'],
         'c': ['ć','č','ç'],
         's': ['ś','š','ş'],
         'n': ['ń','ñ','ň'],
         'z': ['ź','ž','ż'],
         'l': ['ł','Ł'],
         'r': ['ř','ř'],
         'y': ['ý'],
         'g': ['ğ'],
         't': ['ţ'],
         'ss': ['ß']
         }
MAP = dict((v,k) for k, vs in _MAP.items() for v in vs)

def clean_paper(paper):
    '''Cleans a paper.
    
    Currently, we only deal with author names, trying to matching author names
    to real authors since an author’s name may be written in different ways. 
    We implement many heuristic rules to clean and unify author names.
    A cleaned author name only contains lowercase letters, commas, spaces, 
    and dots.
    The order of authors within a paper is preserved.
    
    The following steps are applied to each author name:
        1. change it to lower case
        2. replace - and _ by a space
        3. replace a character with diacritic mark by the corresponding letter
        4. remove multiple consecutive spaces
    
    The following steps are applied to the authors within a paper: 
        1. remove duplicate authors
    '''
    assert(type(paper) == Paper)
    
    # fix authors
    authors = paper.authors
    new_authors = list() 
    for author in authors:
        
        # lower case
        author = unicode(author).lower()
        
        # replace _ and - by a space
        author = re.sub('[-_]+', ' ', author)
        
        # replace a character with diacritic mark by the corresponding letter
        author = ''.join(MAP[str(e)] if str(e) in MAP else str(e) for e in author)
        if 'michael purrer' == author:
            author = 'michael purrer'
        elif 'thomas muller' == author:
            author = 'thomas muller'
        
        # detect invalid characters
        if r'\x' in repr(author):
            print(author)
    
        # remove a character if it is not a letter, a comma, a space, or a dot
        author = re.sub('[^a-z,. ]+', '', author)
                                                                                                                                                                                              
        # replace multiple consecutive spaces by a single space
        author = ' '.join(e for e in author.split(' ')  if e) 
        
        # other manual fix
        if 'harald lueck for the ligo scientific collaboration' in author:
            author = 'harald lueck'
        elif 'j. sadeghi m. khurshudyan m. hakobyan'  == author:
            new_authors.append('j. sadeghi')
            new_authors.append('m. khurshudyan')
            new_authors.append('m. hakobyan') 
        new_authors.append(author)
    authors = new_authors

    # remove duplicate authors within a paper without breaking author order
    author_set = set() 
    new_authors = []
    for author in authors:
        if author not in author_set:
            author_set.add(author)
            new_authors.append(author)
    authors = new_authors
    
    # finally
    paper.authors = authors
    return paper
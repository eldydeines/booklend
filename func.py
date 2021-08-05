#--------------------------------------------------------------------------#
#                   API Calls
#--------------------------------------------------------------------------#

import requests
from models import db, connect_db, Book

SEARCH_URL = "https://openlibrary.org/search.json?"
INFO_URL = "https://openlibrary.org"
COVER_URL = "http://covers.openlibrary.org/b/olid/"

class Warehouse:

    def __init__(self, title, author):
        self.title = title
        self.author = author
        self.book_search_url = ""
        self.findings = {}

    def __repr__(self):
        return f"<Warehouse title={self.title}, author={self.author}"
    
    def add_to_db(self, num, keys):
        """Add all books found to app library"""
        
        for book in range(num):
            in_Book_Tbl = Book.query.filter_by(key=self.findings['docs'][book]['key']).one_or_none()
            if in_Book_Tbl is None:
                new_book = Book(key=self.findings['docs'][book]['key'], 
                    title=self.findings['docs'][book]['title'],
                    author=self.findings['docs'][book]['author_name'],
                    description=self.findings['docs'][book]['description'],
                    subjects=self.findings['docs'][book]['subjects'],
                    cover_img_url=self.findings['docs'][book]['cover_img_url'],
                    published_year=self.findings['docs'][book]['first_publish_year'])
                db.session.add(new_book) 
                db.session.commit()      

        

    def findBooksInWH(self):
        """Find books by calling API"""
        
        books_found = {}
        books_keys = []
        
        if self.title != "" and self.author == "":
            book_search_url = SEARCH_URL + "title="+ str(self.title)
        elif self.title == "" and self.author != "":
            book_search_url = SEARCH_URL + "author="+ str(self.author)
        elif self.title != "" and self.author != "":
            book_search_url = SEARCH_URL + "title="+ str(self.title) +"&author="+str(self.author)
        else:
            return books_found

        #make API Call and save into dictionary
        self.findings = requests.get(book_search_url).json()
      
        #count number of findings if more than 10 cap the findings
        number_of_books = int(self.findings['numFound'])
        if number_of_books > 10: 
            number_of_books = 10;

        #for each book, we need to get additional information i.e. subject, description, and image url
        for doc in range(number_of_books):

            key = self.findings["docs"][doc]["key"]
            book_info_url = INFO_URL + key + ".json"
            book_info = requests.get(book_info_url).json()
            #save subject and description to findings
            self.findings['docs'][doc]['subjects'] = book_info.get('subjects', "No Subjects")
            try:
                book_info.get("description")
                try: 
                    book_info["description"].get("value")
                    self.findings['docs'][doc]['description'] = book_info["description"].get("value")
                except:
                    self.findings['docs'][doc]['description'] = book_info.get("description")
            except:  
                self.findings['docs'][doc]['description'] = "No Description"
            #using the self.findings information use either cover edition key if provided or use the edition
            edition_key = self.findings['docs'][doc]['edition_key'][0]
            cover_id = book_info.get('cover_edition_key', edition_key)
            self.findings['docs'][doc]['cover_img_url'] = COVER_URL + cover_id + "-M.jpg"

            #serialize findings
            book = {
                'key' : self.findings['docs'][doc]['key'],
                'title' : self.findings['docs'][doc]['title'],
                'author' : self.findings['docs'][doc]['author_name'],
                'description' : self.findings['docs'][doc]['description'],
                'subjects' : self.findings['docs'][doc]['subjects'],
                'cover_img_url' : self.findings['docs'][doc]['cover_img_url'],
                'first_publish_year' : self.findings['docs'][doc]['first_publish_year']
            }
            
            #append dictionary
            books_found[doc] = book
            books_keys.append(key)

        self.add_to_db(number_of_books, books_keys)

        return books_found

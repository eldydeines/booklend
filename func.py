#--------------------------------------------------------------------------#
#  Capstone Project:  BookLandia
#  Func.py is dedicated to API calls to Open Library
#  We create a class and class functions to save each search
#  A lot of time was spend on understanding this API even after 
#  conducting the necessary research. Some of the data received was 
#  inconsistent.  By providing different test cases, it helped to indentify  
#  the flaws in the API data. 
#
#  References: 
#  --- API Open Library Documentation Website
#  --- Previous projects in GitHub Repository 
#  --- SpringBoard Exercises & Lessons
#  
#  By: Eldy Deines  Date: 8/11/2021
#--------------------------------------------------------------------------#


#--------------------------------------------------------------------------#
#                           Import Necessary Libraries 
#--------------------------------------------------------------------------#


import requests
from models import db, connect_db, Book


#--------------------------------------------------------------------------#
#                           Establish baseline API URLs
#--------------------------------------------------------------------------#

SEARCH_URL = "https://openlibrary.org/search.json?"
INFO_URL = "https://openlibrary.org"
COVER_URL = "http://covers.openlibrary.org/b/olid/"


#--------------------------------------------------------------------------#
#                           Warehouse Class - stores search findings
#--------------------------------------------------------------------------#

class Warehouse:
    """ Warehouse 
        - makes the API Calls
        - cleans the data  
        - adds to Booklandia database
        - serializes data for JSON reply 
    """
    
    def __init__(self, title, author):
        """Instatiate class variables on self """
        self.title = title
        self.author = author
        self.book_search_url = ""
        self.findings = {}

    def __repr__(self):
        """Creates string identifier in command prompt"""
        return f"<Warehouse title={self.title}, author={self.author}"
    
    def add_to_db(self, num, keys):
        """Add all books found to app library"""
        
        for book in range(num):
            #Make sure book does not already exist in database
            in_Book_Tbl = Book.query.filter_by(key=self.findings['docs'][book]['key']).one_or_none()
            
            if in_Book_Tbl is None:

                #Clean up author data before adding to database
                book_authors = self.findings['docs'][book]['author_name'];
                all_authors = "";
                count = 0;
                if type(book_authors) is list:
                    for auth in book_authors:
                        if count != 0:
                            all_authors = all_authors + ", " + auth
                        else:
                            all_authors = all_authors + auth
                            count = 1;

                #Clean up subject data before adding to database
                book_subjects = self.findings['docs'][book]['subjects'];
                all_subjects = "";
                count = 0;
                if type(book_subjects) is list:
                    for subj in book_subjects:
                        if count != 0:
                            all_subjects = all_subjects + ", " + subj
                        else:
                            all_subjects = all_subjects + subj
                            count = 1;
                
                #add book to book table
                new_book = Book(key=self.findings['docs'][book]['key'], 
                    title=self.findings['docs'][book]['title'],
                    author=all_authors,
                    description=self.findings['docs'][book]['description'],
                    subjects=all_subjects,
                    cover_img_url_m=self.findings['docs'][book]['cover_img_url_m'],
                    cover_img_url_s=self.findings['docs'][book]['cover_img_url_s'],
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
            self.findings['docs'][doc]['cover_img_url_m'] = COVER_URL + cover_id + "-M.jpg"
            self.findings['docs'][doc]['cover_img_url_s'] = COVER_URL + cover_id + "-S.jpg"

            #serialize findings
            book = {
                'key' : self.findings['docs'][doc]['key'],
                'title' : self.findings['docs'][doc]['title'],
                'author' : self.findings['docs'][doc]['author_name'],
                'description' : self.findings['docs'][doc]['description'],
                'subjects' : self.findings['docs'][doc]['subjects'],
                'cover_img_url_m' : self.findings['docs'][doc]['cover_img_url_m'],
                'cover_img_url_s' : self.findings['docs'][doc]['cover_img_url_s'],
                'first_publish_year' : self.findings['docs'][doc]['first_publish_year']
            }
            
            #append dictionary
            books_found[doc] = book
            books_keys.append(key)

        self.add_to_db(number_of_books, books_keys)

        return books_found

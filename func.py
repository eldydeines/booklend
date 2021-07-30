#--------------------------------------------------------------------------#
#                   API Calls
#--------------------------------------------------------------------------#

import requests

URL = "https://openlibrary.org/search.json?"

class Warehouse:

    def __init__(self, title, author):
        self.title = title
        self.author = author
        self.findings = {}

    def findBooksInWH(self):
        """Find books by calling API"""

        print(URL)

        if self.title != "" and self.author == "":
            book_search_url = URL + "title="+ str(self.title)
        elif self.title == "" and self.author != "":
            book_search_url = URL + "author="+ str(self.author)
        elif self.title != "" and self.author != "":
            book_search_url = URL + "title="+ str(self.title) +"&author="+str(self.title)
        else:
            return False
        
        self.findings = requests.get(book_search_url).json()
        print("***************************")
        print(self.findings)
        return True
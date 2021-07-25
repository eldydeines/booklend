# Book Lend 
Book Lend will allow a neighbor to see if anyone in the area has a book that they can't find at the library or by their local book store. If they find the book, they can then ask to borrow it for a week or two. 

## Audience
The app would be utilized by people who live in remote towns or communities where Amazon may not deliver next day or where books take a while to get to your library. They know tech, but love to hold a book in their hands. 

## Data Utilized 
The app would utilize Google Book API to get various details of books to make it easier to build a user's library.  We wouldn't want an end-user to type in all data. We want the process to be easy and quick. Data Attributes: Title of Book, Author, Year Published, Front Cover Image, Synopsis. 

## Functionality
Break the app into features with the following user stories: 
- As a lender, I can find a book so that I can add it to my library.
- As a lender, I can pause books so that my library shows only books that I can lend. 
- As a borrower, I can search books that are available in all lender libraries so that I know its in stock. 
- As a borrower, I can request a book from a lender and provide contact info so that the lender can reach out to me.  
- As a borrower, I can add hearts to those that have lended a book to me so that others know the lender is amazing!
- As a lender, I can checkout a book for a borrower so that I can lend my book to the borrower. 
- As a lender, I can check my book back in upon getting it back from the borrower so that others know the book is available again. 
- As a reader, I can add a review of any lender's book so that others know if it's a good book.

## Outline
1. Build a database design and relationships: Books, Users, Lender Rating, Book Feedback.
2. Build necessary models
3. Build base template
4. Build necessary routes, rest APIs, templates and necessary model functions.  (Test each feature as I build along i.e. Unit Test.
5. Conduct Integration Testing and End-to-End Testing
6. Move build to production

## Additional Information
- Sensitive Information: All user information will be sensitive as you are providing possible address info or phone information.  Username and password information will also need to be secured. 
- Data Flow: Data Flow will be pulling from Google API just to build a lender's library. There will be restful updates (GET and PUT) to the backend when users update book statuses. A lender will be able use DELETE to remove books completely from their library.

## API OpenLibrary
[https://OpenLibrary.org/developers/api]
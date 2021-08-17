# BookLandia
For those who live in small towns with a library and a book store--the majority of the time these places don't have the book you want.  You typically have to order or reserve in advance to get the book to you. Sometimes it takes two to three weeks to get a book. You may ask, why don’t you just order from Amazon. Well, Amazon still takes five days as they deliver via USPS. We don’t get mail or prime packages at our doorstep like bigger areas/towns/cities do.  Sometimes you just want that book in your hand immediately to get a good read on. If you are a bookworm, you probably have a ton of books that you can share and may find the book two doors down if you simply asked for it. 

With my capstone project, BookLandia would allow a user to search for a particular book via OpenLibrary API. They could then add this book to their shelf that other users could borrow in the area. A user could add as many books as they want to share. Other users can then submit a request to the owner on a particular book.  The owner can then approve or deny a request. 

BookLandia has been deployed to Heroku. Check it out here: [https://booklandia.herokuapp.com/]
## Tech Stack Used
- HTML
- JavaScript with JQuery
- CSS with BootStrap and FontAwesome
- Python with Flask
- PostgreSQL

## Audience
The app would be utilized by people who live in remote towns or communities where Amazon may not deliver next day or where books take a while to get to your library. They know tech, but love to hold a book in their hands. 

## Data Utilized 
The app would utilize OpenLibary API to get various details of books to make it easier to build a user's library.  We wouldn't want an end-user to type in all data. We want the process to be easy and quick. Data Attributes: Title of Book, Author, Year Published, Front Cover Image, Synopsis(Description). 

## Features
Break the app into features with the following user stories: 

### Book Features
- "As a user, I can find a book so that I can add it to my bookshelf." This features incorporates the OpenLibrary API and will save the search findings into the books model. A user is presented with the findings and can then add the book to their bookshelf. This creates a record in the status table to link a book with an owner. 
- "As a user, I can see information about the book so that I know what it is about." From the OpenLibrary API, we pull the following information: title, book key, published date, author, description, cover images, and subjects.  Information is saved and cannot be editted to preserve the integrity of the information.  Information is then presented per book when searching or viewing the book details.
- "As an owner of a book, I can pause books so that my library shows only books that I can lend." Each book has a location and condition in the status table. The owner of the book can update the book status to show it being off shelf or can delete the book from BookLandia. 
- "As a reader, I can add reviews on any book in Booklandia so that others know if a books is good or not." Each user can have a review and a rating for a book in the bookratings table.  These reviews and ratings (which are averaged for each book) are presented with the book. 
- "As a reader, I can update my book review and rating so that I can adjust if needed." Each user has the ability to update a review if and only if they have an existing review. 
- "As a lender, I can check my book back in upon getting it back from the borrower so that others know the book is available again." A lender can update the status of the book location to "On Shelf" and will available for users to borrow again.

### User Features
- "As a user, I can register for an account in Booklandia so that I can have my own bookshelf."  Anyone can signup and will get a profile. They will immediately get access to booklandia.  Registration requires a unique username and password with additional profile information. 
- "As a user, I can login using my unique username and password so that only I have access to my bookshelf."  Every user will be authenticated using BCrypt Encrpytion hashing.  
- "As a user, I can logout of my account so that no one else gets into my session." Upon clicking logout, the user's information is removed from the session so no one else can access their information.
- "As a borrower, I can search books that are available in all user libraries so that I know its in stock."  A user can use the global search field to find a specific book.  The search runs against the title, author, and description columns of the books table. Results are rendered on the page.
- "As a borrower, I can request a book from the owner so that the owner knows that I would like to borrow it." A user can request that book upon finding it if the location states it is "On the Shelf". A request is made in the "location" column in the status table.  It will then not be visible to other users until the owner updates the status.  
- "As a lender, I can approve/disapprove the request for a borrower so that I can either lend/not lend my book to the borrower." 
- "As a lender/borrower, I can see all requests made by me or to me so that I know which books are in the limbo state." This helps the user to see everything in one place and check on statuses for those books they have requested. It also is the place that a user can see who has borrowed their book currently.
- "As a borrower, I can add hearts to those that have lended a book to me so that others know the lender is amazing!"  Users can only add a rating and review if they have borrowed/requested a book from someone. The ratings are averaged out and shown with any user when users visit the booklandiers page. 
- "As a borrower, I can update my rating or review in case lender has improved or not improved the lender experience."

## Approach - Outline
1. Build a database design and relationships: Books, Users, Lender Rating, Book Feedback.
2. Build API route to OpenLibrary
3. Build one model at a time with it's necessary routes and jinja templates
4. Along the way, test each feature to Unit Test and Regression Test.
5. Upon completion of the app, conduct Integration Testing and End-to-End Testing
6. Move build to production in Heroku

## Additional Information
- Sensitive Information: All user information will be sensitive as you are providing possible address info or phone information.  Username and password information will also need to be secured. 
- Data Flow: Data Flow will be pulling from OpenLibrarp API just to build a lender's library. There will be restful updates (GET and POST) to the backend when users update book statuses, user statuses. 

## API OpenLibrary
[https://OpenLibrary.org/developers/api]
OpenLibrary was a pretty straightforward API to use. I used the Search, Books, and Book Covers API. 
- The Search API allowed me to get all books that matched the Title and Author.  Upon receipt of the data, it required it to be cleaned up.  This api did not include all the necessary information about the books. 
- After the Search API request was made, another request was made to the Books API to get the description of the book and the subjects for that book.  This certainly created anywhere from 5-10 second lag for the end-user.
- After the Books API, I formatted the information to get the covers api url served up to save in Book Model. 
- The data was also inconsistent for the following and required massaging the data:
  - Description was sometimes not in the right object order
  - The cover image was not saved in the right pixel size.  Whenever a book looks like there is not an image, it is actually because it has been provided too small. 
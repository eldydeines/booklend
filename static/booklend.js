/** processForm: get data from form and make AJAX call to our API. */

async function processForm(evt) {

    evt.preventDefault();

    /** Get form entries */
    const title = $("#title").val();
    const author = $("#author").val();

    /** Make axios request and send entries - Wait for the response*/
    let response = await axios.get("/api/search-wh",
        { params: { title: title, author: author } });

    /** Make call to handle the response received */
    handleResponse(response);
}

/** handleResponse: deal with response from our lucky-num API. */

function handleResponse(resp) {

    /** If entries were errors - provide error and have them retry */
    searchedBooks = resp.data;

    const $showsFoundBooks = $("#shows-found-books");
    $showsFoundBooks.empty();

    let bookCount = Object.keys(searchedBooks);
    bookCount = bookCount.length;


    for (let book = 0; book <= bookCount; book++) {

        /** Shorten book description for card */
        let description = searchedBooks[book]['description'];
        if (description.length >= 300) {
            description = (description.slice(0, 300)) + "...";
        }
        /** Shorten subject content for card */
        let subjects = searchedBooks[book]['subjects'];
        let allSubjects = "";
        for (let x = 0; x <= subjects.length; x++) {
            if (x != 0) {
                allSubjects = allSubjects + ", " + subjects[x];
            }
            else {
                allSubjects = allSubjects + subjects[x];
            }
        }
        if (allSubjects.length >= 100) {
            allSubjects = (allSubjects.slice(0, 100)) + "...";
        }

        /** Shorten author content for card */
        authors = searchedBooks[book]['author'];
        let allAuthors = "";
        console.log(authors.length)
        for (let x = 0; x <= authors.length; x++) {
            if (x != 0 && authors[0] != allAuthors) {
                allAuthors = allAuthors + ", " + authors[0];
            }
            else
                allAuthors = authors[0];
        }
        if (allAuthors.length >= 100) {
            allAuthors = (allAuthors.slice(0, 100)) + "...";
        }

        /** Create card to add to DOM for each book */
        let $item = $(
            `<div class="col-md-6 col-lg-3 Show">
               <div class="card" data-show-id="${searchedBooks[book]['key']}">
                 <div class="card-body">
                   <img class="card-img-top" src="${searchedBooks[book]['cover_img_url']}">
                   <h5 class="card-title">${searchedBooks[book]['title']}</h5>
                   <h6 class="card-subtitle mb-2 text-muted">By ${allAuthors}</h6>
                   <p class="card-text">${description}</p>
                </div>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item">Published: ${searchedBooks[book]['first_publish_year']}</li>
                    <li class="list-group-item">Subject: ${allSubjects}</li>
                </ul>
                <div class="card-body">   
                    <button type="button" class="btn btn-info btn-lg" data-show-id="${searchedBooks[book]['key']}">Add Book to My Library</button>
                </div>
            </div>
        `);

        $showsFoundBooks.append($item);
    }

}

$("#find-book-form").on("submit", processForm);


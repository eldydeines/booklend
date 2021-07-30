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
    console.log(resp.data)
    $("#search-results").empty().
        $("#search-results").empty().append(`${resp.data}`)

}

$("#find-book-form").on("submit", processForm);

// Sort Method Change Handler
var baseUrl = window.location.origin;
var selectSortMethod = document.querySelector("#sort_method"); // Select Tag for Sort Method

var selectTagChangedHandler = function(e) {
    var sortMethodValue = selectSortMethod.value; // Sort method value in select tag
    var destURL = baseUrl + "/?sort_method=" + sortMethodValue // Destination URL with selected sort method
    window.location.href = destURL // Redirect Client to Destination URL
}

selectSortMethod.addEventListener("change", selectTagChangedHandler)
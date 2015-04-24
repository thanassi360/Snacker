//var URL = "http://127.0.0.1:8080/";
var URL = "http://snackerapp.appspot.com/";
var user = localStorage.getItem("view_user");


$(document).ready( function() {
    doUserGet();
});

function doUserGet() {
    $.ajax({
        type: "GET",						// The HTTP operation
        url: URL + "user/" + user,	        // The URL
        async: true,						// This is the default
        contentType: "application/json",	// MIME type function expects...
        dataType: 'json',					// ...and the type of data expected
        success: function(json) {			// Do this if it worked
            console.log(json);
            handleUser(json);
        },
        error: function(e) {				// Do this if it failed
            console.log(e);
        }
    });
    // Good idea to display the last update time...
    var d = new Date(),
    t = twoDigit(d.getHours()) + ":" + twoDigit(d.getMinutes());
    $("#lastUpdate").text("Last updated: " + t);
}

// Generic function to format time strings etc...
function twoDigit(v) {
    if(v < 10) {
        return "0" + v;
    } else {
        return v;
    }
}

function formatThumbs(userPage) {
    var html = "<img class='userThumb' src='/thumb/" + userPage.src + "' alt='A thumbnail' />";
    return html;
}

function handleUser(userDetails) {
    var userHtml = "<div class='col-lg-4 col-sm-6 col-xs-12'><h1>"+userDetails.name+"</h1>" +
        "<p>"+userDetails.description+"<br />"+userDetails.joindate+"</p>"
    ;
    imageList = ""
    for(var i=0; i < userDetails.images.length; i += 1){
        console.log(userDetails.images[i]);
        imageList += formatThumbs(userDetails.images[i]);

    }
    var output = userHtml + imageList +"</div>";
    displayResults(output);
}

function displayResults(userOutput){
    $("#userfeed").html(userOutput);
}
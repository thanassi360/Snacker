//var URL = "http://127.0.0.1:8080/";
var URL = "http://snackerapp.appspot.com/";

$(document).ready( function() {
    // First stage is always to wire up the user-interface controls.
    // 1. The POST button...
    doGetRequest();
    checkConnection();
    $('body').on('click', 'button[name=comment]', function(){
        var buttonVal = $(this).val();
        var comment = document.getElementById(buttonVal).value;
        alert(comment);
    });
    $('body').on('click', 'a[name=comment]', function(){
        var buttonVal = $(this).val();
        var comment = document.getElementById(buttonVal).value;
        alert(comment);
    });
});



function checkConnection(){
    if(window.navigator.onLine){
        $("#status").html("Status: online");
        return true;
    } else {
        $("#status").html("Status: offline");
        return false;
    }
}

function doGetRequest() {
	// The parameters for this are important.
    $.ajax({
        type: "GET",						// The HTTP operation
        url: URL + "stream",	            // The URL
        async: true,						// This is the default
        contentType: "application/json",	// MIME type function expects...
        dataType: 'jsonp',					// ...and the type of data expected
        success: function(json) {			// Do this if it worked
            console.log(json);
            handlePosts(json);
        },
        error: function(e) {				// Do this if it failed
            console.log("error");
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

function formatPost(postBody) {
    var html = "<div class='col-lg-4 col-sm-6 col-xs-12'>";
    html += "<img class='postImage' src='/serve/" + postBody.src + "' />" +
            "<p><a href='/user' name='"+ postBody.username +"' class='postUser' onclick='viewUser(this.name)'>" + postBody.username + " </a></p>" +
            "<p class='postComment'>" + postBody.description + "</p>" +
            "<form>" +
            "<textarea rows='4' cols='50' id='"+postBody.src+"'></textarea>" +
            "<button type='button' name='comment' value='"+postBody.src+"'>Comment</button></form>";
    html += "</div>";
    return html;
}

function handlePosts(posts) {
    var i, list = "";
    for(i=0; i < posts.length; i += 1) {
        list += formatPost(posts[i]);
    }
    displayResults(list);
    // Stash all of these in localStorage (overwrite any previous list)...
    localStorage.setItem("recent_posts", list);
}

function displayResults(list){
    $("#timelineFeed").html(list);
}

function viewUser(userName){
    var user = userName;
    console.log(user);
    localStorage.setItem("view_user", user);

};
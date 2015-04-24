//var URL = "http://127.0.0.1:8080/";
var URL = "http://snackerapp.appspot.com/";

$(document).ready( function() {
    doGetRequest();
    checkConnection();
    $('body').on('click', 'button[name=comment]', function(){
        var buttonVal = $(this).val();
        var comment = document.getElementById(buttonVal).value;
        $("#"+buttonVal).css('display', 'none');
        $("#but-"+buttonVal).css('display', 'none');
        document.getElementById(buttonVal).value = "";
        alert(comment);
        //doCommentPost(buttonVal, comment);
    });
    $('body').on('click', 'button[name=allowComment]', function(){
        var showID = $(this).val();
        if($("#"+showID).css('display')== 'none'){
            $("#"+showID).css('display', 'block');
            $("#but-"+showID).css('display', 'inline');
        }
        else{
            $("#"+showID).css('display', 'none');
            $("#but-"+showID).css('display', 'none');
        }
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
        dataType: 'json',					// ...and the type of data expected
        success: function(json) {			// Do this if it worked
            console.log(json);
            handlePosts(json);
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

/*function doCommentPost(formData) {
    $.ajax({
        type: "POST",
        url: uploadURL,
        data: formData,
        dataType: "json",
        processData: false,
        contentType: false
    }).done(function(data, textStatus, jqXHR){ // None of these params are used (see jQuery docs)
        console.log(formData);
    }).always(function(data, textStatus){

    });
}*/

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
            "<p class='postComment'><a href='/user' name='"+ postBody.username +"' class='postUser' onclick='viewUser(this.name)'>" + postBody.username + ": </a>" + postBody.description + "</p>" +
            "<form>" +
            "<button name='allowComment' value='"+postBody.src+"' type='button' class='btn btn-default'><span class='comment glyphicon glyphicon-pencil' aria-hidden='true'></span></button>" +
            "<button style='display:none;' type='button' name='comment' id='but-"+postBody.src+"' value='"+postBody.src+"' class='btn btn-default'><span class='comment glyphicon glyphicon-send' aria-hidden='true'></span></button></form>" +
            "<textarea style='display:none;' rows='4' cols='40' id='"+postBody.src+"'></textarea>";
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
}
//var URL = "http://127.0.0.1:8080/";
var URL = "http://snackerapp.appspot.com/";
var currentUser = localStorage.getItem("current_user");
var user = localStorage.getItem("view_user");
var buffer = "<div style='height:160px; float:left; width: 95%; text-align: center;'>" +
    "<br />That's All The Delicious Pictures For Now<br />Come Back Soon!</div>";
var onlineStatus = "";
var offline = "<p>Sorry, you are currently offline, but here is some stuff we saved from last time.</p>";
var offlinePlaceholder = "<p>Sorry, you are currently offline, come back soon to see some tasty treats.</p>";
localStorage.setItem("current_version", "Alpha v1.02");             //updates the local storage value of the version

$(document).ready( function(){
    $('body').on('click', 'button[name=comment]', function(){       //assigns an on click event to the submit buttons
        var buttonVal = $(this).val();                              //for commenting
        var comment = document.getElementById(buttonVal).value;
        $("#"+buttonVal).css('display', 'none');
        $("#but-"+buttonVal).css('display', 'none');
        document.getElementById(buttonVal).value = "";
        handleCommentPost(buttonVal, comment);
    });
    $('body').on('click', 'button[name=allowComment]', function(){  //assigns an on click event to make the comment
        var showID = $(this).val();                                 //text box and submit button visible
        if($("#but-"+showID).css('display')== 'none'){
            $("#but-"+showID).css('display', 'inline');
        }
        else{
            $("#but-"+showID).css('display', 'none');
        }
    });
    $('body').on('click', 'button[name=update-user]', function(){   //assigns an on click event to the submit button
        var newName = $("#userName").val();                         //on the profile page and triggers an ajax
        var newBio = $("#userBio").val();                           //post to update the current users name and bio
        handleUserUpdate(newName, newBio);
        localStorage.removeItem("current_user");                    //removes the current users name from local storage
    });
    $("#postButton").bind('click', function(event){                 //on click event to trigger an ajax post
    	postNewMessage();                                           //on the capture page
        event.preventDefault();
    });
    $("#resize").bind('click', function(){                          //on click event that triggers the image cropping
    	$("#show-description").css('display', 'block');             //script and displays the description text input
    });                                                             //and submit button
    checkConnection();
    var d = new Date(),
    t = twoDigit(d.getHours()) + ":" + twoDigit(d.getMinutes());
    $("#lastUpdate").text("Last updated: " + t);
    setVersion();
    if(navigator.userAgent.match(/Android/i)){
    window.scrollTo(0,1);
 }
});
function checkConnection(){                                         //checks the network connection and displays the
    if(window.navigator.onLine){                                    //status on the page, then assigns the status to
        $("#status").html("Status: online");                        //a variable that is used later in the script
        onlineStatus="online";
        return true;
    } else {
        $("#status").html("Status: offline");
        onlineStatus="offline";
        return false;
    }
}
function twoDigit(v) {                                              //formats the update time displayed on the page
    if(v < 10) {
        return "0" + v;
    } else {
        return v;
    }
}
function setVersion(){                                              //updates the version number anchor tag in the nav
    var snackerVersion = localStorage.getItem("current_version");   //bar on each page, based on the local storage entry
    $("#release").html(snackerVersion);
}

////// PAGE ON LOAD FUNCTIONS //////

function homePage(){                                                //page on load event that uses the online status
    if(onlineStatus =="online"){                                    //variable set earlier in an if statement to either
        doGetCurrentUser();                                         //triggers ajax get requests for the home timeline
        doGetRequest();                                             //and current user or uses local storage for the
    }                                                               //timeline if offline
    else{
        var local = localStorage.getItem("recent_posts");
        $("#feed").html(offline+local+buffer);
    }
}
function userPage(){                                                //page on load event that takes a user name from
    if(onlineStatus =="online"){                                    //local storage that is assigned when the users
        doUserGet();                                                //name is clicked on the timeline and triggers an
    }                                                               //ajax get request for that users' profile page
    else{                                                           //displays an offline message if no network available
        $("#feed").html(offlinePlaceholder);
    }
}
function profilePage(){                                             //page on load event that uses the current user value
    if(onlineStatus =="online"){                                    //in local storage to trigger an ajax request for
            doCurrentUserGet()                                      //the current user profile page
    }                                                               //displays local storage data if no network available
    else{
        var local = localStorage.getItem("my_page");
        $("#feed").html(offline+local+buffer);
    }

}

////// END OF ON LOAD //////

////// GLOBAL FUNCTIONS //////

function doGetCurrentUser() {                                       //get request for the current user
    $.ajax({
            type: "GET",
            url: URL + "currentuser",
            async: true,
            contentType: "application/json",
            dataType: 'json',
            success: function(json) {
                handleCurrentUser(json);
            },
            error: function(e) {
                console.log(e);
            }
        });
}
function handleCurrentUser(user) {                                  //assigns current users ID to local storage
    var userID = user.name;
    localStorage.setItem("current_user", userID);
}

////// END OF GLOBAL //////

////// HOMEPAGE FUNCTIONS ///////

/// TIMELINE FUNCTIONS ///

function doGetRequest() {                                           //get request for the home page timeline
    $.ajax({
        type: "GET",
        url: URL + "stream",
        async: true,
        contentType: "application/json",
        dataType: 'json',
        success: function(json) {
            handleGet(json);
        },
        error: function(e) {
            console.log(e);
        }
    });
}
function handleGet(posts) {                                         //processing of the timeline get request into
    var i, list = "";                                               //individual user posts and assigning to local
    for(i=0; i < posts.length; i += 1) {                            //storage in the event of network being unavailable
        list += formatGet(posts[i]);
    }
    displayResults(list);
    localStorage.setItem("recent_posts", list);
}
function formatGet(postBody) {                                      //formatting of each user post into an image, user name,
    var commenthtml="";                                             //description, comments and comment form
    if(postBody.comments.length > 0){
        for(var i=0; i < postBody.comments.length; i++){
            commenthtml += "<div class='singleCom'><p class='comment-view'>" +
            "<a>"+postBody.comments[i].username+":</a> "+postBody.comments[i].content+"<br />" +
            "<br /><a class='timestamp'>"+postBody.comments[i].timestamp+"</a></p></div>";
        }
    }
    var html = "<div class='col-lg-4 col-sm-6 col-xs-12'>";
    html += "<img class='postImage' src='/serve/" + postBody.src + "' />" +
            "<p class='postComment'><a href='/user' name='"+ postBody.username +"' class='postUser' onclick='viewUser(this.name)'>" + postBody.username + ": </a>" + postBody.description + "</p><div class='collapse' id='com-"+ postBody.src +"'>" + commenthtml + "</div>" +
            "<button name='allowComment' value='"+postBody.src+"' type='button' class='btn btn-default' data-toggle='collapse' data-target='#col-"+ postBody.src +"'><span class='comment glyphicon glyphicon-pencil' aria-hidden='true'></span></button>" +
            "<button type='button' class='btn btn-default' data-toggle='collapse' data-target='#com-"+ postBody.src +"'><span class='comment glyphicon glyphicon-sunglasses' aria-hidden='true'></span></button>" +
            "<button style='display:none;' type='button' name='comment' id='but-"+postBody.src+"' value='"+postBody.src+"' class='btn btn-default'><span class='comment glyphicon glyphicon-send' aria-hidden='true'></span></button>" +
            "<div class='collapse' id='col-"+ postBody.src +"'><textarea rows='4' cols='40' id='"+postBody.src+"'></textarea></div></div>";
    html += "</div>";
    return html;
}
function displayResults(list){                                      //output of formatted user posts to the page
    $("#feed").html(list+buffer);                                   //with a buffer div at the end
}

/// COMMENT FUNCTIONS ///

function handleCommentPost(pict, comment) {                         //triggers an ajax post for comments
    commentData = JSON.stringify({"photoid": pict, "comment": comment});
    doCommentPost(commentData);
}
function doCommentPost(commentBody) {                               //post request for comments made on user posts
    $.ajax({                                                        //performs a get request as part of the post
        type: "POST",                                               //as more efficient than a reload
        url: URL + "comment",
        data: commentBody,
        dataType: "json",
        processData: false,
        contentType: false
    }).done(function(){
    }).always(function(data, textStatus){
        doGetRequest();
    });
}

/// VIEW USER FUNCTION ///

function viewUser(userName){                                        //triggered by a hyperlink onclick to assign a user
    var user = userName;                                            //name to local storage which is used in a get request
    localStorage.setItem("view_user", user);                        //on the user page
}

////// END OF HOMEPAGE //////

////// CAPTURE PAGE FUNCTIONS //////

function postNewMessage() {                                         //gathers data and triggers an ajax post for a
    var description=$("#desc").val(),                               //submitted image
        image=$("#pict").val(),
        formData = JSON.stringify({"blob": image, "description": description});
        doPostRequest(formData);
}
function doPostRequest(formData) {                                  //post request for image and description
    $.ajax({
        type: "POST",
        url: URL + 'upload',
        data: formData,
        dataType: "json",
        processData: false,
        contentType: false
    }).done(function(){
    }).always(function(data, textStatus){
        window.location = "/";
    });
}

////// END OF CAPTURE PAGE //////

////// USER PAGE FUNCTIONS //////

function doUserGet() {                                              //get request for viewing a user profile, uses the
    $.ajax({                                                        //local storage variable assign when a user clicks
        type: "GET",                                                //on a user hyperlink on the timeline
        url: URL + "user/" + user,
        async: true,
        contentType: "application/json",
        dataType: 'json',
        success: function(json) {
            handleUser(json);
        },
        error: function(e) {
            console.log(e);
        }
    });
}
function viewThumbs(userPage) {                                     //processing of images for the user page
    var html = "<img class='userThumb' src='/thumb/" +
        userPage.src + "' alt='A thumbnail' />";
    return html;
}
function handleUser(userDetails) {                                  //produces elements that make up the user page
    var userHtml = "<div class='col-lg-4 col-sm-6 col-xs-12'>" +    //and adds the processed images at the end
            "<h2>"+userDetails.name+"</h2>" +
            "<p>"+userDetails.description+"<br />" +
            "Joined Snacker: "+userDetails.joindate+"</p>"
    ;
    imageList = ""
    for(var i=0; i < userDetails.images.length; i += 1){
        imageList += viewThumbs(userDetails.images[i]);
    }
    var output = userHtml + imageList +"</div>";
    displayUser(output);
}
function displayUser(userOutput){                                   //outputs the html element to the user page
    $("#feed").html(userOutput+buffer);
}

////// END OF USER PAGE //////

////// PROFILE PAGE FUNCTIONS //////

/// GET CURRENT USER DETAILS ///
function doCurrentUserGet() {                                       //get request for the current user, using the variable
    $.ajax({                                                        //that is assigned in local storage
        type: "GET",
        url: URL + "user/" + currentUser,
        async: true,
        contentType: "application/json",
        dataType: 'json',
        success: function(json) {
            handleCurrentUserData(json);
        },
        error: function(e) {
            console.log(e);
        }
    });
}
function handleCurrentUserData(userDetails) {                       //produces form elements for current user, with update
    var userHtml = "<div class='col-lg-4 col-sm-6 col-xs-12'>" +    //button linked to an ajax post request
            "<form onsubmit='updateUser(userName, userBio)'><table id='userTable'>" +
            "<tr><td id='label'>Username: </td><td id='field'><input class='input' type='text' id='userName' value='"+ userDetails.name +"'></td></tr>" +
            "<tr><td>Bio: </td><td rowspan='2'><textarea id='userBio' class='input'>"+ userDetails.description +"</textarea></td></tr>" +
            "<tr><td><button type='button' name='update-user'>Update</button></td></tr>" +
            "<tr><td colspan='2' align='center'>Snacker since: "+ userDetails.joindate +"</td></tr>" +
            "</table></form></div><br />"
    ;
    imageList = "";
    for(var i=0; i < userDetails.images.length; i += 1){            //produces a list of images attached to current user
        imageList += formatThumbs(userDetails.images[i]);

    }
        localStorage.setItem("my_page", imageList);
    var output = userHtml + imageList +"</div>";
    displayCurrentUser(output);
}
function displayCurrentUser(userOutput){                            //outputs html element to the profile page
        $("#feed").html(userOutput+buffer);
}
function formatThumbs(userPage) {                                   //formats the images into html image tags
    var html = "<img class='userThumb' src='/thumb/" +
        userPage.src + "' alt='A thumbnail' />";
    return html;
}

/// END OF CURRENT USER ///

/// UPDATE USER FUNCTIONS ///

function handleUserUpdate(newName, newBio){                         //gathers data and triggers an ajax post to update user
    userForm = JSON.stringify({"username": newName, "description": newBio});
    updateUser(userForm);
}
function updateUser(userForm) {                                     //post request for updating the current users name
    $.ajax({                                                        //and bio
        type: "POST",
        url: URL + 'update',
        data: userForm,
        dataType: "json",
        processData: false,
        contentType: false
    }).done(function(){ // None of these params are used (see jQuery docs)
    }).always(function(data, textStatus){
        doGetCurrentUser();
    });
}
/// END OF UPDATE USER ///

////// END OF PROFILE PAGE //////

////// VERSION PAGE FUNCTIONS //////



////// END OF VERSION PAGE //////











































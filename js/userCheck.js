//var URL = "http://127.0.0.1:8080/";
var URL = "http://snackerapp.appspot.com/";
var currentUser = localStorage.getItem("current_user");

$(document).ready( function() {
    doGetUser();
});

function doGetUser() {
    if(currentUser===null){
        $.ajax({
            type: "GET",						// The HTTP operation
            url: URL + "currentuser",	            // The URL
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
    }
    else{
        console.log("User Exists");
    }
}

function handleUser(user) {
    var userID = user.name;
    console.log(userID);
    localStorage.setItem("current_user", userID);
}

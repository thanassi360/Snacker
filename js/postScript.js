var URL = "http://127.0.0.1:8080/url";
//var URL = "http://snackerapp.appspot.com/url";

var uploadURL = "";

$(document).ready( function() {
    // First stage is always to wire up the user-interface controls.
    // 1. The POST button...
    $("#postButton").bind('click', function(event){
    	postNewMessage();
        // prevent default posting of the form (since we're making an Ajax call)...
        event.preventDefault();
    });
    getURL();
});

function getURL() {
	// The parameters for this are important.
    $.ajax({
        type: "GET",						// The HTTP operation
        url: URL,	            	// The URL
        async: true,						// This is the default
        contentType: "application/json",	// MIME type function expects...
        dataType: 'jsonp',					// ...and the type of data expected
        success: function(json) {			// Do this if it worked
            console.log(json);
            uploadURL = json[0].url;
        },
        error: function(e) {				// Do this if it failed
            console.log("error");
        }
    });
}

function doPostRequest(formData) {
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
}

function postNewMessage() {
    var description=$("#desc").val(),
        image=$("#pict").get(0).files[0];
        var formData = new FormData();
        var blob = new Blob([image],{type:"image/jpeg"});
        formData.append("blob",blob);
        formData.append("description",description);
        console.log(formData);
        doPostRequest(formData);
}
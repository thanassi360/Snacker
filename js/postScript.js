//var URL = "http://127.0.0.1:8080/";
var URL = "http://snackerapp.appspot.com/";

$(document).ready( function() {
    $("#postButton").bind('click', function(event){
    	postNewMessage();
        // prevent default posting of the form (since we're making an Ajax call)...
        event.preventDefault();
    });
});

function doPostRequest(formData) {
    $.ajax({
        type: "POST",
        url: URL + 'upload',
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
        image=$("#pict").val(),
        formData = JSON.stringify({"blob": image, "description": description})
        console.log(formData);
        doPostRequest(formData);
}



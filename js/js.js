
var imageList = null,
    imageId = null;
var url = "http://localhost:8080/stream"
$(document).ready(function() {



    // Get user logged in some way...
    //imageList = localStorage.getItem('currentImageList');
    //imageId = imageList[0];

$.ajax({
    url: url,
    dataType: "jsonp",
    async: true,
    success: function (result) {
        console.log(result);
        x = result;
        console.log(x);
        $("#image").attr("src", "/serve/"+x[0].src);

    },
    error: function (error) {
        console.log("Network error occured")
    }
});

  /*  $("#getimage").on('click', function() {
        for (var index = 0; index < 3; index += 1) {
            getImage(imageId);
        }
    });

    $(")*/

});

/*
function getImage(imageID) {
    $.ajax({
        type: 'get',
        url: "/images" + imageId,
        async: true,
        contentType: 'application/json',
        dataType: 'jsonp',
        success: function(data) {
            $("#image").attr('src', data.src);
        },
        error: function(err) {

        }
    });
}*/

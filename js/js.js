
var imageList = null,
    imageId = null;

$(document).ready(function() {

    // Get user logged in some way...
    imageList = localStorage.getItem('currentImageList');
    imageId = imageList[0];

    $.ajax({
        type: 'get',
        url: "/",       // Get a list of images.
        async: true,
        contentType: 'application/json',
        dataType: 'jsonp',
        success: function(data) {
            imageList= data;
            localStorage.setItem('currentImageList', data);
        },
        error: function(err) {
            imageList = localStorage.getItem('currentImageList');
        }
    });

    $("#getimage").on('click', function() {
        for (var index = 0; index < 3; index += 1) {
            getImage(imageId);
        }
    });

    $(")

});

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
}       \
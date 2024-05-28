function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

var interval = null;

function ping(request_id) {
    var res = false;

    $.ajax({
        url: 'http://127.0.0.1:8090/ping/video/' + request_id + '-pipline.mp4',
        type: 'get',
        data: {},
        cache: false,
        processData: false,
        contentType: false,
        success: function(response) {
            console.log(response)
            res = response.is_exist;
            if (res) {
                clearInterval(interval);
                $('#file-upload-form')[0].reset();
                    $("#loading").css("display", "none");
                    $("#step-2").css("display", "block");
                    var video = $('<video />', {
                        src: 'http://127.0.0.1:8090/video/video/' + request_id + '-rgb.mp4',
                        type: 'video/mp4',
                        width: "600",
                        controls: true
                    });
                    video.appendTo($('#rgb-video'));
        
                    var video = $('<video />', {
                        src: 'http://127.0.0.1:8090/video/video/' + request_id + '-depth.mp4',
                        type: 'video/mp4',
                        width: "600",
                        controls: true
                    });
                    video.appendTo($('#depth-video'));
        
                    var video = $('<video />', {
                        src: 'http://127.0.0.1:8090/video/video/' + request_id + '-pipline.mp4',
                        type: 'video/mp4',
                        width: "600",
                        controls: true
                    });
                    video.appendTo($('#pipline-video'));
            }
        }
    });
    
}
// Authorization

async function upload(event) {
    event.preventDefault();
    var data = new FormData($('form').get(0));
    $("#step-1").css("display", "none");
    $("#loading").css("display", "block");
    $("#error").css("display", "none");
    $.ajax({
        url: $(this).attr('action'),
        type: $(this).attr('method'),
        beforeSend: function (xhr) {
            xhr.setRequestHeader('Authorization', 'Bearer ' + getCookie('session'));
        },
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function(response) {
            console.log(response);
            var request_id = response.request_id;
            if (request_id != 'not_valid'){
                interval = setInterval(function () {
                    ping(request_id);
                }, 10000);
            }
            else{
                $("#step-1").css("display", "block");
                $("#loading").css("display", "none");
                $("#error").css("display", "block");

            }
            
            
        }
    });
    return false;
}



    
$(function() {
    $('form').submit(upload);

});
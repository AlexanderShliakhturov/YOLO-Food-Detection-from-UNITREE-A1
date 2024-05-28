function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

async function login(event) {
    event.preventDefault();
    var data = new FormData($('form').get(0));
    $("#error").css("display", "none");
    $.ajax({
        url: $(this).attr('action'),
        type: $(this).attr('method'),
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function(response) {
            console.log(response);
            setCookie('session', response.access_token, 1)
            window.location.href = '/'; // переход на главную страницу
        },
        error: function(response) {
            $("#error").css("display", "block");
        }
    });
    
    return false;
}

$(function() {
   
    $('form').submit(login);
    
});

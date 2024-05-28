function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

async function register(event) {
    event.preventDefault();
    var data = new FormData($('form').get(0));
    $("#error").css("display", "none");
    if (data.get('password').length >= 10 && data.get('username') != data.get('password') && data.get('password') == data.get('confirm_password')) {
        $.ajax({
            url: $(this).attr('action'),
            type: $(this).attr('method'),
            data: data,
            cache: false,
            processData: false,
            contentType: false,
            
            success: function(response) {
                console.log(response);
                setCookie('session', response.access_token, 1);
                console.log(response)
                if (response.is_succes) {
                    window.location.href = '/'; // переход на главную страницу
                }
            }
        });
    }
    else{
        $("#error").css("display", "block");
    }
    
    return false;
}

$(function() {
    $('form').submit(register);

});
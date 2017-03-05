/* global $ */

$(function(){
    var $count = 500 - $('#about_me').val().length;
    $('.chars-left').text($count);
    
    $('#about_me').on('input', function(){
        var $count = 500 - $('#about_me').val().length;
        if($count >= 0){
            $('.chars-left').text($count);
        }
        else{
            var new_val = $('#about_me').val().toString().substr(0,500);
            $('#about_me').val(new_val);
            $('.chars-left').text(0);
        }
    });
});
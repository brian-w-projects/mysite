/* global $ */

$(function(){
    var $count = 250 - $('.textentry').val().length;
    $('.chars-left').text($count);
    
    $('.textentry').on('input', function(){
        var $count = 250 - $('.textentry').val().length;
        if($count >= 0){
            $('.chars-left').text($count);
        }
        else{
            var new_val = $('.textentry').val().toString().substr(0,250);
            $('.textentry').val(new_val);
            $('.chars-left').text(0);
        }
    });
});
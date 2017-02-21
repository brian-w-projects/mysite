/* global $ */

$(function(){
    var $count = 500 - $('#about_me').val().length;
    $('.chars-left').text($count);

    $('#about_me').on('input', function(){
        var $count = 500 - $('#about_me').val().length;
        $('.chars-left').text($count);
    });
});
/* global $ */

$(function(){
    $('.flash-close').on('click', function(){
        $(this).parent().css('display', 'none');
    });
});
/* global $ */
/* global gotoF */
/* global id */

$(function(){
    $('.to_check').each(function(){
        var $to_mod = $(this);
       $to_mod.on('click', function(){
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: gotoF,
                datatype:'json',
                data: {'id': $(this).attr('id'), 'follow':$(this).text()},
                success: function(x){
                    $to_mod.parent().hide();
                    $to_mod.parent().next().hide();
                }
            });
        }); 
    });
});
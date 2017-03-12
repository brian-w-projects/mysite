/* global $ */
/* global goto */
/* global gotoM */

$(function(){
    $('.listrecs').on('click', '.to_check', function(){
        var $to_mod = $(this);
        var $id = $(this).attr('id');
        var $action = $(this).hasClass('verify');
        $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: gotoM,
            datatype:'json',
            data: {'id': $id, 'verify':$action},
            success: function(x){
                $to_mod.parent().hide();
                $to_mod.parent().next().hide();
            }
        });
    });
    
    $('#ajax').bind('click', function(){
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: goto,
           datatype:'json',
           success: function(x){
               $('.listrecs').append(x);
               if($('.empty').length){
                   $('.loadMore').css('display', 'none');
               }
           }
        });
    });
});
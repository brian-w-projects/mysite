/* global $ */
/* global goto */
/* global gotoM */
/* global id */
/* global page */

$(function(){
    $('.to_check').each(function(){
        var $to_mod = $(this);
        var $id = $(this).attr('id');
        $to_mod.on('click', function(){
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: goto,
                datatype:'json',
                data: {'id': $id, 'follow':false},
                success: function(x){
                    $to_mod.parent().hide();
                    $to_mod.parent().next().hide();
                }
            });
        }); 
    });
    
    $('.ajax').bind('click', function(){
        page += 1;
        $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: gotoM,
            datatype:'json',
            data: {'id': id, 'page':page},
            success: function(x){
                $('.loadMore').before(x);
               if($('.empty').length){
                    $('.loadMore').hide();
                }
            }
        });
    });
});
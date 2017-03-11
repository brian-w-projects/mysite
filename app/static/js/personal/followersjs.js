/* global $ */
/* global goto */
/* global id */

$(function(){
    $('.ajax').bind('click', function(){
        $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto,
            datatype:'json',
            data: {'id': id},
            success: function(x){
                $('.listrecs').append(x);
               if($('.empty').length){
                    $('.loadMore').hide();
                }
            }
        });
    });
});
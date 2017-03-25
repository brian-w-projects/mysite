/* global $ */
/* global goto */
/* global id */
/* global page */

$(function(){
    $('.ajax').bind('click', function(){
        page += 1;
        $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto,
            datatype:'json',
            data: {'id': id, 'page': page},
            success: function(x){
                $('.listrecs').append(x);
               if($('.empty').length){
                    $('.loadMore').hide();
                }
            }
        });
    });
});
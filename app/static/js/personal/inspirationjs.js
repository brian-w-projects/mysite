/* global $ */
/* global goto */
/* global page */

$(function(){
    $('#ajax').bind('click', function(){
        page += 1;
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: goto,
           datatype:'json',
           data: {'page':page},
           success: function(x){
               $('.listrecs').append(x);
               if($('.empty').length){
                   $('.loadMore').css('display', 'none');
               }
           }
        });
    });
});


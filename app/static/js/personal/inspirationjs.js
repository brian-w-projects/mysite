/* global $ */
/* global goto */

$(function(){
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


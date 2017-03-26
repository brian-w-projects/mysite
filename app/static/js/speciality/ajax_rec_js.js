/* global $ */
/* global goto */

var page = 1;

$(function(){
    $('#ajax_recs').on('click', function(){
        page += 1;
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: goto,
           datatype:'json',
           data: {'page': page},
           success: function(x){
               $('.loadMore').before(x);
               if($('.empty').length){
                   $('.loadMore').hide();
               }
           }
        });
    });
});
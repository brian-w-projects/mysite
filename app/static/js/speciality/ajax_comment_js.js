/* global $ */
/* global gotoCom */

var pageCom = 1;

$(function(){
    $('#ajax_comments').on('click', function(){
        pageCom += 1;
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: gotoCom,
           datatype:'json',
           data: {'page': pageCom},
           success: function(x){
               $('.loadMoreCom').before(x);
               if($('.emptyCom').length){
                   $('.loadMoreCom').hide();
               }
           }
        });
    });
});
/* global $ */
/* global gotoCom */
/* global flask_moment_render_all */

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
               $('.loadMoreCom').before(x['ajax_request']);
               if(x['last'] == true){
                   $('.loadMoreCom').hide();
               }
               flask_moment_render_all();
           }
        });
    });
});
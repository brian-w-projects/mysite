/* global $ */
/* global goto */
/* global flask_moment_render_all*/

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
               $('.loadMore').before(x['ajax_request']);
               if(x['last'] == true){
                   $('.loadMore').hide();
               }
              flask_moment_render_all();
           }
        });
    });
});
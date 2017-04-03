/* global $ */
/* global goto */
/* global flask_moment_render_all*/
/* global $to_modify*/
/* global goto_insert_com */
/* global $insert_location */
/* global $to_modify_comments */

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
              load_rec_attributes();
           }
        });
    });
    
    load_rec_attributes();
});


function load_rec_attributes(){
    $('.toggle_comments').each(function(){
        $(this).one('click', function(){
            $insert_location = $(this).parent().parent();
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: goto_insert_com,
                datatype:'json',
                data: {'id': $(this).attr('id')},
                success: function(x){
                    $insert_location.after(x['ajax_request']);
                    flask_moment_render_all();
                }
            });
        });
    });
    
     $('.toggle_show').each(function(){
        $(this).on('click', function(){
            $to_modify = $(this).parent().next();
            $to_modify_comments = $(this).parent().parent().next('.w940-center');
            if($to_modify.css('display') == 'none'){
                $to_modify.slideDown();
                $to_modify_comments.slideDown();
            }else{
                $to_modify.slideUp();
                $to_modify_comments.slideUp();
            }
        });
    });
}
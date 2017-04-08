/* global goto_rec */
/* global flask_moment_render_all*/
/* global goto_insert_com */
/* global load_rec_attributes */

(function($, window, document){
    
    var page = 1;
    
    var $ajax_recs = $('#ajax_recs');
    var $load_more_recs = $('.loadMore');
    
    $(function(){
        $ajax_recs.on('click', function(){
            page += 1;
            rec_ajax({'page':page}).done(function(data){
                $load_more_recs.before(data['ajax_request']);
                if(data['last'] == true){
                    $load_more_recs.remove();
                }
                flask_moment_render_all();
            });
        });

        window.load_rec_attributes = function(){
            $(document.body).on('click', '.toggle_comments', function(event){
                var $insert_point = $(this).parent().parent();
                var $to_modify_comments = $(this).parent().parent().next('.w940_center');
                if(!$to_modify_comments.length){
                    rec_comment_ajax({'id': $(this).attr('id')}).done(function(data){
                        $insert_point.after(data['ajax_request']);
                        flask_moment_render_all();
                    });
                }
            });
            
            $(document.body).on('click', '.toggle_show', function(){
                var $to_modify = $(this).parent().next();
                var $to_modify_comments = $(this).parent().parent().next('.w940_center');
                if($to_modify.css('display') == 'none'){
                    $to_modify.slideDown();
                    $to_modify_comments.slideDown();
                }else{
                    $to_modify.slideUp();
                    $to_modify_comments.slideUp();
                }
            });
        };
        
        load_rec_attributes();
    });

    
    
    function rec_ajax(page_info){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_rec,
            datatype:'json',
            data: page_info
        });
    }
    
    function rec_comment_ajax(id_info){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_insert_com,
            datatype:'json',
            data: id_info
        });
    }
}(window.jQuery, window, document));
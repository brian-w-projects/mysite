/* global goto_rec */
/* global flask_moment_render_all*/
/* global goto_insert_com */
/* global goto_follow */
/* global load_rec_attributes */

(function($, window, document){

    var page = 1;
    
    var $ajax_recs = $('#ajax-recs');
    var $load_more_recs = $('.load-more');
    
    var $content = $('#content');
    var $follower_count = $('.follower-count');
    
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

        $content.on('click', '.follow-button', function(){
            var $to_mod = $(this);
            var $id = $(this).attr('id');
            follow_ajax({'id': $id}).done(function(data){
                follow_change(data['added'], $id);
                if($follower_count.length){
                    if(data['added'] == true){
                        $follower_count.html(parseInt($follower_count.text(), 10)+1);
                    }
                    else{
                        $follower_count.html(parseInt($follower_count.text(), 10)-1);
                    }
                }
            });
        });

        window.load_rec_attributes = function(){
            $(document.body).on('click', '.toggle-comments', function(event){
                var $insert_point = $(this).closest('.single-post');
                var $to_modify_comments = $insert_point.next('.list-comments');
                if(!$to_modify_comments.length){
                    rec_comment_ajax({'id': $(this).attr('id')}).done(function(data){
                        $insert_point.after(data['ajax_request']);
                        flask_moment_render_all();
                    });
                }else if($to_modify_comments.css('display') == 'none'){
                    $to_modify_comments.show();
                }else{
                    $to_modify_comments.hide();
                }
            });
            
            $(document.body).on('click', '.toggle-show', function(){
                var $to_modify = $(this).closest('.post-header').next();
                var $to_modify_comments = $(this).closest('.single-post').next('.list-comments');
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

    function follow_change(add, id){
        $('[id='+id+']').each(function(){
           if(add){
                $(this).replaceWith("<i id='"+id+"' class='follow-button font-link fa fa-heart fa-2x'></i>");
           }else{
                $(this).replaceWith("<i id='"+id+"' class='follow-button font-link fa fa-heart-o fa-2x'></i>");
           }
        });
    }

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
    
    function follow_ajax(id_info){
        return  $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_follow,
            datatype:'json',
            data: id_info
        });
    }
}(window.jQuery, window, document));
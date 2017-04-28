/* global goto_comment */
/* global goto_follow */
/* global flask_moment_render_all */
/* global page_com */

(function($, window, document){
   
    page_com = 1;
    
    var $content = $('#content');
    var $load_more_comments = $('.load-more-com');

    $(function(){
        $load_more_comments.on('click', function(){
            page_com += 1;
            comment_ajax({'page':page_com}).done(function(data){
                $load_more_comments.before(data['ajax_request']);
                if(data['last'] == true){
                    $load_more_comments.remove();
                }
                flask_moment_render_all();
            });
        });
        
        $content.on('click', '.follow-button-comment', function(){
            var $id = $(this).attr('id');
            follow_ajax({'id': $id}).done(function(data){
                follow_change(data['added'], $id);
            });
        });
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
    
    function comment_ajax(page_info){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_comment,
            datatype:'json',
            data: page_info
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
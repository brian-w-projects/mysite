/* global goto_comment */
/* global flask_moment_render_all */

(function($, window, document){
   
    var page_com = 1;
    
    var $ajax_comments = $('#ajax-comments');
    var $load_more_comments = $('.load-more-com');

    $(function(){
        $ajax_comments.on('click', function(){
            page_com += 1;
            comment_ajax({'page':page_com}).done(function(data){
                $load_more_comments.before(data['ajax_request']);
                if(data['last'] == true){
                    $load_more_comments.remove();
                }
                flask_moment_render_all();
            });
        });
    });
    
    function comment_ajax(page_info){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_comment,
            datatype:'json',
            data: page_info
        });
    }
}(window.jQuery, window, document));
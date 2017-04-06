/* global gotoCom */
/* global flask_moment_render_all */

(function($, window, document){
   
    var pageCom = 1;
    
    var $ajax_comments = $('#ajax_comments');
    var $load_more_comments = $('.loadMoreCom');

    $(function(){
        $ajax_comments.on('click', function(){
            pageCom += 1;
            comment_ajax({'page':pageCom}).done(function(data){
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
            url: gotoCom,
            datatype:'json',
            data: page_info
        });
    }
}(window.jQuery, window, document));
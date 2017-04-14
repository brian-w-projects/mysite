/* global goto_change_comment_mod */
/* global goto_change_mod */

(function($, window, document){
    
    var $recs = $('.list-recs');
    var $comments = $('.list-comments');
    
    $(function(){
        $recs.on('click', '.change-decision', function(){
            var $to_mod = $(this);
            var $id = $(this).attr('id');
            var $mod_text = $(this).next();
            change_moderate_ajax({'id': $id}).done(function(data){
                if($.trim($mod_text.html()) == 'Accepted'){
                    $mod_text.text('Made Private');
                }else{
                    $mod_text.text('Accepted');
                }
                $to_mod.replaceWith("<i id='"+$id+"'class='font-link fa fa-smile-o fa-2x'></i>");
            });
        });
        
        $comments.on('click', '.change-decision', function(){
            var $to_mod = $(this);
            var $id = $(this).attr('id');
            var $mod_text = $(this).next();
            change_moderate_comment_ajax({'id': $id}).done(function(data){
                if($.trim($mod_text.html()) == 'Accepted'){
                    $mod_text.text('Deleted');
                }else{
                    $mod_text.text('Accepted');
                }
                $to_mod.replaceWith("<i id='"+$id+"'class='font-link fa fa-smile-o fa-2x'></i>");
            });
        });
    });
    
    function change_moderate_comment_ajax(moderate_info){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_change_comment_mod,
            datatype:'json',
            data: moderate_info
        });
    }
    
    function change_moderate_ajax(moderate_info){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_change_mod,
            datatype:'json',
            data: moderate_info
        });
    }
}(window.jQuery, window, document));
/* global gotoE */

(function($, window, document){
    
    var $list_comments = $('.listcomments');
    var $list_recs = $('.listrecs');
    
    var $load_more_comments = $('.loadMoreCom');
    var $load_more_recs = $('.loadMore');
    
    var $submit_button = $('#submit');
    var $follow_button = $('.follow_button');
    
    $(function(){
        $load_more_comments.hide();
        $list_comments.hide();
        
        $follow_button.on('click', function(){
            if($(this).text().trim() == 'Edit'){
                window.location.href = gotoE;
            }
        });
        
        $submit_button.on('click', function(){
            if($(this).text() == 'Comments'){
                $(this).text('Recs');
                $list_recs.hide();
                if($load_more_recs.length){
                    $load_more_recs.hide();
                }
                $list_comments.show();
                if($load_more_comments.length){
                    $load_more_comments.show();
                }
            }
            else{
                $(this).text('Comments');
                $list_comments.hide();
                if($load_more_comments.length){
                    $load_more_comments.hide();
                }
                $list_recs.show();
                if($load_more.length){
                    $load_more.show();
                }
            }
        });
    });
        
}(window.jQuery, window, document));
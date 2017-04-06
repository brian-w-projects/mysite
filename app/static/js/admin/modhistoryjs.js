(function($, window, document){

    var $list_comments = $('.listcomments');   
    var $list_recs = $('.listrecs');
   
    var $load_more_comments = $('.loadMoreCom');
    var $load_more_recs = $('.loadMore');

    $(function(){
        $load_more_comments.hide();
        $list_comments.hide();
    
        $('#submit').on('click', function(){
            if($(this).text() == 'Comments'){
                $(this).text('Recs');
                $list_recs.hide();
                $load_more_recs.hide();
                $list_comments.show();
            }
            else{
                $(this).text('Comments');
                $list_comments.hide();
                $load_more_comments.hide();
                $list_recs.show();
            }
        });
    });
    
}(window.jQuery, window, document));

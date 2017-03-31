/* global $ */

$(function(){
    $('.loadMoreCom').hide();
    $('.listcomments').hide();
    
    $('#submit').on('click', function(){
        if($(this).text() == 'Comments'){
            $(this).text('Recs');
            $('.listrecs').hide();
            $('.loadMore').hide();
            $('.listcomments').show();
            if(!$('.emptyCom').length){
                $('.loadMoreCom').show();
            }
            
        }
        else{
            $(this).text('Comments');
            $('.listcomments').hide();
            $('.loadMoreCom').hide();
            $('.listrecs').show();
            if(!$('.empty').length){
                $('.loadMore').show();
            }
        }
    });
});
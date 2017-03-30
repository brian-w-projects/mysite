/* global $ */
/* global gotoP */
/* global gotoC */
/* global gotoF */
/* global gotoE */
/* global id */
/* global page */
/* global pageCom */

$(function(){
    $('.loadMoreCom').hide();
    $('.listcomments').hide();
    
    $('.follow_button').on('click', function(){
        if($(this).text().trim() == 'Edit'){
            window.location.href = gotoE;
        }
    });
    
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
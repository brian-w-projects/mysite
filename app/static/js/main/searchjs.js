/* global $ */
/* global goto_initial */
/* global page */
/* global pageCom */

$(function(){
    $('.loadMore').hide();
    $('.loadMoreCom').hide();
    
    $('#submit').on('click', function(event){
        page = 1;
        pageCom = 1;
        event.preventDefault();
        $.ajax({
           type: 'POST',
           url: goto_initial,
           data: $('form').serialize(),
           success: function(x){
                $('.loadMore').prevAll().remove();
                $('.loadMoreCom').prevAll().remove();
                $('.loadMore').hide();
                $('.loadMoreCom').hide();
                if($('.type').val() == 'Recs'){
                    $('.loadMore').before(x);
                    if(!$('.empty').length){
                        $('.loadMore').show();
                    }
                }else{
                    $('.loadMoreCom').before(x);
                    if(!$('.emptyCom').length){
                        $('.loadMoreCom').show();
                    }
                }
                
             
           }
        });
    });
    
    $( "#datepicker" ).datepicker();
});

/* global $ */
/* global gotoP */
/* global gotoC */
/* global id */

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
    
    $('.ajax').bind('click', function(){
        if($('#submit').text() == 'Comments'){
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: gotoP,
                datatype:'json',
                data: {'id': id},
                success: function(x){
                    $('.listrecs').append(x);
                   if($('.empty').length){
                        $('.loadMore').hide();
                    }
                }
            });
        }
        else
        {
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: gotoC,
                datatype:'json',
                data: {'id': id},
                success: function(x){
                    $('.listcomments').append(x);
                   if($('.emptyCom').length){
                        $('.loadMoreCom').hide();
                    }
                }
            });
        }
    });
});
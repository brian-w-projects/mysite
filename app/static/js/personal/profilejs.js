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
    
    $('#follow').on('click', function(){
        if($(this).text().trim() == 'Edit'){
            window.location.href = gotoE;
        }
        else{
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: gotoF,
                datatype:'json',
                data: {'id': id, 'follow': $(this).text().trim() == 'Follow'},
                success: function(x){
                    var y = $.parseJSON(x);
                    if(y['added'] == true)
                    {
                        $('#follow').text('Following');
                        $('.f_count').html(parseInt($('.f_count').text())+1);
                    }
                    else
                    {
                        $('#follow').text('Follow');
                        $('.f_count').html(parseInt($('.f_count').text())-1);
                    }
                }
            });
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
    
    $('.ajax').bind('click', function(){
        if($('#submit').text() == 'Comments'){
            page += 1;
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: gotoP,
                datatype:'json',
                data: {'id': id, 'page':page},
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
            pageCom += 1;
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: gotoC,
                datatype:'json',
                data: {'id': id, 'page': pageCom},
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
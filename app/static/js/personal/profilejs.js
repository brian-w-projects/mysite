/* global $ */
/* global gotoP */
/* global gotoC */
/* global gotoF */
/* global limitVar */
/* global offsetVar */
/* global limitCom */
/* global offsetCom */
/* global id */

$(function(){
    
    $('#follow').on('click', function(){
        $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: gotoF,
                datatype:'json',
                data: {'id': id, 'follow':$('#follow').text()},
                success: function(x){
                    var y = $.parseJSON(x);
                    if(y['added'] == true)
                    {
                        $('#follow').text('Following');
                        var original = parseInt($('.f_count').text())+1;
                        $('.f_count').html(original);
                    }
                    else
                    {
                        $('#follow').text('Follow');
                        var original = parseInt($('.f_count').text())-1;
                        $('.f_count').html(original);
                    }
                    
                }
            });
    });
    
    $('#submit').on('click', function(){
        if($(this).text() == 'Comments')
        {
            $(this).text('Recs');
            $('.listrecs').addClass('hide');
            $('.loadMore').addClass('hide');
            $('.listcomments').removeClass('hide');
            $('.loadMoreCom').removeClass('hide');
            
        }
        else
        {
            $(this).text('Comments');
            $('.listcomments').addClass('hide');
            $('.loadMoreCom').addClass('hide');
            $('.listrecs').removeClass('hide');
            $('.loadMore').removeClass('hide');
        }
        
    });
    
    $('.ajax').bind('click', function(){
        if($('#submit').text() == 'Comments')
        {
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: gotoP,
                datatype:'json',
                data: {'limit':limitVar, 'offset': offsetVar, 'id': id},
                success: function(x){
                    $('.listrecs').append(x);
                    offsetVar += limitVar;
                   if($('.empty').length){
                        $('.loadMore').css('display', 'none');
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
                data: {'limit':limitCom, 'offset': offsetCom, 'id': id},
                success: function(x){
                    $('.listcomments').append(x);
                    offsetCom += limitCom;
                   if($('.emptyCom').length){
                        $('.loadMoreCom').css('display', 'none');
                    }
                }
            });
        }
    });
});
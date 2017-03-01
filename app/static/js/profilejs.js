/* global $ */
/* global gotoP */
/* global gotoC */
/* global limitVar */
/* global offsetVar */
/* global limitCom */
/* global offsetCom */
/* global id */

$(function(){
    $('#submit').on('click', function(){
        if($(this).text() == 'Comments')
        {
            $(this).text('Recs');
            $('.listrecs').addClass('hide');
            $('.listcomments').removeClass('hide');
        }
        else
        {
            $(this).text('Comments');
            $('.listcomments').addClass('hide');
            $('.listrecs').removeClass('hide');
        }
        
    });
    
    $('#ajax').bind('click', function(){
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
                        $('.loadMore').css('display', 'none');
                    }
                }
            });
        }
    });
});
/* global $ */
/* global $SCRIPT_ROOT */
/* global limitVar */
/* global offsetVar */
/* global goto */
/* global gotoF */
/* global idVar */
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
                }
                else
                {
                    $('#follow').text('Follow');
                }
                
            }
        });
    });
    
    $('#ajax').bind('click', function(){
        $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto,
            datatype:'json',
            data: {'limit':limitVar, 'offset': offsetVar, 'id':idVar},
            success: function(x){
                $('.listcomments').append(x);
                offsetVar += limitVar;
               if($('.emptyCom').length){
                        $('.loadMore').css('display', 'none');
                }
            }
        });
    });
});
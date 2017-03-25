/* global $ */
/* global goto */
/* global gotoF */
/* global id */
/* global page */
/* global rec_id */

$(function(){
    $('#follow').on('click', function(){
        $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: gotoF,
            datatype:'json',
            data: {'id': id, 'follow':$('#follow').text().trim()=='Follow'},
            success: function(x){
                var y = $.parseJSON(x);
                if(y['added'] == true){
                    $('#follow').text('Following');
                }
                else{
                    $('#follow').text('Follow');
                }
            }
        });
    });
    
    $('#ajax').bind('click', function(){
        page += 1;
        $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto,
            datatype:'json',
            data: {'id': rec_id, 'page': page},
            success: function(x){
                $('.listcomments').append(x);
               if($('.emptyCom').length){
                        $('.loadMore').css('display', 'none');
                }
            }
        });
    });
    
    var $count = 250 - $('.textentry').val().length;
    $('.chars-left').text($count);
    
    $('.textentry').on('input', function(){
        var $count = 250 - $('.textentry').val().length;
        if($count >= 0){
            $('.chars-left').text($count);
        }
        else{
            var new_val = $('.textentry').val().toString().substr(0,250);
            $('.textentry').val(new_val);
            $('.chars-left').text(0);
        }
    });
});
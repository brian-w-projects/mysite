/* global $ */
/* global goto */

$(function(){
    $('#ajax').bind('click', function(){
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: goto,
           datatype:'json',
           success: function(x){
               $('.listrecs').append(x);
               if($('.empty').length){
                   $('.loadMore').css('display', 'none');
               }
           }
        });
    });
    
    var $count = 1000 - $('.textentry').val().length;
    $('.chars-left').text($count);
    
    $('.textentry').on('input', function(){
        var $count = 1000 - $('.textentry').val().length;
        if($count >= 0){
            $('.chars-left').text($count);
        }
        else{
            var new_val = $('.textentry').val().toString().substr(0,1000);
            $('.textentry').val(new_val);
            $('.chars-left').text(0);
        }
    });
    
    var $count = 100 - $('.titleentry').val().length;
    $('.chars-left-title').text($count);
    
    $('.titleentry').on('input', function(){
        var $count = 100 - $('.titleentry').val().length;
        if($count >= 0){
            $('.chars-left-title').text($count);
        }
        else{
            var new_val = $('.titleentry').val().toString().substr(0,100);
            $('.titleentry').val(new_val);
            $('.chars-left-title').text(0);
        }
    });
});


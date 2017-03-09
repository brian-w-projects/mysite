/* global $ */
/* global goto */
/* global gotoM */

$(function(){
    $('#submit').bind('click', function(event){
        event.preventDefault();
        $.ajax({
           type: 'POST',
           url: goto,
           data: $('form').serialize(),
           success: function(x){
                $('.listrecs').html(x);
               if($('.empty').length){
                   $('.loadMore').css('display', 'none');
               }
               else{
                    $('.loadMore').css('display', 'block');
               }
               
           }
        });
    });
    
    $('#ajax').bind('click', function(){
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: gotoM,
           datatype:'json',
           data: {},
           success: function(x){
               $('.listrecs').append(x);
               if($('.empty').length || $('.emptyCom').length){
                   $('.loadMore').css('display', 'none');
               }
           }
        });
    });
    
    $( "#datepicker" ).datepicker();
});

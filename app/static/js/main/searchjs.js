/* global $ */
/* global goto */
/* global gotoM */
/* global page */

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
        page += 1;
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: gotoM,
           datatype:'json',
           data: {'page': page},
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

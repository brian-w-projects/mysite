/* global $ */
/* global $SCRIPT_ROOT */
/* global limitVar */
/* global goto */
/* global gotoM */
/* global offsetVar */

$(function(){
    $('#submit').bind('click', function(event){
        event.preventDefault();
        $.ajax({
           type: 'POST',
           url: goto,
           data: $('form').serialize(),
           success: function(x){
                $('.listrecs').html(x);
                offsetVar = limitVar;
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
           data: {'limit':limitVar, 'offset':offsetVar},
           success: function(x){
               $('.listrecs').append(x);
               offsetVar += limitVar;
               if($('.empty').length || $('.emptyCom').length){
                   $('.loadMore').css('display', 'none');
               }
           }
        });
    });
    
    $( "#datepicker" ).datepicker();
});

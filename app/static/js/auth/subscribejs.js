/* global $ */
/* global goto */
/* global gotoE */

$(function(){
    $('.username').bind('blur', function(){
        var username_check = $(this).val();
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: goto,
           datatype:'json',
           data: {'username':username_check},
           success: function(x){
               console.log(x);
               var y = $.parseJSON(x);
               if(y['exists'] == true){
                   $('.nameexists').text('This name is in use.');
               }
               else{
                   $('.nameexists').text('This name is available.');
               }
               
           }
        });
    });
    
    $('.email').bind('blur', function(){
        var email_check = $(this).val();
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: gotoE,
           datatype:'json',
           data: {'email':email_check},
           success: function(x){
               console.log(x);
               var y = $.parseJSON(x);
               if(y['exists'] == true){
                   $('.emailexists').text('This email is in use.');
               }
               else{
                   $('.emailexists').text('This email is available.');
               }
               
           }
        });
    });
});


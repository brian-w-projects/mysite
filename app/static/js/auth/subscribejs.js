/* global $ */
/* global goto */
/* global gotoE */

$(function(){
    $('.username').on('keyup', function(){
       var username_check = $(this).val();
       if(username_check.length > 0 && username_check.length < 5){
           $('.nameexists').text('Must be between 5 and 12 characters');
       }else{
           $('.nameexists').text('');
           animate_good($('.username'));
       }
    });
    
    $('.username').on('blur', function(){
        var username_check = $(this).val();
        if(username_check.length >= 5 && username_check.length <= 12){
            $.ajax({
               type: 'GET',
               contentType: 'application/json;charset=UTF-8',
               url: goto,
               datatype:'json',
               data: {'username':username_check},
               success: function(x){
                   if(x['exists'] == true){
                       $('.nameexists').text('This name is in use.');
                       animate_bad($('.username'));
                   }
                   else{
                       $('.nameexists').text('This name is available.');
                       animate_good($('.username'));
                   }
                   
               }
            });
        }else{
            animate_bad($('.username'));
        }
    });

    $('.email').on('keyup', function(){
       var email_check = $(this).val();
       if(email_check.length == 0){
           animate_good($('.email'));
       }
    });
    
    $('.email').on('blur', function(){
        var email_check = $(this).val();
        var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,6})?$/;
        if(email_check.length == 0 || !emailReg.test(email_check)){
            $('.emailexists').text('Enter a valid e-mail address');
            animate_bad($('.email'));
        }else{
            $.ajax({
               type: 'GET',
               contentType: 'application/json;charset=UTF-8',
               url: gotoE,
               datatype:'json',
               data: {'email':email_check},
               success: function(x){
                   if(x['exists'] == true){
                       $('.emailexists').text('This email is in use.');
                       animate_bad($('.email'));
                   }
                   else{
                       $('.emailexists').text('This email is available.');
                       animate_good($('.email'));
                   }
               }
            });
        }
    });
    
    $('#password').on('keyup', function(){
        var password_check = $(this).val();
        if(password_check.length >= 8){
            $('.passwordexists').text('');
            animate_good($('#password'));
        }else if(password_check.length == 0){
            $('.passwordexists').text('');
            animate_good($('#password'));
        }
    });
    
    $('#password').on('blur', function(){
        var password_check = $(this).val();
        if(password_check.length < 8){
            $('.passwordexists').text('Password must be 8 character long or more');
            animate_bad($('#password'));
        }
    });
    
    $('#password_confirm').on('focus', function(){
       animate_good($('#password_confirm')); 
       $('.passwordconfirmexists').text('');
    });
    
    $('#password_confirm').on('blur', function(){
       var password_check = $('#password').val();
       var password_confirm_check = $('#password_confirm').val();
       if(password_check != password_confirm_check){
           animate_bad($('#password_confirm'));
           $('.passwordconfirmexists').text('Passwords must match');
       }
    });
});

function animate_bad($which){
    $which.animate({
        backgroundColor: '#ff0000'}, 'fast');
}

function animate_good($which){
    $which.animate({
        backgroundColor: '#efefef'}, 'fast');
}
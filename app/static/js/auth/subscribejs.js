/* global goto_username_check */
/* global goto_email_check */

(function($, window, document){

    var $username = $('.username');
    var $email = $('.email');
    var $password = $('#password');
    var $password_confirm = $('#password_confirm');
    
    var $username_exists = $('.name_valid');
    var $email_exists = $('.email_valid');
    var $password_exists = $('.password_valid');
    var $password_confirm_exists = $('.password_confirm_valid');

    $(function(){
        $username.on('keyup', function(){
            var username_check = $(this).val();
            if(username_check.length > 0 && username_check.length < 5){
                $username_exists.text('Must be between 5 and 12 characters');
            }else{
                $username_exists.text('');
                animate_good($username);
            }
        });
    
        $username.on('blur', function(){
            var username_check = $(this).val();
            if(username_check.length >= 5 && username_check.length <= 12){
                username_ajax(username_check).done(function(data){
                    if(data['exists'] == true){
                        $username_exists.text('This name is in use.');
                        animate_bad($username);
                    }else{
                        $username_exists.text('This name is available.');
                        animate_good($username);
                    }
                });
            }else{
                animate_bad($username);
            }
        });
            
        $email.on('keyup', function(){
            var email_check = $(this).val();
            if(email_check.length == 0){
                animate_good($email);
            }
        });
        
        $email.on('blur', function(){
            var email_check = $(this).val();
            var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,6})?$/;
            if(email_check.length == 0 || !emailReg.test(email_check)){
                $email_exists.text('Enter a valid e-mail address');
                animate_bad($email);
            }else{
                email_ajax(email_check).done(function(data){
                    if(data['exists'] == true){
                        $email_exists.text('This email is in use.');
                        animate_bad($email);
                    }
                    else{
                        $email_exists.text('This email is available.');
                        animate_good($email);
                    }
                });
            }
        });
        
        $password.on('keyup', function(){
            var password_check = $(this).val();
            if(password_check.length >= 8){
                $password_exists.text('Password is acceptable length');
                animate_good($password);
            }else if(password_check.length == 0){
                $password_exists.text('');
                animate_good($password);
            }
        });
        
        $password.on('blur', function(){
            var password_check = $(this).val();
            if(password_check.length < 8){
                $password_exists.text('Password must be 8 character long or more');
                animate_bad($password);
            }
        });
        
        $password_confirm.on('focus', function(){
           animate_good($password_confirm); 
           $password_confirm_exists.text('');
        });
        
        $password_confirm.on('blur', function(){
           if($password.val() != $password_confirm.val()){
               animate_bad($password_confirm);
               $password_confirm_exists.text('Passwords must match');
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
    
    function username_ajax(username_check){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_username_check,
            datatype:'json',
            data: {'username':username_check}
        });
    }
    
    function email_ajax(email_check){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_email_check,
            datatype:'json',
            data: {'email':email_check},
        });
    }

}(window.jQuery, window, document));
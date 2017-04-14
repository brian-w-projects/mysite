(function($, window, document){

    var $font_icons = $('#username, #email, #password, #password_confirm, #token,\
        #type, #tags, #user, #datepicker');

    $(function(){
        $font_icons.on('mouseover focus', function(){
           $(this).prev().css('borderBottomWidth', '2px');
        });
        
        $font_icons.on('mouseout blur', function(){
            if(!$(this).is(':focus')){
                $(this).prev().css('borderBottomWidth', '1px');
            }
        });
    });

}(window.jQuery, window, document));
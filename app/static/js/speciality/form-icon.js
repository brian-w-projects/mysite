(function($, window, document){

    var $font_icons = $('#username, #email, #password, #password_confirm, #token,\
        #type, #tags, #user, #datepicker, #limit');

    $(function(){
        $font_icons.on('focus blur', function(){
           $(this).parent().toggleClass('hovered');
        });
    });

}(window.jQuery, window, document));
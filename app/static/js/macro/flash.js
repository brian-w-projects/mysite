(function($, window, document){
    
    var $flash_close = $('.flash-close');
    
    $(function(){
        
        $flash_close.on('click', function(){
            console.log('here');
            $(this).parent().parent().hide();
        });
    });

}(window.jQuery, window, document));
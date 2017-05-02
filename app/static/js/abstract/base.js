/* global NProgress */

(function($, window, document){

    var $content = $('a, #submit');

    NProgress.configure({ showSpinner: false });
    NProgress.set(0.6);

    $(function(){
        NProgress.done();
        
        $content.on('click', function(){
           NProgress.start(); 
        });
        
        $(window).bind('beforeunload', function(){
           NProgress.start(); 
        });
        
    });

}(window.jQuery, window, document));

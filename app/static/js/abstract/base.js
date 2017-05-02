/* global NProgress */

(function($, window, document){

    var $content = $('a');

    $(function(){
        NProgress.done();
        
        $content.on('click', function(){
           NProgress.start(); 
        });
        
    });

}(window.jQuery, window, document));

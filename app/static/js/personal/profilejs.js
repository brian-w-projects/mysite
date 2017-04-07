/* global gotoE */

(function($, window, document){

    var $edit_button = $('.edit_button');

    $(function(){
        if($edit_button.length){
            $edit_button.on('click', function(){
                window.location.href = gotoE;
            });
        }
    });
        
}(window.jQuery, window, document));
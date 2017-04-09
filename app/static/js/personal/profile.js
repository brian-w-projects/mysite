/* global goto_edit */

(function($, window, document){

    var $edit_button = $('.edit-button');

    $(function(){
        if($edit_button.length){
            $edit_button.on('click', function(){
                window.location.href = goto_edit;
            });
        }
    });
        
}(window.jQuery, window, document));
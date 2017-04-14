/* global goto_mod */

(function($, window, document){
    
    var $content = $('#content');
    
    $(function(){
        $content.on('click', '.mod-button', function(){
            var $to_mod = $(this);
            var $id = $(this).attr('id');
            var $action = $(this).hasClass('verify');
            moderate_ajax({'id': $id, 'verify':$action}).done(function(data){
                $to_mod.parent().slideUp();
            });
        });
    });
    
    function moderate_ajax(moderate_info){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_mod,
            datatype:'json',
            data: moderate_info
        });
    }
}(window.jQuery, window, document));
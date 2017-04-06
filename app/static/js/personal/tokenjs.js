/* global api */
/* global goto */

(function($, window, docuement){
  
    var $api_entry = $('.api_entry');
    var $copy = $('.copy');
    var $reload = $('.reload');
   
   $(function(){
    
        $api_entry.val(api);
    
        
        $api_entry.on('click', function(event){
            event.preventDefault();
            $(this).blur();
        });
        
        $copy.on('click', function(){
            $api_entry.select();
            document.execCommand('copy');
            $api_entry.blur();
        });
        
        $reload.on('click', function(){
            token_ajax().done(function(data){
                $api_entry.val(data);
            });
                    
               
        });
    }); 
    
    function token_ajax(){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto,
        });
    }
}(window.jQuery, window, document));
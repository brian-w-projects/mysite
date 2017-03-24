/* global $ */
/* global api */
/* global goto */

$(function(){
    
    $('.api_entry').val(api);
    
    // $('.api_entry').on('input', function(){
    //     $(this).val(api);
    // });
    
    $('.api_entry').on('click', function(event){
        event.preventDefault();
        $(this).blur();
    });
    
    $('.copy').on('click', function(){
        $('.api_entry').select();
        document.execCommand('copy');
        $('.api_entry').blur();
    });
    
    $('.reload').on('click', function(){
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: goto,
           success: function(x){
                $('.api_entry').val(x);   
           }
        });
    });
});
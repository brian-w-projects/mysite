/* global $ */
/* global api */
/* global goto */

$(function(){
    
    $('.entry').val(api);
    
    $('.entry').on('input', function(){
        $(this).val(api);
    });
    
    $('.copy').on('click', function(){
        $('.entry').select();
        document.execCommand('copy');
    });
    
    $('.reload').on('click', function(){
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: goto,
           success: function(x){
                $('.entry').val(x);   
           }
        });
    });
});
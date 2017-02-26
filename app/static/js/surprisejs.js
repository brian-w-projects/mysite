/* global $ */
/* global $SCRIPT_ROOT */
/* global limitVar */

$(function(){
    $('#ajax').bind('click', function(){
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: $SCRIPT_ROOT + '/_surprise',
           datatype:'json',
           data: {'limit':limitVar},
           success: function(x){
               $('.listrecs').append(x);
           }
        });
    });
});


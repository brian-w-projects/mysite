/* global $ */
/* global $SCRIPT_ROOT */
/* global limitVar */
/* global goto */

$(function(){
    $('#ajax').bind('click', function(){
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: goto,
           datatype:'json',
           data: {'limit':limitVar},
           success: function(x){
               $('.listrecs').append(x);
           }
        });
    });
});


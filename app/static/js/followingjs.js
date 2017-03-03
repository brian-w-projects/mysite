/* global $ */
/* global $SCRIPT_ROOT */
/* global limitVar */
/* global offsetVar */
/* global goto */

$(function(){
    $('#ajax').bind('click', function(){
        $.ajax({
           type: 'GET',
           contentType: 'application/json;charset=UTF-8',
           url: goto,
           datatype:'json',
           data: {'limit':limitVar, 'offset': offsetVar},
           success: function(x){
               $('.listrecs').append(x);
               offsetVar += limitVar;
               if($('.empty').length){
                   $('.loadMore').css('display', 'none');
               }
           }
        });
    });
});


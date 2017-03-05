/* global $ */
/* global goto */

$(function(){
    $('.to_check').each(function(){
        var $to_mod = $(this);
        var $id = $(this).attr('id');
        $to_mod.on('click', function(){
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: goto,
                datatype:'json',
                data: {'id': $id, 'follow':false},
                success: function(x){
                    $to_mod.parent().hide();
                    $to_mod.parent().next().hide();
                }
            });
        }); 
    });
});
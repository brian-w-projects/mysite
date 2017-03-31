/* global $ */
/* global goto_mod */

$(function(){
    $('.listrecs, .listcomments').on('click', '.mod_button', function(){
        var $to_mod = $(this);
        var $id = $(this).attr('id');
        var $action = $(this).hasClass('verify');
        $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_mod,
            datatype:'json',
            data: {'id': $id, 'verify':$action},
            success: function(x){
                $to_mod.parent().hide();
                $to_mod.parent().next().hide();
                $to_mod.parent().next().next().hide();
            }
        });
    });
});
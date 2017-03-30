/* global $ */
/* global goto_follow */

$(function(){
    $(':button').each(function(){
        var $to_mod = $(this);
        var $id = $(this).attr('id');
        $to_mod.on('click', function(){
            $.ajax({
                type: 'GET',
                contentType: 'application/json;charset=UTF-8',
                url: goto_follow,
                datatype:'json',
                data: {'id': $id},
                success: function(x){
                    if(x['added'] == true){
                        $to_mod.html('Unfollow');
                        $('.f_count').html(parseInt($('.f_count').text())+1);
                        
                    }else{
                        $to_mod.html('Follow');
                        $('.f_count').html(parseInt($('.f_count').text())-1);
                    }
                }
            });
        }); 
    });
});
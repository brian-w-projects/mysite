/* global $ */
/* global goto_follow */

(function($, window, docuement){
   
   var $follow_button = $('.follow_button');
   var $follower_count = $('.f_count');
   
   
   $(function(){
        $follow_button.each(function(){
            var $to_mod = $(this);
            var $id = $(this).attr('id');
            $to_mod.on('click', function(){
                follow_ajax({'id': $id}).done(function(data){
                    if(data['added'] == true){
                        $to_mod.html('Unfollow');
                        if($follower_count.length){
                            $follower_count.html(parseInt($follower_count.text(), 10)+1);
                        }
                    }else{
                        $to_mod.html('Follow');
                        if($follower_count.length){
                            $follower_count.html(parseInt($follower_count.text(), 10)-1);
                        }
                    }
                });
            }); 
        });
    });
    
    function follow_ajax(id_info){
        return  $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_follow,
            datatype:'json',
            data: id_info
        });
    }
}(window.jQuery, window, document));
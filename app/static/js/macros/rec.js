/* global goto_follow */
/* global goto_insert_com */
/* global goto_rec */
/* global flask_moment_render_all*/
/* global load_rec_attributes */
/* global page */
/* global NProgress */
/* global id */

(function($, window, document){

    page = 1; //global
    
    var $content = $('#content');
    var $follower_count = $('.follower-count');
    var $load_more_recs = $('.load-more');
    
    $(function(){
        
        comment_injection(id);
        
        $load_more_recs.on('click', function(){
            page += 1;
            rec_ajax({'page':page}).always(function(){
                NProgress.done();
                $load_more_recs.prev().hide();
            }).done(function(data){
                $load_more_recs.prev().before(data['ajax_request']);
                if(data['last'] == true){
                    $load_more_recs.remove();
                }
                comment_injection(data['id']);
                flask_moment_render_all();
            }).fail(function(){
                page -= 1;
            });
        });

        $content.on('click', '.follow-button', function(){
            var $id = $(this).attr('id');
            follow_ajax({'id': $id}).done(function(data){
                follow_change(data['added'], $id);
                if($follower_count.length){
                    if(data['added'] == true){
                        $follower_count.html(parseInt($follower_count.text(), 10)+1);
                    }
                    else{
                        $follower_count.html(parseInt($follower_count.text(), 10)-1);
                    }
                }
            });
        });

        window.load_rec_attributes = function(){
            $content.on('click', '.toggle-comments', function(event){
                var $to_modify_comments = $(this).closest('.single-post').next().next('.inline-comments');
                if($to_modify_comments.css('display') == 'none'){
                    $to_modify_comments.show();
                }else{
                    $to_modify_comments.hide();
                }
            });
            
            $content.on('click', '.toggle-show', function(){
                var $to_modify = $(this).closest('.post-header').next();
                var $to_modify_comments = $(this).closest('.single-post').next().next('.inline-comments');
                if($to_modify.css('display') == 'none'){
                    $to_modify.slideDown();
                    $to_modify_comments.slideDown();
                }else{
                    $to_modify.slideUp();
                    $to_modify_comments.slideUp();
                }
            });
        };
        
        load_rec_attributes();
    });

    function comment_injection(id){
        begin_comment_ajax(id).done(function(data){
            if(data['status'] == 'PROGRESS'){
                setTimeout(function(){
                    comment_injection(id);
                }, 2000);
            }
            else{
                $('.inline-comments').each(function(){
                    var id = parseInt($(this).attr('id'));
                   $(this).html($(data['results'][id]).html());
                });
            }
        });
    }

    function follow_change(add, id){
        $('[id='+id+']').each(function(){
           if(add){
                $(this).replaceWith("<i id='"+id+"' class='follow-button font-link fa fa-heart fa-2x'></i>");
           }else{
                $(this).replaceWith("<i id='"+id+"' class='follow-button font-link fa fa-heart-o fa-2x'></i>");
           }
        });
    }

    function rec_ajax(page_info){
        return $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_rec,
            datatype:'json',
            data: page_info,
            timeout: 10000,
            beforeSend: function(){
                NProgress.start();
                $load_more_recs.prev().show();
            },
        });
    }
    
    function follow_ajax(id_info){
        return  $.ajax({
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            url: goto_follow,
            datatype:'json',
            data: id_info,
            timeout: 5000,
        });
    }
    
    function begin_comment_ajax(id){
        return $.ajax({
           type: 'GET', 
           contentType: 'application/json;charset=UTF-8',
           url: goto_insert_com,
           datatype: 'json',
           data: {'id': id},
        });
    }
}(window.jQuery, window, document));
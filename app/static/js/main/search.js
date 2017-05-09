/* global goto_initial */
/* global flask_moment_render_all*/
/* global page */
/* global page_com */
/* global NProgress */
/* global history */
/* global location */

(function($, window, document){

    var $load_more_comments = $('.load-more-com');
    var $load_more_recs = $('.load-more');
    
    var $submit_button = $('#submit');
    var $form = $('form');
    var $type = $('#type');
    var $date_picker = $("#datepicker");
    var $initial_search = $('.initial-search');
    var $error = $('.error');

    $load_more_recs.hide();
    $load_more_comments.hide();
    $error.hide();
    
    $(function(){
    
        $submit_button.on('click', function(event){
            search_ajax().always(function(){
                history.pushState('', 'Search Results', $(location).attr('href'));
                NProgress.done();
                $initial_search.hide();
            }).done(function(data){
                if($type.val() == 'Recs'){
                    $load_more_recs.prev().before(data['ajax_request']);
                    if(data['ajax_request'].trim() == ''){
                        $error.text('No Results').show();
                    }
                    if(data['last'] == false){
                        $load_more_recs.show();
                    }
                }else{
                    $load_more_comments.prev().before(data['ajax_request']);
                    if(data['ajax_request'].trim() == ''){
                        $error.text('No Results').show();
                    }
                    if(data['last'] == false){
                        $load_more_comments.show();
                    }
                }
                flask_moment_render_all();
                comment_injection(data['id']);
            }).fail(function(){
                $error.text('Could not load content').show();
            });
        });

        window.onpopstate = function(event){
            page = 1;
            page_com = 1;
            NProgress.start();
            $load_more_recs.prev().prevAll().remove();
            $load_more_comments.prev().prevAll().remove();
            $load_more_recs.hide();
            $load_more_comments.hide();
            NProgress.done();
        };

        $date_picker.datepicker();
    });

    function search_ajax(){
        return  $.ajax({
            type: 'POST',
            url: goto_initial,
            data: $form.serialize(),
            timeout: 10000,
            beforeSend: function(){
                page = 1;
                page_com = 1;
                NProgress.start();
                event.preventDefault();
                $error.hide();
                $initial_search.show();
                $load_more_recs.prev().prevAll().remove();
                $load_more_comments.prev().prevAll().remove();
                $load_more_recs.hide();
                $load_more_comments.hide();
            },
        });
    }
    
}(window.jQuery, window, document));

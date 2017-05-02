/* global goto_initial */
/* global flask_moment_render_all*/
/* global page */
/* global page_com */
/* global NProgress */

(function($, window, document){

    var $load_more_comments = $('.load-more-com');
    var $load_more_recs = $('.load-more');
    
    var $submit_button = $('#submit');
    var $form = $('form');
    var $type = $('#type');
    var $date_picker = $("#datepicker");
    var $initial_search = $('.initial-search');
    
    $(function(){
        $load_more_recs.hide();
        $load_more_comments.hide();
    
        $submit_button.on('click', function(event){
            page = 1;
            page_com = 1;
            NProgress.start();
            event.preventDefault();
            $initial_search.show();
            $load_more_recs.prev().prevAll().remove();
            $load_more_comments.prev().prevAll().remove();
            $load_more_recs.hide();
            $load_more_comments.hide();
            search_ajax().done(function(data){
                NProgress.done();
                $initial_search.hide();
                if($type.val() == 'Recs'){
                    $load_more_recs.prev().before(data['ajax_request']);
                    if(data['last'] == false){
                        $load_more_recs.show();
                    }
                }else{
                    $load_more_comments.prev().before(data['ajax_request']);
                    if(data['last'] == false){
                        $load_more_comments.show();
                    }
                }
                flask_moment_render_all();
            });
        });

        $date_picker.datepicker();
    });

    function search_ajax(){
        return  $.ajax({
            type: 'POST',
            url: goto_initial,
            data: $form.serialize(),
        });
    }
    
}(window.jQuery, window, document));

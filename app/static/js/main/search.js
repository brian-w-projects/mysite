/* global goto_initial */
/* global flask_moment_render_all*/

(function($, window, document){
    
    var $load_more_comments = $('.load-more-com');
    var $load_more_recs = $('.load-more');
    
    var $submit_button = $('#submit');
    var $form = $('form');
    var $type = $('.type');
    var $date_picker = $("#datepicker");
    
    $(function(){
        $load_more_recs.hide();
        $load_more_comments.hide();
    
        $submit_button.on('click', function(event){
            page = 1;
            page_com = 1;
            event.preventDefault();
            search_ajax().done(function(data){
                $load_more_recs.prevAll().remove();
                $load_more_comments.prevAll().remove();
                $load_more_recs.hide();
                $load_more_comments.hide();
                if($type.val() == 'Recs'){
                    $load_more_recs.before(data['ajax_request']);
                    if(data['last'] == false){
                        $load_more_recs.show();
                    }
                }else{
                    $load_more_comments.before(data['ajax_request']);
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

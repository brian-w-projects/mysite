/* global $ */
/* global goto_initial */
/* global page */
/* global pageCom */
/* global flask_moment_render_all*/

$(function(){
    $('.loadMore').hide();
    $('.loadMoreCom').hide();
    
    $('#submit').on('click', function(event){
        page = 1;
        pageCom = 1;
        event.preventDefault();
        $.ajax({
           type: 'POST',
           url: goto_initial,
           data: $('form').serialize(),
           success: function(x){
                $('.loadMore').prevAll().remove();
                $('.loadMoreCom').prevAll().remove();
                $('.loadMore').hide();
                $('.loadMoreCom').hide();
                if($('.type').val() == 'Recs'){
                    $('.loadMore').before(x['ajax_request']);
                    load_rec_attributes(); //from ajax_rec_js
                    if(x['last'] == false){
                        $('.loadMore').show();
                    }
                }else{
                    $('.loadMoreCom').before(x['ajax_request']);
                    if(x['last'] == false){
                        $('.loadMoreCom').show();
                    }
                }
                flask_moment_render_all();
                
             
           }
        });
    });
    
    $( "#datepicker" ).datepicker();
});

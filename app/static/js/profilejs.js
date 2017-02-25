/* global $ */

$(function(){
    $('#submit').on('click', function(){
        if($(this).text() == 'Comments')
        {
            $(this).text('Recs');
            $('.listrecs').addClass('hide');
            $('.listcomments').removeClass('hide');
        }
        else
        {
            $(this).text('Comments');
            $('.listcomments').addClass('hide');
            $('.listrecs').removeClass('hide');
        }
        
    });
});
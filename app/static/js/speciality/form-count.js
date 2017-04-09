/* global $ */

(function($, window, docuement){
    
    var $rec_title_entry = $('.rec-title-entry');
    var $rec_title_chars_left = $('.rec-title-chars-left');
    
    var $rec_text_entry = $('.rec-text-entry');
    var $rec_chars_left = $('.rec-chars-left');
    
    var $comment_text_entry = $('.comment-text-entry');
    var $comment_chars_left = $('.comment-chars-left');
    
    var $about_me_text_entry = $('.about-me-text-entry');
    var $about_me_chars_left = $('.about-me-chars-left');
    
    $(function(){
        if($rec_title_entry.length){
            var $rec_title_count = 100 - $rec_title_entry.val().length;
            $rec_title_chars_left.text($rec_title_count);
            
            $rec_title_entry.on('input', function(){
                $rec_title_count = 100 - $rec_title_entry.val().length;
                if($rec_title_count >= 0){
                    $rec_title_chars_left.text($rec_title_count);
                }
                else{
                    var new_val = $rec_title_entry.val().toString().substr(0,100);
                    $rec_title_entry.val(new_val);
                    $rec_title_chars_left.text(0);
                }
            });
        }
    
        if($rec_text_entry.length){
            var $rec_text_count = 1000 - $rec_text_entry.val().length;
            $rec_chars_left.text($rec_text_count);
            
            $rec_text_entry.on('input', function(){
                $rec_text_count = 1000 - $rec_text_entry.val().length;
                if($rec_text_count >= 0){
                    $rec_chars_left.text($rec_text_count);
                }
                else{
                    var new_val = $rec_text_entry.val().toString().substr(0,1000);
                    $rec_text_entry.val(new_val);
                    $rec_chars_left.text(0);
                }
            });
        }
        
        if($comment_text_entry.length){
            var $comment_text_count = 250 - $comment_text_entry.val().length;
            $comment_chars_left.text($comment_text_count);
            
            $comment_text_entry.on('input', function(){
                $comment_text_count = 250 - $comment_text_entry.val().length;
                if($comment_text_count >= 0){
                    $comment_chars_left.text($comment_text_count);
                }
                else{
                    var new_val = $comment_text_entry.val().toString().substr(0,250);
                    $comment_text_entry.val(new_val);
                    $comment_chars_left.text(0);
                }
            });
        }
        
        if($about_me_text_entry.length){
            var $about_me_count = 500 - $about_me_text_entry.val().length;
            $about_me_chars_left.text($about_me_count);
            
            $about_me_text_entry.on('input', function(){
                $about_me_count = 500 - $about_me_text_entry.val().length;
                if($about_me_count >= 0){
                    $about_me_chars_left.text($about_me_count);
                }
                else{
                    var new_val = $about_me_text_entry.val().toString().substr(0,500);
                    $about_me_text_entry.val(new_val);
                    $about_me_chars_left.text(0);
                }
            });
        }
    });
}(window.jQuery, window, document));
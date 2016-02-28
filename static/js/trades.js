/** Trade proposal handling  **/

function set_proposal_message(proposal) {
  var message = $('#message').val();
	$.post('set_proposal_message',
	       { 'proposal': proposal,
	         'message' : message });
	return true;
}

$(function() {
	$('.proposal-button').click(function() {
    set_proposal_message(current_proposal_id);
  });

  var prevent_submission = true;
  $('.search-form').submit(function(e) {
     if (prevent_submission) {
     	 e.preventDefault();
       set_proposal_message(current_proposal_id);
       prevent_submission = false;
       $(this).submit();
     }
  });
});
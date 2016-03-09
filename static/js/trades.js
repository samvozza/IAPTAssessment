/** Trade proposal handling  **/

function set_proposal_details(proposal) {
  var title = $('#title').val();
  if (title != '') {
	  $.ajax({
      type: 'POST',
      url: 'set_proposal_title',
      data: { 'proposal': proposal,
	            'title'   : title },
      async: false
    });
	}

  var message = $('#message').val();
	$.ajax({
    type: 'POST',
    url: 'set_proposal_message',
    data: { 'proposal': proposal,
	          'message' : message },
    async: false
  });

	$('.quantity-input').each(function() {
		var item = $(this).siblings('[name=item_id]').val();
    $.ajax({
      type: 'POST',
      url: 'set_proposal_item_quantity',
      data: { 'proposal': proposal,
	            'item'    : item,
	            'quantity': $(this).val() },
      async: false
    });
  });

	return true;
}

$(function() {
	$('.proposal-button').click(function() {
    set_proposal_details(current_proposal_id);
  });

  var prevent_submission = true;
  $('.search-form').submit(function(e) {
     if (prevent_submission) {
     	 e.preventDefault();
       set_proposal_details(current_proposal_id);
       prevent_submission = false;
       $(this).submit();
     }
  });
  
  $('.send-proposal').click(function() {
  	var error = false;
    $('.quantity-input').each(function() {
		  var item = $(this).siblings('[name=item_id]').val();
		  var item_limit = $(this).siblings('[name=item_limit]').val();
		  var item_quantity = $(this).val();
      if (item_quantity > item_limit || item_quantity < 0) {
        set_proposal_details(current_proposal_id);
        window.location.href = current_proposal_url + "&message=invalid_quantity";
        error = true;
      }
    });
    return !error;
  });
});
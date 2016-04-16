/** Trade proposal handling  **/

function loadCollections() {
	$('.collection-link').each(function() {
		id = $(this).siblings('form').find('[name=collection_id]').val();
	  
	  if (id == current_collection_id) {
	  	$(this).addClass('active');
	  } else {
	  	$(this).removeClass('active');
	  }
  });
}

function getCollectionData() {
	var collection_items;
	
	$.ajax({
    type: 'GET',
    url: 'get_collection_items.json',
    data: { 'proposal': current_proposal_id,
            'collection': current_collection_id },
		dataType: 'json',
	  success: function(data) {
	  	$.each(data, function(index, element) {
	  		if (index == 'collection_items') {
	        collection_items = element;
	  		}
      });
	  },
    async: false
  });
  
  return collection_items;
}

function getItemData() {
	var users_items;
	var other_users_items;
	
	$.ajax({
    type: 'GET',
    url: 'get_proposal_items.json',
    data: { 'proposal': current_proposal_id },
		dataType: 'json',
	  success: function(data) {
	  	$.each(data, function(index, element) {
	  		if (index == 'users_items') {
	        users_items = element;
	   	  } else if (index == 'other_users_items') {
	        other_users_items = element;
	  		}
      });
	  },
    async: false
  });
  
  return [users_items, other_users_items];
}

function calculateValue(items) {
	var total = 0;
	$.each(items, function(index, item) {
		total += item.value * item.quantity;
	});
	return total;
}

function loadItems() {
	item_data = getItemData();
	users_items = item_data[0];
	other_users_items = item_data[1];
	collection_items = getCollectionData();
	
	$('.item-preview').remove();
	$('.no-items').remove();

  collection_section = $('#collection-items');
  if (collection_items.length > 0) {
    $.each(collection_items, function(index, element) {
    	item_preview = makeCollectionItemPreview(element);
	    item_preview.appendTo(collection_section);
    });
  } else {
  	$('<div class="alert alert-info no-items">There are no objects in this collection.</div>').appendTo(collection_section);
  }

  your_items_section = $('#your-items-panel');
  $.each(users_items, function(index, element) {
  	item_preview = makeSummaryItemPreview(element);
	  item_preview.appendTo(your_items_section);
  });
	$('#your-items').find('.total-value').html(calculateValue(users_items).toFixed(2));
  
  their_items_section = $('#their-items-panel');
  $.each(other_users_items, function(index, element) {
  	item_preview = makeSummaryItemPreview(element);
	  item_preview.appendTo(their_items_section);
  });
	$('#their-items').find('.total-value').html(calculateValue(other_users_items).toFixed(2));
}

function makeCollectionItemPreview(item) {
	item_preview = $('#collection-item-template').clone();
	item_preview.attr('id', 'collection-item-preview-' + item.id);
	item_preview.addClass('item-preview');
	item_image = item_preview.find('img');
	item_image.attr('src', downloads_url + "/" + item.image);
	item_image.attr('alt', item.name);
	item_preview.find('.object-name').html(item.name);
	item_preview.find('.item-value').html('&pound;' + item.value.toFixed(2));
	item_details_button = item_preview.find('.item-details');

  if (item.in_trade) {
	  item_preview.addClass('selected-panel');
	  item_remove_button = item_preview.find('.remove-item');
  	item_remove_button.show();
  	item_remove_button.click(function() {
      setProposalDetails();
  		$.ajax({
  			type: 'POST',
  			url: 'set_proposal_item_quantity',
  			data: { 'proposal': current_proposal_id,
  			        'item'    : item.id,
	              'quantity': 0 },
        async: false
      });
      loadItems();
      return false;
	  });
  } else {
	  item_add_button = item_preview.find('.add-item');
  	item_add_button.show();
  	item_add_button.click(function() {
      setProposalDetails();
  		$.ajax({
  			type: 'POST',
  			url: 'set_proposal_item_quantity',
  			data: { 'proposal': current_proposal_id,
  			        'item'    : item.id,
	              'quantity': 1 },
        async: false
      });
      loadItems();
      return false;
	  });
  }

	item_preview.show();
	return item_preview;
}

function makeSummaryItemPreview(item) {
	item_preview = $('#summary-item-template').clone();
	item_preview.attr('id', 'summary-item-preview-' + item.id);
	item_preview.addClass('item-preview');
	item_image = item_preview.find('img');
	item_image.attr('src', downloads_url + "/" + item.image);
	item_image.attr('alt', item.name);
	item_preview.find('.object-name').html(item.name);
	item_preview.find('.item-value').html('&pound;' + item.value.toFixed(2));
	item_quantity_input = item_preview.find('.quantity-input');
	item_quantity_input.attr('id', 'quantity-input-' + item.id);
	item_quantity_input.attr('value', item.quantity);
	item_quantity_input.change(function() {
    setProposalDetails();
	  loadItems();
  });
	
	item_preview.find('.quantity-limit').html(item.available_quantity);
	item_preview.find('[name=item_id]').attr('value', item.id);
	item_preview.find('[name=item_limit]').attr('value', item.available_quantity);
	item_remove_button = item_preview.find('.remove-item');
	item_remove_button.click(function() {
    setProposalDetails();
		$.ajax({
			type: 'POST',
			url: 'set_proposal_item_quantity',
      data: { 'proposal': current_proposal_id,
	            'item'    : item.id,
	            'quantity': 0 },
      async: false
    });
    loadItems();
    return false;
	});
	
	item_quantity_form = item_preview.find('.quantity-form');
	if (item.quantity > item.available_quantity || item.quantity < 0) {
		item_quantity_form.addClass('has-error');
		
		if (item.quantity > item.available_quantity) {
			$('<span class="help-block form-helper">Please choose a lower quantity</span>').appendTo(item_quantity_form);
		}
		
		if (item.quantity < 0) {
			$('<span class="help-block form-helper">Please choose a higher quantity</span>').appendTo(item_quantity_form);
		}
	}
	
	item_preview.show();
	return item_preview;
}

function setProposalDetails() {
  var title = $('#title').val();
  if (title != '') {
	  $.ajax({
      type: 'POST',
      url: 'set_proposal_title',
      data: { 'proposal': current_proposal_id,
	            'title'   : title },
      async: false
    });
	}

  var message = $('#message').val();
	$.ajax({
    type: 'POST',
    url: 'set_proposal_message',
    data: { 'proposal': current_proposal_id,
	          'message' : message },
    async: false
  });

	$('.quantity-input').each(function() {
		if ($(this).attr('id') != 'quantity-item-template') {
		  var item = $(this).siblings('[name=item_id]').val();
      $.ajax({
        type: 'POST',
        url: 'set_proposal_item_quantity',
        data: { 'proposal': current_proposal_id,
	              'item'    : item,
	              'quantity': $(this).val() },
        async: false
      });
    }
  });
}

function setSummaryBar() {
	if ($('#summary-section').visible(true)) {
    $('#trade-summary-bar').hide();
  } else {
  	$('#trade-summary-bar').show();
  }
}

$(function() {
	loadCollections();
	loadItems();
	setSummaryBar();
	
	$('.proposal-button').click(function() {
    setProposalDetails();
  });

  var prevent_submission = true;
  $('.search-form').submit(function(e) {
     if (prevent_submission) {
     	 e.preventDefault();
       setProposalDetails();
       prevent_submission = false;
       $(this).submit();
     }
  });
  
  $('.send-proposal').click(function() {
  	var error = false;
    $('.quantity-input').each(function() {
    	if ($(this).attr('id') != 'quantity-item-template') {
		    var item = $(this).siblings('[name=item_id]').val();
        var item_limit = $(this).parent().find('[name=item_limit]').val();
		    var item_quantity = $(this).val();
        if (item_quantity > item_limit || item_quantity < 0) {
          setProposalDetails();
          window.location.href = current_proposal_url + "&message=invalid_quantity";
          error = true;
        }
      }
    });
    return !error;
  });

  $(window).scroll(function() {
    setSummaryBar();
  });
  
  $('.collection-link').each(function() {
  	$(this).click(function() {
      setProposalDetails();
  		current_collection_id = $(this).siblings('form').find('[name=collection_id]').val();
  		loadCollections();
      loadItems();
      return false;
    });
	});
	
	$('.summary-link').click(function() {
	  $('html, body').animate({
	  	scrollTop: $("#summary").offset().top
    }, 500);
    return false;
  });
});

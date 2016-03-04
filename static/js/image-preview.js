/** Image loading as suggested by
https://stackoverflow.com/questions/18457340/how-to-preview-selected-image-in-input-type-file-in-popup-using-jquery */

function load_image_preview(input, dest) {
	if (input.files && input.files[0]) {
		var reader = new FileReader();

		reader.onload = function(e) {
			$(dest).attr('src', e.target.result);
			$(dest).attr('hidden', false);
		};

		reader.readAsDataURL(input.files[0]);
	}
}

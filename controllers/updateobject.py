#When the value was sent to the form, the record should be able to take that value.
def updateobject():
	db.Objects.description.widget = SQLFORM.widgets.text.widget
	record = db.Objects(request.args(0))
	updateobjectform = SQLFORM(db.Objects, record, fields = ['name', 'price', 'type_taxonomy', 'quantity', 'tradable_quantity', 'description', 'image'])
															
	if updateobjectform.accepts(request, session):
		response.flash = "Your object is updated."
		
	elif updateobjectform.errors:
		response.flash = "One or more errors in your form field. Please see below for more information."
		
	else:
		response.flash = "Please complete the form to update your object."
		
	return dict(updateobjectform = updateobjectform)

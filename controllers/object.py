#When the value was sent to the form, the record should be able to take that value.
@auth.requires_login() 
def update():
	db.Objects.description.widget = SQLFORM.widgets.text.widget
	record = db.object(request.args(0))
	updateobjectform = SQLFORM(db.object, record, fields = ['name', 'price', 'category', 'quantity', 'tradable_quantity', 'wanted_quantity','description', 'image'])

	if updateobjectform.accepts(request, session):
		response.flash = "Your object is updated."

	elif updateobjectform.errors:
		response.flash = "One or more errors in your form field. Please see below for more information."

	else:
		response.flash = "Please complete the form to update your object."

	return dict(updateobjectform = updateobjectform)

@auth.requires_login() 
def create():
	addobjectform = SQLFORM(db.object)
	if addobjectform.process(onvalidation = checking_quantity).accepted:
		response.flash = "New object is added."
		
	elif addobjectform.errors:
		response.flash = "One or more errors in your form field. Please see below for more information."
		
	else:
		response.flash = "Please complete the form below to add a new object."
		
	return dict(addobjectform = addobjectform)
	
#check the quantity and tradable_quantity to ensure that tradable_quantity is less than quantity.	
def checking_quantity(form):
	if (form.vars.quantity  < form.vars.tradable_quantity):
		form.errors.tradable_quantity = "Tradable quantity cannot be greater than quantity of the object."
	else:
		form.vars.tradable_quantity = form.vars.tradable_quantity
	
		
def viewobject():
	results = db(db.object.id == 1).select()
	return dict(results = results)
		


		


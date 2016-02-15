#When the value was sent to the form, the record should be able to take that value.
def update():
	db.Objects.description.widget = SQLFORM.widgets.text.widget
	record = db.object(request.args(0))
	updateobjectform = SQLFORM(db.object, record, fields = ['name', 'price', 'type_taxonomy', 'quantity', 'tradable_quantity', 'description', 'image'])

	if updateobjectform.accepts(request, session):
		response.flash = "Your object is updated."

	elif updateobjectform.errors:
		response.flash = "One or more errors in your form field. Please see below for more information."

	else:
		response.flash = "Please complete the form to update your object."

	return dict(updateobjectform = updateobjectform)

def create():
	setOfType = ['Advertising and brand', 'Architectural', 'Books, magazines, and paper', 'Clothing,fabric and textiles', 'Coins, currency, stamps',
				'Film and television', 'Glass and pottery', 'Household items', 'Memorabilia', 'Music', 'Nature and animals','Sports',
				'Technology ', 'Themed', 'Toys and games']

	addobjectform = FORM(DIV(LABEL('Name', _for = 'name')),
						 DIV(INPUT(_name = 'name', requires = [IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in the object's name.")])),
						 DIV(LABEL('Price(£)', _for = 'price')),
						 DIV(INPUT(_name = 'price', requires = [IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in the value of the object."),
																IS_DECIMAL_IN_RANGE(0,None, dot = ".", error_message = "Please type in a numeric value.")])),

						 DIV(LABEL('Type', _for = 'type_taxonomy')),
						 DIV(SELECT(*setOfType, **dict(_name = 'type_taxonomy'))),
						 DIV(LABEL('Quantity', _for = 'quantity')),
						 DIV(INPUT(_name = 'quantity', requires = [IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in the number of the objects that you want to upload."),
																   IS_INT_IN_RANGE(0, None, error_message = "Please type in an integer, not a decimal number or others.")])),

						 DIV(LABEL('Tradable Quantity', _for = 'tradable_quantity')),
						 DIV(INPUT(_name = 'tradable_quantity', requires = [IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in the number of the objects that you want to trade with people."),
																			IS_INT_IN_RANGE(0, None, error_message = "Please type in an integer, not a decimal number or others.")])),

						 DIV(LABEL('Description', _for = 'description')),
						 DIV(TEXTAREA(_name = 'description',  requires = IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in a short description of your object."))),
						 DIV(LABEL('Image', _for = 'image')),
						 DIV(INPUT(_name = 'image', _type = 'file', requires = IS_IMAGE(extensions=('jpeg','png'), error_message = "The extension of an image should be '.jpeg' or 'png'."))),
						 DIV(INPUT(_type = 'submit')))

	if addobjectform.accepts(request, session):
		db.Objects.insert(name = request.vars.name, price = request.vars.price, type_taxonomy = request.vars.type_taxonomy, quantity = request.vars.quantity,
						 tradable_quantity = request.vars.tradable_quantity, description = request.vars.description, image = request.vars.image)
		db.commit
		response.flash = "New object is added."

	elif addobjectform.errors:
		response.flash = "One or more errors in your form field. Please see below for more information."

	else:
		response.flash = "Please complete the form below to add a new object."

	return dict(addobjectform = addobjectform)

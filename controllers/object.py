@auth.requires_login()
def update():
	db.object.description.widget = SQLFORM.widgets.text.widget
	record = db(db.object.id == request.args[0]).select().first()
	db.object.id.readable  = False
	db.object.owner.readable = False
	updateobjectform = SQLFORM(db.object, record, fields = ['name', 'collection', 'price', 'category', 'quantity', 'tradable_quantity', 'wanted_quantity','description', 'image'], submit_button = 'Update')
	owner = db(db.auth_user.id == record.owner).select().first()
	current_collection = db(db.collection.id == record.collection).select().first()
	updateobjectform.vars.collection = current_collection.id

	if updateobjectform.process(onvalidation = checking_quantity).accepted:
		response.flash = "Your object is updated."

	elif updateobjectform.errors:
		response.flash = "One or more errors in your form field. Please see below for more information."

	else:
		response.flash = "Please complete the form to update your object."

	name = 'Your' if owner.id == auth.user.id else owner.username + '\'s'
	add_breadcrumb(name + ' Collections', URL('collection', 'user', args=[owner.id]))
	add_breadcrumb(current_collection.name, URL('collection', 'view', args=[current_collection.id]))
	add_breadcrumb('Edit Item')
	add_breadcrumb(record.name)
	return dict(updateobjectform = updateobjectform, record = record)

@auth.requires_login()
def create():
	response.owner = db(db.auth_user.id == auth.user_id).select().first()
	if request.vars.collection:
		response.collection = db(db.collection.id == request.vars['collection']).select().first()
	else:
		response.collection = db((db.collection.name == 'Default') & (db.collection.owner == auth.user.id)).select().first()

	form = SQLFORM(db.object, fields = ['name', 'collection', 'price', 'category', 'quantity', 'tradable_quantity', 'wanted_quantity','description', 'image'], submit_button='Create')
	form.vars.owner = auth.user_id
	form.vars.collection = response.collection.id
	if form.process(onvalidation = checking_quantity).accepted:
		redirect(URL('object', 'view', args=[form.vars.id], vars=dict(message='object_created')))
	elif form.errors:
		response.flash = "One or more errors in your form field. Please see below for more information."

	name = 'Your' if response.owner.id == auth.user.id else response.owner.username + '\'s'
	add_breadcrumb(name + ' Collections', URL('collection', 'user', args=[response.owner.id]))
	add_breadcrumb(response.collection.name, URL('collection', 'view', args=[response.collection]))
	add_breadcrumb('Add Item')
	return dict(form = form)

#check the quantity and tradable_quantity to ensure that tradable_quantity is less than quantity.
def checking_quantity(form):
	if (form.vars.quantity  < form.vars.tradable_quantity):
		form.errors.tradable_quantity = "Tradable quantity cannot be greater than quantity of the object."
	else:
		form.vars.tradable_quantity = form.vars.tradable_quantity
		
def canceladd():
	response.owner = db(db.auth_user.id == auth.user_id).select().first()
	collection = db(db.collection.id == request.args[0]).select().first()
	if request.vars.collection:
		response.collection = db(db.collection.id == request.vars['collection']).select().first()
	else:
		response.collection = db((db.collection.name == 'Default') & (db.collection.owner == auth.user.id)).select().first()
		
	form = FORM(DIV(P('Are you sure you want to cancel adding a new item in collection: ' + collection.name + ' ?')),
	            LABEL(),
                DIV(DIV(INPUT(_type='button', _value='No', _onclick='window.location=\'%s\';;return false' %
                URL('create'), _class='btn btn-primary pull-left'),
                                _class='col-sm-0 col-md-0 col-lg-0')),
                DIV(DIV(INPUT(_type='submit', _value='Yes', _class='btn btn-danger pull-left'),
                            _class='col-sm-1 col-md-1 col-lg-1')),
               )
	if form.accepts(request,session):
            response.flash = 'Going back to the collection: ' + collection.name + ' .'
            redirect(URL('collection', 'view', args=[collection.id]))
			
	name = 'Your' if response.owner.id == auth.user.id else response.owner.username + '\'s'
	add_breadcrumb(name + ' Collections', URL('collection', 'user', args=[response.owner.id]))
	add_breadcrumb(response.collection.name, URL('collection', 'view', args=[response.collection]))
	add_breadcrumb('Add Item')
	add_breadcrumb('Cancel')
	return dict(form = form)
	
def canceledit():
	response.owner = db(db.auth_user.id == auth.user_id).select().first()
	record = db(db.object.id == request.args[0]).select().first()	
	collection = db(db.collection.id == record.collection).select().first()
	if request.vars.collection:
		response.collection = db(db.collection.id == request.vars['collection']).select().first()
	else:
		response.collection = db((db.collection.name == 'Default') & (db.collection.owner == auth.user.id)).select().first()
		
	form = FORM(DIV(P('Are you sure you want to cancel editing ' + record.name + ' ?')),
	            LABEL(),
                DIV(DIV(INPUT(_type='button', _value='No', _onclick='window.location=\'%s\';;return false' %
                URL('update', args =[record.id]), _class='btn btn-primary pull-left'),
                                _class='col-sm-0 col-md-0 col-lg-0')),
                DIV(DIV(INPUT(_type='submit', _value='Yes', _class='btn btn-danger pull-left'),
                            _class='col-sm-1 col-md-1 col-lg-1')),
               )
	if form.accepts(request,session):
            response.flash = 'Going back to item: ' + record.name + ' .'
            redirect(URL('object', 'view', args=[record.id]))
			
	name = 'Your' if response.owner.id == auth.user.id else response.owner.username + '\'s'
	add_breadcrumb(name + ' Collections', URL('collection', 'user', args=[response.owner.id]))
	add_breadcrumb(response.collection.name, URL('collection', 'view', args=[response.collection]))
	add_breadcrumb(record.name)
	add_breadcrumb('Edit ' + record.name)
	add_breadcrumb('Cancel')
	return dict(form = form)

def view():
	response.result = db(db.object.id == request.args[0]).select().first()
	response.collection = db(db.collection.id == response.result.collection).select().first()
	response.owner = db(db.auth_user.id == response.collection.owner).select().first()
	
	category_id = db(db.object.id == request.args[0])._select(db.object.category)
	sel_category = db(db.category.id.belongs(category_id)).select()
	response.category = sel_category[0].name

	name = 'Your' if response.owner.id == auth.user.id else response.owner.username + '\'s'
	add_breadcrumb(name + ' Collections', URL('collection', 'user', args=[response.owner.id]))
	add_breadcrumb(response.collection.name, URL('collection', 'view', args=[response.collection]))
	add_breadcrumb(response.result.name)
	return dict()

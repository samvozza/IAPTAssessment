#This is a table just for testing the addobject function. It should be modified after
#we have our data model.
db.define_table('Objects',
	Field('name'),
	Field('price'),
	Field('type_taxonomy'),
	Field('quantity'),
	Field('tradable_quantity'),
	Field('description'),
	Field('image', 'upload'))

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')

from gluon.tools import Auth, Service, PluginManager


db = DAL('sqlite://storage.db')
auth = Auth(db, controller='auth')
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)
db.auth_user.username.requires = IS_NOT_IN_DB(db, 'auth_user.username')

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# configure auth messages
auth.messages.logged_in = None
auth.messages.logged_out = None

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.define_table('collection',
    Field('name', type='string', unique=True),
    Field('owner', db.auth_user, default=auth.user_id),
    Field('public', type="boolean")
)

db.define_table('category',
    Field('name', type='string', unique=True)
)

db.define_table('object',
	Field('name', type="string",requires = IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in the object's name.")),
    Field('collection', db.collection),
	Field('price', type="double",requires = IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in the value of the object.")),
	Field('category', requires = IS_IN_SET(db.category, error_message = "This field cannot be empty. Please select the category of your object.")),
	Field('quantity', type="integer", requires = IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in the quantity of your object that you want to upload.")),
	Field('tradable_quantity', type="integer", requires = IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in how many of your objects for trade.")),
	Field('description', type="text", requires = IS_NOT_EMPTY(error_message = "This field cannot be empty. Please give a short description of your object.")),
	Field('image', type='upload', default = 'static/images/thumbnail.jpg', uploadfield=True,
		requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg','png','jpg'), error_message = "The extension of an image should be '.jpeg', 'png' or 'jpg'."))))

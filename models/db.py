from datetime import datetime
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

#User settings table
#+user refers to a user
#+trade_non_tradable_items whether the user is happy to receive
#requests for items which they have not marked as tradable
db.define_table('user_settings',
                Field('user', db.auth_user, default=auth.user_id,
                      notnull=True, unique=True, ondelete="CASCADE"),
                Field('trade_non_tradable_items', type='boolean', default=True,
                      notnull=True)
)

#Collection table
#+owner refers to User
#+name  should be unique per owner, but not be unique in the DB (e.g Default)
#+public
db.define_table('collection',
                Field('owner', db.auth_user, default=auth.user_id,
                      notnull=True, ondelete="CASCADE"),
                Field('name', type='string', length=64, required=True,
                      notnull=True),
                Field('public', type="boolean", default=False,
                      notnull=True)
)

#Category table
#+name  used as enumeration values by Object.category
db.define_table('category',
                Field('name', type='string', length=32,
                notnull=True, unique=True)
)

#Object table
#+owner refers to User
#+collection refers to Collection. Allow null, for loose Objects
#+name
#+price non-negative value in GBP; assumed "0.0" => "not set"
#+category refers to Category
#quantity quantity (owned) subset; non-negative integer
#tradable_quantity quantity (tradable) subset; non-negative integer
#+description
#+image image is required, but may be the default thumbnail

db.define_table('object',
        Field('owner', db.auth_user, default=auth.user_id,
                notnull=True, ondelete="CASCADE",
	        comment = T("This is the owner of the object.")),
        Field('collection',  db.collection, required=True,
                notnull=False, ondelete="SET NULL",
                label ='Collection',
	        requires = IS_IN_DB(db(db.collection.owner == auth.user_id), db.collection.id, '%(name)s',
                error_message = "This field cannot be empty. Please select the collection that your object is added to."),
		comment = T("Choose one of your collections for your object.")),
        Field('name', type="string", length=64, required=True,
                requires = IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in the object's name."),
                notnull=True,
		label ='Name',
		comment = T("Enter a name for the object.")),
        Field('price', type="double", default = 0,
                requires = IS_FLOAT_IN_RANGE(0, 1e100, error_message = "This field cannot be empty. Please type in the value of the object."),
                notnull=True,
		label ='Price',
                comment = T("Enter the price for your object.")),
        Field('category', type="string", length=32, required=True,
		requires = IS_IN_DB(db(db.category.name == db.category.name), db.category.id, '%(name)s',
					error_message = "This field cannot be empty. Please select the category of your object."),
		label ='Category',
                notnull=True,
		comment = T("Choose one of the categories for your object.")),
        Field('quantity', type="integer", default=0,
                requires = IS_INT_IN_RANGE(0, 1e100, error_message = "This field cannot be empty or negative. Please type in the quantity of your object that you want to upload."),
                notnull=True,
		label ='Quality',
		comment = T("Enter the amount of the object(s) that you want to store in your collection.")),
        Field('tradable_quantity', type="integer", default=0,
                requires=IS_INT_IN_RANGE(0, 1e100, error_message = "This field cannot be empty or negative. Please type in how many objects for trade."),
                notnull=True,
		label ='Tradable Quantity',
		comment = T("Enter the number of your object(s) for trade.")),
        Field('wanted_quantity', type="integer", default=0,
                requires=IS_INT_IN_RANGE(0, 1e100, error_message = "This field cannot be empty or negative. Please type in how many objects you wish to trade for."),
                notnull=True,
		label ='Wanted Quantity',
		comment = T("Enter the number of object(s) that you wish to trade for.")),
        Field('description', type="text", length=65536, default="",
                requires = None,
                notnull=True,
		label ='Description',
		comment = T("Enter a short description for your object.")),
        Field('image', type="upload", uploadfield=True, default="static/images/thumbnail.jpg",
                requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg','png','jpg'), error_message = "The extension of an image should be '.jpeg', 'png' or 'jpg'.")),
                notnull=True,
		label ='Image',
		comment = T("Upload an image for your object, otherwise, we set a default image for your object. " +
				"You can upload your image anytime you want."))
)

#Trade table defaults/enums
DEFAULT_TRADE_TITLE = "New trade proposal"

STATUS_PREPARE = 0 #IN PREPARATION
STATUS_ACTIVE = 1 #SENDER ABLE TO EDIT
STATUS_OFFERED = 2 #RECEIVER ABLE TO EDIT
STATUS_ACCEPTED = 3
STATUS_REJECTED = 4
STATUS_CANCELLED = 5

#Trade table
#+sender refers to User; who initially proposed the trade
#+receiver refers to User; who the trade was initially sent to
#+title
#+status value from STATUS constants indicating current trade status
#+message
#+time_created timestamp of Trade creation
#+time_modified timestamp of when proposal was last modified
db.define_table('trade',
                Field('sender', db.auth_user, default=auth.user_id,
                      notnull=True, ondelete="CASCADE"),
                Field('receiver', db.auth_user, required=True,
                      notnull=True, ondelete="CASCADE"),
                Field('title', type="string", length=64, required=True,
                      notnull=True),
                Field('status', type="integer", default=STATUS_PREPARE,
                      notnull=True),
                Field('message', type="string", length=512, default=DEFAULT_TRADE_TITLE,
                      notnull=True),
                Field('time_created', type='datetime', default=datetime.now,
                      notnull=True, writable=False),
                Field('time_modified', type='datetime', default=datetime.now, update=datetime.now,
                      notnull=True, writable=False),
)

#Trade_contains_Object table
#+trade refers to Trade
#+object refers to Object
#+quantity the number of the Objects in the Trade
db.define_table('trade_contains_object',
                Field('trade', db.trade, required=True,
                      notnull=True, ondelete="CASCADE"),
                Field('object', db.object, required=True,
                      notnull=False, ondelete="SET NULL"),
                Field('quantity', type="integer", required=True,
                      notnull=False),
)

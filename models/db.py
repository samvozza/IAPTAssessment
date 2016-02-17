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
                      notnull=True, ondelete="CASCADE"),
                Field('collection',  db.collection, required=True,
                      notnull=False, ondelete="SET NULL",
                      requires = IS_IN_DB(db(db.collection.owner == auth.user_id), db.collection.id, '%(name)s',
											                    error_message = "This field cannot be empty. Please select the collection that your object is added to.")),
                Field('name', type="string", length=64, required=True,
                      requires = IS_NOT_EMPTY(error_message = "This field cannot be empty. Please type in the object's name."),
                      notnull=True),
                Field('price', type="double", default=0,
                      requires = IS_FLOAT_IN_RANGE(0, 1e100, error_message = "This field cannot be empty. Please type in the value of the object."),
                      notnull=True),
                Field('category', type="string", length=32, required=True,
 #                     requires = IS_IN_SET(db.category, error_message = "This field cannot be empty. Please select the category of your object."),
                      requires = IS_IN_DB(db(db.category.name == db.category.name), db.category.id, '%(name)s',
										                        error_message = "This field cannot be empty. Please select the category of your object."),
                      notnull=True),
                Field('quantity', type="integer", default=0,
                      requires = IS_INT_IN_RANGE(0, 1e100, error_message = "This field cannot be empty or negative. Please type in the quantity of your object that you want to upload."),
                      notnull=True),
                Field('tradable_quantity', type="integer", default=0,
                      requires=IS_INT_IN_RANGE(0, 1e100, error_message = "This field cannot be empty or negative. Please type in how many objects for trade."),
                      notnull=True),
                Field('wanted_quantity', type="integer", default=0,
                      requires=IS_INT_IN_RANGE(0, 1e100, error_message = "This field cannot be empty or negative. Please type in how many objects you wish to trade for."),
                      notnull=True),
                Field('description', type="text", length=65536, default="",
                      requires = None,
                      notnull=True),
                Field('image', type="upload", uploadfield=True, default="static/images/thumbnail.jpg",
                      requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg','png','jpg'), error_message = "The extension of an image should be '.jpeg', 'png' or 'jpg'.")),
                      notnull=True)
)

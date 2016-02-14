def view():
    response.collections = db(db.collection.owner == '1').select()
    return dict(message=T('Welcome to web2py!'))


def create():

    form=FORM(TABLE(
                DIV(LABEL('Name', _for = 'name')),
                DIV(INPUT(_type="text",_name="name",requires=IS_NOT_EMPTY())),
                DIV(LABEL('Type', _for = 'public')),
                DIV(SELECT('yes','no',_name="public",requires=IS_IN_SET(['yes','no']))),
                DIV(LABEL('', _for = 'submit')),
                DIV(INPUT(_type="submit",_value="SUBMIT"))))

    form.vars.owner = 1

    if form.accepts(request,session):
        response.flash = 'collection created'
        redirect(URL('view'))

    elif form.errors:
        response.flash = 'value missing'

    else:
        response.flash = 'please fill the form'

    return  dict(form=form)


def edit():
    form=FORM(TABLE(DIV(LABEL('Name', _for = 'name')),
                    DIV(INPUT(_type="text",_name="name",_class="control-form col-md-5",requires=IS_NOT_EMPTY())),
                    DIV(LABEL('Type', _for = 'public')),
                    DIV(SELECT('yes','no',_name="sure",requires=IS_IN_SET(['yes','no']))),
                    DIV(LABEL('', _for = 'submit')),
                    DIV(INPUT(_type="submit",_value="SUBMIT"))
                    )
             )
    form.vars.owner = 1

    if form.accepts(request,session):
            response.flash = 'Your collection updated.'
            redirect(URL('view'))
    elif form.errors:
        response.flash = 'We couldn\' process your form because it contain errors. Check below for more detail.'
    else:
        response.flash = 'You the form below to create a new collection.'

    return  dict(form=form)

def my():
    redirect(URL('collection', 'view', args=['1']))

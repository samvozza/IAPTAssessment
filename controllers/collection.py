def view():
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))

def new_collection():

    form=FORM(TABLE
                (
                DIV(LABEL('Name', _for = 'name')),
                DIV(INPUT(_type="text",_name="name",requires=IS_NOT_EMPTY())),
                DIV(LABEL('Public', _for = 'privacy')),
                DIV(INPUT(_type="checkbox", _name="privacy")),
                DIV(LABEL('', _for = 'submit')),
                DIV(INPUT(_type="submit",_value="SUBMIT"))
                )
            )

    if form.accepts(request,session):
        response.flash = 'collection created'
        redirect(URL('view'))
        #db.collection.insert(name = form.vars.name, privacy = form.vars.privacy)

    elif form.errors:
        response.flash = 'value missing'

    else:
        response.flash = 'please fill the form'

    return  dict(form=form)

def edit_collection():

    form=FORM(TABLE
                    (
                    DIV(LABEL('Name', _for = 'name')),
                    DIV(INPUT(_type="text",_name="name",requires=IS_NOT_EMPTY())),
                    DIV(LABEL('Public', _for = 'privacy')),
                    DIV(INPUT(_type="checkbox", _name="privacy")),
                    DIV(LABEL('', _for = 'submit')),
                    DIV(INPUT(_type="submit",_value="SUBMIT"))
                    )
             )

    if form.accepts(request,session):
            response.flash = 'collection updated'
            redirect(URL('view'))
            #db(db.collection.name == vars.name).update(name = form.vars.name, privacy = form.vars.privacy)

    elif form.errors:
        response.flash = 'form has errors'

    else:
        response.flash = 'please fill the form'

    return  dict(form=form)

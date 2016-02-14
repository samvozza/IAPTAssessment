def view():
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def new_collection():

    form=FORM(TABLE(
                DIV(LABEL('Name', _for = 'name')),
                DIV(INPUT(_type="text",_name="name",requires=IS_NOT_EMPTY())),
                DIV(LABEL('Type', _for = 'privacy')),
                DIV(SELECT('yes','no',_name="privacy",requires=IS_IN_SET(['yes','no']))),
                DIV(LABEL('', _for = 'submit')),
                DIV(INPUT(_type="submit",_value="SUBMIT"))))

    if form.accepts(request,session):
        response.flash = 'collection created'
        redirect(URL('view'))

    elif form.errors:
        response.flash = 'value missing'

    else:
        response.flash = 'please fill the form'

    return  dict(form=form)

def edit_collection():

    form=FORM(TABLE(
                    DIV(LABEL('Name', _for = 'name')),
                    DIV(INPUT(_type="text",_name="name",requires=IS_NOT_EMPTY())),
                    DIV(LABEL('Type', _for = 'privacy')),
                    DIV(SELECT('yes','no',_name="sure",requires=IS_IN_SET(['yes','no']))),
                    DIV(LABEL('', _for = 'submit')),
                    DIV(INPUT(_type="submit",_value="SUBMIT"))
                    )
             )

    if form.accepts(request,session):
            response.flash = 'collection updated'
            redirect(URL('view'))

    elif form.errors:
        response.flash = 'form has errors'

    else:
        response.flash = 'please fill the form'

    return  dict(form=form)

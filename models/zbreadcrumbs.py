# Breadcrumbs

class Breadcrumb(object):
    def __init__(self, text, link=None):
        self._text = text
        self._link = link

    def text(self):
        return self._text
    
    def make_link(self, active=False):
        if active:
            return LI(self._text, _class='active')
        elif self._link == None:
            return LI(self._text)
        else:
            return LI(A(self._text, _href=self._link))


def start_breadcrumbs():
    if response.breadcrumbs == None:
        response.breadcrumbs = [Breadcrumb('Home', URL('default', 'index'))]


def add_breadcrumb(text, link=None):
    start_breadcrumbs()
    breadcrumb = Breadcrumb(text, link)
    response.breadcrumbs.append(breadcrumb)


def last_breadcrumb_text():
    start_breadcrumbs()
    return response.breadcrumbs[-1].text()


def make_breadcrumbs():
    start_breadcrumbs()
    
    breadcrumbs = []
    for breadcrumb in response.breadcrumbs[:-1]:
        breadcrumbs.append(breadcrumb.make_link())
    
    breadcrumbs.append(response.breadcrumbs[-1].make_link(True))
    return breadcrumbs


def page_title():
    # Prefer response.title, as long as it isn't set to its default
    if response.title and response.title != '' and response.title != request.application.replace('_',' ').title():
        return response.title

    # Next preference is the last breadcrumb's text
    breadcrumb_text = last_breadcrumb_text()
    if breadcrumb_text and breadcrumb_text != '':
        return breadcrumb_text

    # Otherwise use the application name
    return request.application

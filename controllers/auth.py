def user():
    response.title = auth_title()
    attr = {
        '_class': 'nav navbar-nav',
        '_title': response.title}
    response.logo = LI(A(response.title, **attr))
    return dict(form=auth())

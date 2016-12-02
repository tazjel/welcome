def page_not_found():
    response.title = 'Page not found'
    log.warning('%s: %s', response.title, request.vars.request_url)
    return {'message': response.title}

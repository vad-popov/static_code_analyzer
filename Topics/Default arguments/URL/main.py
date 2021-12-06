def create_url(host='localhost', port=443):
    return ''.join(('https://', host, ':', str(port)))

from pyngrok import ngrok


def get_https():
    ngrok.set_auth_token('2GwFlRVGxbzVXFmbO9ug0Z3LQVA_6GuMdEo3uE1XSEEDmy18J')
    http_tunnel = ngrok.connect(80,bind_tls=True)
    return http_tunnel.data['public_url']



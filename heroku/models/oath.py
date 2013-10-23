from . import BaseResource, User


class Grant(BaseResource):
    """Heroku Grant"""

    _strs = ['code', 'id', 'type']
    _ints = ['expires_in']
    _pks = ['id']

    def __init__(self):
        #self.app = None
        super(Grant, self).__init__()

    def __repr__(self):
        return "<grant '{0} {1} {2}'>".format(self.id, self.code, self.expires_in)


class RefreshToken(BaseResource):
    """Heroku RefreshToken"""

    _strs = ['token', 'id']
    _ints = ['expires_in']
    _pks = ['id']

    def __init__(self):
        #self.app = None
        super(RefreshToken, self).__init__()

    def __repr__(self):
        return "<refreshtoken '{0} {1} {2}'>".format(self.id, self.token, self.expires_in)


class AccessToken(BaseResource):
    """Heroku AccessToken"""

    _strs = ['token', 'id']
    _ints = ['expires_in']
    _pks = ['id']

    def __init__(self):
        #self.app = None
        super(AccessToken, self).__init__()

    def __repr__(self):
        return "<AccessToken '{0} {1} {2}'>".format(self.id, self.token, self.expires_in)


#class Client(BaseResource):
    #"""Heroku Client"""
#
    #_strs = ['id', 'name', 'redirect_uri']
    #_pks = ['id']
#
    #def __init__(self):
        #self.app = None
        #super(Client, self).__init__()
#
    #def __repr__(self):
        #return "<Client '{0} {1} {2}'>".format(self.id, self.name, self.redirect_uri)


class OAuthClient(BaseResource):
    """Heroku OAuthClient"""

    _strs = ['id', 'name', 'redirect_uri', 'secret']
    _dates = ['created_at', 'updated_at']
    _bools = ['ignores_delinquent']
    _pks = ['id']

    def __init__(self):
        #self.app = None
        super(OAuthClient, self).__init__()

    def __repr__(self):
        return "<OAuthClient '{0} {1} {2} {3}'>".format(self.id, self.name, self.redirect_uri, self.created_at)

    def delete(self):
        """
        Destroys the current OAuthClient
        """
        r = self._h._http_resource(
            method='DELETE',
            resource=('oauth', 'clients', self.id)
        )
        r.raise_for_status()
        return r.ok

    def update(self, name=None, redirect_uri=None):

        assert (name or redirect_uri)
        payload = {'name': name, 'redirect_uri': redirect_uri}
        r = self._h._http_resource(
            method='PATCH',
            resource=('oauth', 'clients', self.id),
            data=self._h._resource_serialize(payload)
        )

        r.raise_for_status()
        item = self._h._resource_deserialize(r.content.decode("utf-8"))
        return OAuthClient.new_from_dict(item, h=self._h)


class OAuthAuthorization(BaseResource):
    _strs = ['id']
    _dates = ['created_at', 'updated_at']
    _map = {'grant': Grant, 'refresh_token': RefreshToken, 'access_token': AccessToken, 'client': OAuthClient}
    _pks = ['id']
    order_by = 'id'

    def __init__(self):
        #self.app = None
        super(OAuthAuthorization, self).__init__()

    def __repr__(self):
        return "<OAuthAuthorization '{0} {1} {2}'>\n".format(self.id, self.created_at, self.client.id)

    def delete(self):
        """
        Destroys the current OAuthAuthorization
        """
        r = self._h._http_resource(
            method='DELETE',
            resource=('oauth', 'authorizations', self.id)
        )
        r.raise_for_status()
        return r.ok


class OAuthToken(BaseResource):
    _strs = ['id']
    _dates = ['created_at', 'updated_at']
    _map = {
                'grant': Grant,
                'refresh_token': RefreshToken,
                'access_token': AccessToken,
                'client': OAuthClient,
                'authorization': OAuthAuthorization,
                'user': User
        }
    _pks = ['id']
    order_by = 'id'

    def __init__(self):
        #self.app = None
        super(OAuthToken, self).__init__()

    def __repr__(self):
        return "<OAuthToken '{0} {1} {2} {3}'>\n".format(self.id, self.created_at, self.user.id, self.grant.type)


class Session(BaseResource):
    _strs = ['id']
    _pks = ['id']
    order_by = 'id'

    def __init__(self):
        #self.app = None
        super(Session, self).__init__()

    def __repr__(self):
        return "<Session '{0}'>\n".format(self.id)

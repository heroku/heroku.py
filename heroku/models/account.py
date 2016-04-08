from baseresource import BaseResource


class Account(BaseResource):

    _strs = ['email', 'id']
    _bools = ['allow_tracking', 'beta', 'confirmed', 'verified']
    _pks = ['id']
    _dates = ['confirmed_at', 'created_at', 'last_login', 'updated_at']

    def __repr__(self):
        return "<account '{0}'>".format(self.email)

# -*- coding: utf-8 -*-
"""
werkzeug.contrib.authdigest
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The authdigest module contains classes to support
digest authentication compliant with RFC 2617.


Usage
=====

::

from werkzeug.contrib.authdigest import RealmDigestDB

realmDigest = RealmDigestDB('test-realm')
realmDigest.add_user('admin', 'test')

def protectedResource(environ, start_reponse):
request = Request(environ)
if not realmDigest.isAuthenticated(request):
return realmDigest.challenge()

return get_protected_response(request)

:copyright: (c) 2010 by the Werkzeug Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This code was modified by the Avencall company.
Modification:
- access to a custom database to retrieve passwords
"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from xivo_dao.accesswebservice_dao import get_password
import hashlib
import os
import weakref
import werkzeug

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Realm Digest Credentials Database
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class RealmDigestDB(object):
    """Database mapping user to hashed password.

Passwords are hashed using realm key, and specified
digest algorithm.

:param realm: string identifing the hashing realm
:param algorthm: string identifying hash algorithm to use,
default is 'md5'
"""

    def __init__(self, realm, algorithm = 'md5'):
        self.realm = realm
        self.alg = self.newAlgorithm(algorithm)
        self.db = self.newDB()

    @property
    def algorithm(self):
        return self.alg.algorithm

    def toDict(self):
        r = {'cfg': {'algorithm': self.alg.algorithm,
                'realm': self.realm},
            'db': self.db, }
        return r

    def toJson(self, **kw):
        import json
        kw.setdefault('sort_keys', True)
        kw.setdefault('indent', 2)
        return json.dumps(self.toDict(), **kw)

    def del_user(self, user):
        del self.db[user]

    def __contains__(self, user):
        return user in self.db

    def __getitem__(self, user):
        passwd = self.db.get(user)
        return self.alg.hashPassword(user, self.realm, passwd)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def newDB(self):
        return DbAccessClass()

    def newAlgorithm(self, algorithm):
        return DigestAuthentication(algorithm)

    def isAuthenticated(self, request, **kw):
        authResult = AuthenticationResult(self)
        request.authentication = authResult

        authorization = request.authorization
        if authorization is None or authorization.response is None:
            return authResult.deny('initial', None)
        authorization.result = authResult

        hashPass = self[authorization.username]
        if hashPass is None:
            return authResult.deny('unknown_user')
        elif not self.alg.verify(authorization, hashPass, request.method, **kw):
            return authResult.deny('invalid_password')
        else:
            return authResult.approve('success')

    challenge_class = werkzeug.Response

    def challenge(self, response = None, status = 401):
        try:
            authReq = response.www_authenticate
        except AttributeError:
            response = self.challenge_class(response, status)
            authReq = response.www_authenticate
        else:
            if isinstance(status, (int, long)):
                response.status_code = status
            else: response.status = status

        authReq.set_digest(self.realm, os.urandom(8).encode('hex'))
        return response


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Authentication Result
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AuthenticationResult(object):
    """Authentication Result object

Created by RealmDigestDB.isAuthenticated to operate as a boolean result,
and storage of authentication information."""

    authenticated = None
    reason = None
    status = 500

    def __init__(self, authDB):
        self.realmDigest = weakref.ref(authDB)

    def __repr__(self):
        return '<authenticated: %r reason: %r>' % (
            self.authenticated, self.reason)
    def __nonzero__(self):
        return bool(self.authenticated)

    def deny(self, reason, authenticated = False):
        if bool(authenticated):
            raise ValueError("Denied authenticated parameter must evaluate as False")
        self.authenticated = authenticated
        self.reason = reason
        self.status = 401
        return self

    def approve(self, reason, authenticated = True):
        if not bool(authenticated):
            raise ValueError("Approved authenticated parameter must evaluate as True")
        self.authenticated = authenticated
        self.reason = reason
        self.status = 200
        return self

    def challenge(self, response = None, force = False):
        if force or not self:
            return self.realmDigest().challenge(response, self.status)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Digest Authentication Algorithm
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class DigestAuthentication(object):
    """Digest Authentication implementation.

references:
"HTTP Authentication: Basic and Digest Access Authentication". RFC 2617.
http://tools.ietf.org/html/rfc2617

"Digest access authentication"
http://en.wikipedia.org/wiki/Digest_access_authentication
"""

    def __init__(self, algorithm = 'md5'):
        self.algorithm = algorithm.lower()
        self.H = self.hashAlgorithms[self.algorithm]

    def verify(self, authorization, hashPass = None, method = 'GET', **kw):
        reqResponse = self.digest(authorization, hashPass, method, **kw)
        if reqResponse:
            return (authorization.response.lower() == reqResponse.lower())

    def digest(self, authorization, hashPass = None, method = 'GET', **kw):
        if authorization is None:
            return None

        if hashPass is None:
            hA1 = self._compute_hA1(authorization, kw['password'])
        else: hA1 = hashPass

        hA2 = self._compute_hA2(authorization, method)

        if 'auth' in authorization.qop:
            res = self._compute_qop_auth(authorization, hA1, hA2)
        elif not authorization.qop:
            res = self._compute_qop_empty(authorization, hA1, hA2)
        else:
            raise ValueError("Unsupported qop: %r" % (authorization.qop,))
        return res

    def hashPassword(self, username, realm, password):
        return self.H(username, realm, password)

    def _compute_hA1(self, auth, password = None):
        return self.hashPassword(auth.username, auth.realm, password or auth.password)
    def _compute_hA2(self, auth, method = 'GET'):
        return self.H(method, auth.uri)
    def _compute_qop_auth(self, auth, hA1, hA2):
        return self.H(hA1, auth.nonce, auth.nc, auth.cnonce, auth.qop, hA2)
    def _compute_qop_empty(self, auth, hA1, hA2):
        return self.H(hA1, auth.nonce, hA2)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    hashAlgorithms = {}

    @classmethod
    def addDigestHashAlg(klass, key, hashObj):
        key = key.lower()
        def H(*args):
            x = ':'.join(map(str, args))
            return hashObj(x).hexdigest()

        H.__name__ = "H_" + key
        klass.hashAlgorithms[key] = H
        return H

DigestAuthentication.addDigestHashAlg('md5', hashlib.md5)
DigestAuthentication.addDigestHashAlg('sha', hashlib.sha1)


class DbAccessClass():

    def __init__(self):
        pass

    def get(self, user):
        return get_password(user)
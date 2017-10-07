##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import itertools
import os
import json
import urllib
import urllib2

from pyprelude.util import unpack_args

def _parse_args(*args):
    return list(filter(
        lambda x: len(x) > 0,
        itertools.chain(*map(
            lambda x: x.split("/"),
            unpack_args(*args)))))

_API_STORAGE_PATH = _parse_args("api/storage")

class _Item(object):
    def __init__(self, repo, *args):
        self._repo = repo
        self._paths = _parse_args(*args)
        self._api_url = self._repo.api_url(*args)
        self._download_url = self._repo.download_url(*args)
        self._obj = None
        self._files = None
        self._folders = None

    def invalidate(self):
        self._obj = None

    @property
    def api_url(self): return self._api_url

    @property
    def download_url(self): return self._download_url

    @property
    def files(self):
        self._ensure()
        return self._files

    @property
    def folders(self):
        self._ensure()
        return self._folders

    def _ensure(self):
        if self._obj is None:
            self._obj = self._do_request()
            self._files = map(
                lambda o: self._repo.fetch(self._paths + [o["uri"]]),
                filter(lambda o: not o["folder"], self._obj["children"]))
            self._folders = map(
                lambda o: self._repo.fetch(self._paths + [o["uri"]]),
                filter(lambda o: o["folder"], self._obj["children"]))

    def _do_request(self, query=None, method="GET", allow_not_found=False, decode_json=True):
        api_url = self._repo.api_url(self._paths) + ("" if query is None else query)
        request = urllib2.Request(api_url)
        request.get_method = lambda: method
        request.add_header("X-JFrog-Art-Api", self._repo.api_key)
        opener = urllib2.build_opener(urllib2.HTTPHandler)

        if allow_not_found:
            try:
                response = opener.open(request)
            except urllib2.HTTPError as e:
                if e.code != 404:
                    raise e
                return
        else:
            response = opener.open(request)

        s = response.read()
        return json.loads(s) if decode_json else s

class ArtifactoryRepo(object):
    def __init__(self, api_key, url):
        self._api_key = api_key
        self._url = url.strip("/")

    @property
    def api_key(self): return self._api_key

    def api_url(self, *args):
        return "/".join([self._url] + _API_STORAGE_PATH + _parse_args(*args))

    def download_url(self, *args):
        return "/".join([self._url] + _parse_args(*args))

    def fetch(self, *args):
        return _Item(self, *args)

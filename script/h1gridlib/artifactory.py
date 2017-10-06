##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import os
import json
import urllib
import urllib2

from pyprelude.util import unpack_args

class ArtifactoryItem(object):
    def __init__(self, component_info, *args):
        self._component_info = component_info
        self._paths = map(lambda x: x.strip("/"), unpack_args(*args))
        self._pretty_path = "/" if len(self._paths) == 0 else "/".join(self._paths)
        self._api_url = self._component_info.api_url(self._paths)
        self._download_url = self._component_info.download_url(self._paths)
        self._obj = None
        self._files = None
        self._folders = None

    def invalidate(self):
        self._obj = None

    @property
    def paths(self): return list(self._paths)

    @property
    def pretty_path(self): return self._pretty_path

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
                lambda o: ArtifactoryItem(self._component_info, self._paths + [o["uri"]]),
                filter(lambda o: not o["folder"], self._obj["children"]))
            self._folders = map(
                lambda o: ArtifactoryItem(self._component_info, self._paths + [o["uri"]]),
                filter(lambda o: o["folder"], self._obj["children"]))

    def _do_request(self, query=None, method="GET", allow_not_found=False, decode_json=True):
        api_url = self._component_info.api_url(self._paths) + ("" if query is None else query)
        request = urllib2.Request(api_url)
        request.get_method = lambda: method
        request.add_header("X-JFrog-Art-Api", self._component_info.api_key)
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

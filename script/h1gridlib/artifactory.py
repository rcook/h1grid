##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

import os
import json
import re
import urllib
import urllib2

from pyprelude.util import unpack_args

_PROPERTY_RE = re.compile("([{}])".format(re.escape(",\\|=")))

def _encode(s):
    return urllib.quote_plus(_PROPERTY_RE.sub("\\\\\\1", str(s)))

def _encode_properties(properties):
    return "|".join([_encode(key) + "=" + _encode(value) for key, value in properties])

def _make_properties_query(*args):
    q = "?properties"
    arg_count = len(args)
    if arg_count == 0:
        result_q = q
    elif arg_count == 1:
        arg = args[0]
        if isinstance(arg, list):
            result_q = q + "=" + _encode_properties(arg)
        else:
            result_q = q + "=" + _encode(arg)
    elif arg_count == 2:
        result_q = q + "=" + _encode_properties([args])
    else:
        raise ValueError("Invalid arguments")

    return result_q

class PackageMetadata(object):
    def __init__(self, branch, version, base_name):
        self._branch = branch
        self._version = version
        self._base_name = base_name

    @property
    def branch(self): return self._branch

    @property
    def version(self): return self._version

    @property
    def base_name(self): return self._base_name

class ArtifactoryItem(object):
    def __init__(self, component_info, *args):
        self._component_info = component_info
        self._paths = map(lambda x: x.strip("/"), unpack_args(*args))
        self._real_api_url = None
        self._download_url = None
        self._package_metadata = None

    @property
    def paths(self): return self._paths # TODO: Breaks immutability

    @property
    def real_api_url(self):
        if self._real_api_url is None:
            self._real_api_url = self._component_info.real_api_url(self._paths)

        return self._real_api_url

    @property
    def download_url(self):
        if self._download_url is None:
            self._download_url = self._component_info.download_url(self._paths)

        return self._download_url

    @property
    def package_metadata(self):
        if self._package_metadata is None:
            if len(self._paths) != 3:
                raise RuntimeError("Not a valid package")

            branch = self._paths[0]
            version = self._paths[1]
            base_name, ext = os.path.splitext(self._paths[2])
            if ext != ".zip" and ext != ".tgz":
                raise RuntimeError("Package must be a .zip or .tgz file")

            self._package_metadata = PackageMetadata(branch, version, base_name)

        return self._package_metadata

    def exists(self):
        try:
            self._do_request()
            return True
        except urllib2.HTTPError as e:
            if e.code != 404:
                raise
            return False

    def get_files(self):
        obj = self._do_request(query="?list&listFolders=0")
        result = map(
            lambda o: ArtifactoryItem(self._component_info, self._paths + [o["uri"]]),
            filter(lambda o: not o["folder"], obj["files"]))
        return result

    def get_folders(self):
        obj = self._do_request("?list&listFolders=1")
        result = map(
            lambda o: ArtifactoryItem(self._component_info, self._paths + [o["uri"]]),
            filter(lambda o: o["folder"], obj["files"]))
        return result

    def get_properties(self):
        obj = self._do_request(
            query=_make_properties_query(),
            allow_not_found=True)
        return {} if obj is None else obj["properties"]

    def set_properties(self, *args):
        self._do_request(
            query=_make_properties_query(*args),
            method="PUT",
            decode_json=False)

    def _do_request(self, query=None, method="GET", allow_not_found=False, decode_json=True):
        api_url = self._component_info.real_api_url(self._paths) + ("" if query is None else query)
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

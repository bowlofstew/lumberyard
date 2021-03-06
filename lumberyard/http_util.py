# -*- coding: utf-8 -*-
"""
http_util.py

utility functions for connecting with nimbus.io via HTTP
"""
import hashlib
import hmac
import os
import time
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

meta_prefix = "__nimbus_io__"
# TODO ssl
_service_domain = os.environ.get("NIMBUS_IO_SERVICE_DOMAIN", 'nimbus.io')
_host_port = int(os.environ.get("NIMBUS_IO_SERVICE_PORT", "443"))
_default_collection_prefix = "dd"
_reserved_collection_prefix = "rr"

def compute_default_collection_name(username):
    """
    return the name of this customer's default collection
    """
    return "-".join([_default_collection_prefix, username])

def compute_reserved_collection_name(username, collection_name):
    """
    return the decorated name of a reserved collection name
    """
    return "-".join([_reserved_collection_prefix, username, collection_name])

def compute_collection_hostname(collection_name):
    """
    return the DNS hostname for this collection
    """
    return ".".join([collection_name, compute_default_hostname()])

def compute_default_hostname():
    """
    return the DNS hostname for the default collection
    """
    hostname_with_port = ":".join([_service_domain, str(_host_port)])
    return hostname_with_port

def compute_reserved_hostname(username, collection_name):
    """
    return the DNS hostname for one of this customer's reserved collection
    """
    return compute_collection_hostname(
        compute_reserved_collection_name(username, collection_name)
    )

def compute_authentication_string(
    auth_key_id,  auth_key, user_name,  method, timestamp, uri
):
    """
    auth_key_id
        the id of the authentication key

    auth_key
        authentication_key

    user_name
        name of a valid nimbus.io user

    method
        one of GET, POST, DELETE, HEAD
        This must be the mehtod used in the request

    timestamp
        the value of the HTTP header ``x-nimbus-io-timestamp``

    uri
        the REST command for the request

    Compute the authentication hmac that will be sent to the server
    """
    message = "\n".join([user_name, method, str(timestamp), uri])
    hmac_object = hmac.new(
        auth_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    )
    return "NIMBUS.IO {0}:{1}".format(auth_key_id, hmac_object.hexdigest())

def compute_uri(sub_dir, key=None, **kwargs):
    """
    Create the REST URI sent to the server
    """    
    # do not use os.path here, we're not dealing with a real path
    # but os.path tries to fix things

    if sub_dir[0] != os.sep:
        path = "".join([os.sep, sub_dir, ])
    else:
        path = sub_dir

    if key is not None:
        path = os.sep.join([path, key, ])

    # filter out params set to None
    params = [(k, v) for k, v in kwargs.items() if v is not None]

    if len(params) > 0:
        if "?" in path:
            path = "&".join([path, urlencode(params), ])
        else:
            path = "?".join([path, urlencode(params), ])

    return path

def current_timestamp():
    """
    return the current time as an integer
    """
    return int(time.time())



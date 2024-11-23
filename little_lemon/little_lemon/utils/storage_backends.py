"""
Module: little-lemon.utils.storage_backends

This module contains custom classes for storing static, public media, and private media files in AWS S3.

Classes:
- StaticStorage: Used for storing static files in BunnyCDn.


"""

from django_bunny.storage import BunnyStorage


class StaticStorage(BunnyStorage):
    location = "staticfiles"
    default_acl = "public-read"

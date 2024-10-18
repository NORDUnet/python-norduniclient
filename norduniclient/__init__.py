# -*- coding: utf-8 -*-

from __future__ import absolute_import
from norduniclient.core import *

__author__ = 'lundberg'


# Init as singleton for easy use in Django
# You can use it like this:
# from norduniclient import graphdb as db
# get_node(db.manager, 'node_id*)
graphdb = GraphDB.get_instance()

neo4jdb = graphdb.manager  # Works as the old neo4jdb

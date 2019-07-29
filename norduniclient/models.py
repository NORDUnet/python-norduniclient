# -*- coding: utf-8 -*-

from functools import total_ordering
from collections import defaultdict
try:
    # Python 2
    import core
except ImportError:  # Fix circular import in python 2 vs python 3
    # Python 3
    from norduniclient import core

import six

__author__ = 'lundberg'


@total_ordering
class BaseRelationshipModel(object):

    def __init__(self, manager):
        self.manager = manager
        self.id = None
        self.type = None
        self.data = None
        self.start = None
        self.end = None

    def __str__(self):
        return u'({start})-[{id}:{type}{data}]->({end}) in database {db}.'.format(
            start=self.start['handle_id'], type=self.type, id=self.id, data=self.data, end=self.end['handle_id'],
            db=self.manager.uri
        )

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id

    def __repr__(self):
        return u'<{c} id:{id} in {db}>'.format(c=self.__class__.__name__, id=self.id, db=self.manager.uri)

    def load(self, relationship_bundle):
        self.id = relationship_bundle.get('id')
        self.type = relationship_bundle.get('type')
        self.data = relationship_bundle.get('data', {})
        self.start = relationship_bundle.get('start')
        self.end = relationship_bundle.get('end')
        return self

    def delete(self):
        core.delete_relationship(self.manager, self.id)


@total_ordering
class BaseNodeModel(object):

    def __init__(self, manager):
        self.manager = manager
        self.meta_type = None
        self.labels = None
        self.data = None

    def __str__(self):
        labels = ':'.join(self.labels)
        return u'(node:{meta_type}:{labels} {data}) in database {db}.'.format(
            meta_type=self.meta_type, labels=labels, data=self.data, db=self.manager.uri
        )

    def __eq__(self, other):
        return self.handle_id == other.handle_id

    def __lt__(self, other):
        return self.handle_id < other.handle_id

    def __repr__(self):
        return u'<{c} handle_id:{handle_id} in {db}>'.format(c=self.__class__.__name__, handle_id=self.handle_id,
                                                             db=self.manager.uri)

    def _get_handle_id(self):
        return self.data.get('handle_id')
    handle_id = property(_get_handle_id)

    def _incoming(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r]-(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)
    incoming = property(_incoming)

    def _outgoing(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r]->(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)
    outgoing = property(_outgoing)

    def _relationships(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r]-(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)
    relationships = property(_relationships)

    def _basic_read_query_to_dict(self, query, **kwargs):
        d = defaultdict(list)
        with self.manager.session as s:
            kwargs['handle_id'] = self.handle_id
            result = s.run(query, kwargs)
            for record in result:
                relationship = record['r']
                node = record['node']
                key = relationship.type
                if 'key' in record.keys():
                    key = record['key']
                d[key].append({
                    'relationship_id': relationship.id,
                    'relationship': relationship,
                    'node': core.get_node_model(self.manager, node=node)
                })
        d.default_factory = None
        return d

    def _basic_write_query_to_dict(self, query, **kwargs):
        d = defaultdict(list)
        with self.manager.session as s:
            kwargs['handle_id'] = self.handle_id
            result = s.run(query, kwargs)
            for record in result:
                created = record['created']
                relationship = record['r']
                node = record['node']
                key = relationship.type
                if 'key' in record.keys():
                    key = record['key']
                d[key].append({
                    'created': created,
                    'relationship_id': relationship.id,
                    'relationship': relationship,
                    'node': core.get_node_model(self.manager, node=node)
                })
        d.default_factory = None
        return d

    def load(self, node_bundle):
        self.meta_type = node_bundle.get('meta_type')
        self.labels = node_bundle.get('labels')
        self.data = node_bundle.get('data')
        return self

    def add_label(self, label):
        q = """
            MATCH (n:Node {{handle_id: {{handle_id}}}})
            SET n:{label}
            RETURN n
            """.format(label=label)
        with self.manager.session as s:
            node = s.run(q, {'handle_id': self.handle_id}).single()['n']
        return self.reload(node=node)

    def remove_label(self, label):
        q = """
            MATCH (n:Node {{handle_id: {{handle_id}}}})
            REMOVE n:{label}
            RETURN n
            """.format(label=label)
        with self.manager.session as s:
            node = s.run(q, {'handle_id': self.handle_id}).single()['n']
        return self.reload(node=node)

    def change_meta_type(self, meta_type):
        if meta_type not in core.META_TYPES:
            raise core.exceptions.MetaLabelNamingError(meta_type)
        if meta_type == self.meta_type:
            return self
        model = self.remove_label(self.meta_type)
        return model.add_label(meta_type)

    def switch_type(self, old_type, new_type):
        if old_type == new_type:
            return self
        model = self.remove_label(old_type)
        return model.add_label(new_type)

    def delete(self):
        core.delete_node(self.manager, self.handle_id)

    def reload(self, node=None):
        return core.get_node_model(self.manager, self.handle_id, node=node)

    def add_property(self, property, value):
        if isinstance(value, six.string_types):
            value = "'{}'".format(value)

        q = """
            MATCH (n:Node {{handle_id: {{handle_id}}}})
            SET n.{property} = {value}
            RETURN n
            """.format(property=property, value=value)
        with self.manager.session as s:
            node = s.run(q, {'handle_id': self.handle_id}).single()['n']
        return self.reload(node=node)

    def remove_property(self, property):
        q = """
            MATCH (n:Node {{handle_id: {{handle_id}}}})
            REMOVE n.{property}
            RETURN n
            """.format(property=property)
        with self.manager.session as s:
            node = s.run(q, {'handle_id': self.handle_id}).single()['n']
        return self.reload(node=node)


class CommonQueries(BaseNodeModel):

    def get_location_path(self):
        return {'location_path': []}

    def get_placement_path(self):
        return {'placement_path': []}

    def get_location(self):
        return {}

    def get_child_form_data(self, node_type):
        type_filter = ''
        if node_type:
            type_filter = 'and (child):{node_type}'.format(node_type=node_type)
        q = """
            MATCH (parent:Node {{handle_id:{{handle_id}}}})
            MATCH (parent)--(child)
            WHERE (parent)-[:Has]->(child) or (parent)<-[:Located_in|Part_of]-(child) {type_filter}
            RETURN child.handle_id as handle_id, labels(child) as labels, child.name as name,
                   child.description as description
            """.format(type_filter=type_filter)
        return core.query_to_list(self.manager, q, handle_id=self.handle_id)

    def get_relations(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Owns|Uses|Provides|Responsible_for|Works_for|Parent_of|Member_of|Uses_a]-(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)

    def get_dependencies(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Depends_on]->(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)

    def get_dependents(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Depends_on]-(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)

    def get_dependent_as_types(self):
        q = """
            MATCH (node:Node {handle_id: {handle_id}})
            OPTIONAL MATCH (node)<-[:Depends_on]-(d)
            WITH node, collect(DISTINCT d) as direct
            MATCH (node)<-[:Part_of|Depends_on*1..20]-(dep)
            WITH direct, collect(DISTINCT dep) as deps
            WITH direct, deps, filter(n in deps WHERE n:Service) as services
            WITH direct, deps, services, filter(n in deps WHERE n:Optical_Path) as paths
            WITH direct, deps, services, paths, filter(n in deps WHERE n:Optical_Multiplex_Section) as oms
            WITH direct, deps, services, paths, oms, filter(n in deps WHERE n:Optical_Link) as links
            RETURN direct, services, paths, oms, links
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)

    def get_dependencies_as_types(self):
        q = """
            MATCH (node:Node {handle_id: {handle_id}})
            OPTIONAL MATCH (node)-[:Depends_on]->(d)
            WITH node, collect(DISTINCT d) as direct
            MATCH (node)-[:Depends_on*1..20]->(dep)
            WITH node, direct, collect(DISTINCT dep) as deps
            WITH node, direct, deps, filter(n in deps WHERE n:Service) as services
            WITH node, direct, deps, services, filter(n in deps WHERE n:Optical_Path) as paths
            WITH node, direct, deps, services, paths, filter(n in deps WHERE n:Optical_Multiplex_Section) as oms
            WITH node, direct, deps, services, paths, oms, filter(n in deps WHERE n:Optical_Link) as links
            WITH node, direct, services, paths, oms, links
            OPTIONAL MATCH (node)-[:Depends_on*1..20]->()-[:Connected_to*1..50]-(cable)
            RETURN direct, services, paths, oms, links, filter(n in collect(DISTINCT cable) WHERE n:Cable) as cables
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)

    def get_ports(self):
        q = """
            MATCH (node:Node {handle_id: {handle_id}})-[r:Connected_to|Depends_on]-(port:Port)
            WITH port, r
            OPTIONAL MATCH p=(port)<-[:Has*1..]-(parent)
            RETURN port, r as relationship, LAST(nodes(p)) as parent
            ORDER BY parent.name
            """
        return core.query_to_list(self.manager, q, handle_id=self.handle_id)

class LogicalModel(CommonQueries):

    def get_part_of(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Part_of]->(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)

    def set_user(self, user_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (user:Node {handle_id: {user_handle_id}})
            WITH n, user, NOT EXISTS((n)<-[:Uses]-(user)) as created
            MERGE (n)<-[r:Uses]-(user)
            RETURN created, r, user as node
            """
        return self._basic_write_query_to_dict(q, user_handle_id=user_handle_id)

    def set_provider(self, provider_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (provider:Node {handle_id: {provider_handle_id}})
            WITH n, provider, NOT EXISTS((n)<-[:Provides]-(provider)) as created
            MERGE (n)<-[r:Provides]-(provider)
            RETURN created, r, provider as node
            """
        return self._basic_write_query_to_dict(q, provider_handle_id=provider_handle_id)

    def set_dependency(self, dependency_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (dependency:Node {handle_id: {dependency_handle_id}})
            WITH n, dependency, NOT EXISTS((n)-[:Depends_on]->(dependency)) as created
            MERGE (n)-[r:Depends_on]->(dependency)
            RETURN created, r, dependency as node
            """
        return self._basic_write_query_to_dict(q, dependency_handle_id=dependency_handle_id)

    def get_connections(self):  # Logical versions of physical things can't have physical connections
        return []

    # TODO: Create a method that complains if any relationships that breaks the model exists


class PhysicalModel(CommonQueries):

    def get_location(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Located_in]->(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)

    def get_location_path(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[:Located_in]->(r)
            MATCH p=()-[:Has*0..20]->(r)
            WITH COLLECT(nodes(p)) as paths, MAX(length(nodes(p))) AS maxLength
            WITH FILTER(path IN paths WHERE length(path)=maxLength) AS longestPaths
            UNWIND(longestPaths) as location_path
            RETURN location_path
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)

    def get_placement_path(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[:Has]-(parent)
            OPTIONAL MATCH p=()-[:Has*0..20]->(parent)
            WITH COLLECT(nodes(p)) as paths, MAX(length(nodes(p))) AS maxLength
            WITH FILTER(path IN paths WHERE length(path)=maxLength) AS longestPaths
            UNWIND(longestPaths) as placement_path
            RETURN placement_path
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)

    def set_owner(self, owner_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (owner:Node {handle_id: {owner_handle_id}})
            WITH n, owner, NOT EXISTS((n)<-[:Owns]-(owner)) as created
            MERGE (n)<-[r:Owns]-(owner)
            RETURN created, r, owner as node
            """
        return self._basic_write_query_to_dict(q, owner_handle_id=owner_handle_id)

    def set_provider(self, provider_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (provider:Node {handle_id: {provider_handle_id}})
            WITH n, provider, NOT EXISTS((n)<-[:Provides]-(provider)) as created
            MERGE (n)<-[r:Provides]-(provider)
            RETURN created, r, provider as node
            """
        return self._basic_write_query_to_dict(q, provider_handle_id=provider_handle_id)

    def set_location(self, location_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (location:Node {handle_id: {location_handle_id}})
            WITH n, location, NOT EXISTS((n)-[:Located_in]->(location)) as created
            MERGE (n)-[r:Located_in]->(location)
            RETURN created, r, location as node
            """
        return self._basic_write_query_to_dict(q, location_handle_id=location_handle_id)

    def get_has(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Has]->(part:Physical)
            RETURN r, part as node
            """
        return self._basic_read_query_to_dict(q)

    def set_has(self, has_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (part:Node {handle_id: {has_handle_id}})
            WITH n, part, NOT EXISTS((n)-[:Has]->(part)) as created
            MERGE (n)-[r:Has]->(part)
            RETURN created, r, part as node
            """
        return self._basic_write_query_to_dict(q, has_handle_id=has_handle_id)

    def get_part_of(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Part_of]-(part:Logical)
            RETURN r, part as node
            """
        return self._basic_read_query_to_dict(q)

    def set_part_of(self, part_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (part:Node:Logical {handle_id: {part_handle_id}})
            WITH n, part, NOT EXISTS((n)<-[:Part_of]-(part)) as created
            MERGE (n)<-[r:Part_of]-(part)
            RETURN created, r, part as node
            """
        return self._basic_write_query_to_dict(q, part_handle_id=part_handle_id)

    def get_parent(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Has]-(parent)
            RETURN r, parent as node
            """
        return self._basic_read_query_to_dict(q)

    # TODO: Create a method that complains if any relationships that breaks the model exists


class LocationModel(CommonQueries):

    def get_location_path(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[:Has]-(r)
            MATCH p=()-[:Has*0..20]->(r)
            WITH COLLECT(nodes(p)) as paths, MAX(length(nodes(p))) AS maxLength
            WITH FILTER(path IN paths WHERE length(path)=maxLength) AS longestPaths
            UNWIND(longestPaths) as location_path
            RETURN location_path
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)

    def get_parent(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Has]-(parent)
            RETURN r, parent as node
            """
        return self._basic_read_query_to_dict(q)

    def get_located_in(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Located_in]-(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)

    def get_has(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Has]->(node:Location)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)

    def set_has(self, has_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (part:Node {handle_id: {has_handle_id}})
            WITH n, part, NOT EXISTS((n)-[:Has]->(part)) as created
            MERGE (n)-[r:Has]->(part)
            RETURN created, r, part as node
            """
        return self._basic_write_query_to_dict(q, has_handle_id=has_handle_id)

    def set_responsible_for(self, owner_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (owner:Node {handle_id: {owner_handle_id}})
            WITH n, owner, NOT EXISTS((n)<-[:Responsible_for]-(owner)) as created
            MERGE (n)<-[r:Responsible_for]-(owner)
            RETURN created, r, owner as node
            """
        return self._basic_write_query_to_dict(q, owner_handle_id=owner_handle_id)


class RelationModel(CommonQueries):

    def with_same_name(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (other:Node:Relation {name: {name}})
            WHERE other.handle_id <> n.handle_id
            RETURN COLLECT(other.handle_id) as ids
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id, name=self.data.get('name'))

    def get_uses(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Uses]->(usable)
            RETURN r, usable as node
            """
        return self._basic_read_query_to_dict(q)

    def get_provides(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Provides]->(usable)
            RETURN r, usable as node
            """
        return self._basic_read_query_to_dict(q)

    def get_owns(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Owns]->(usable)
            RETURN r, usable as node
            """
        return self._basic_read_query_to_dict(q)

    def get_responsible_for(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Responsible_for]->(usable)
            RETURN r, usable as node
            """
        return self._basic_read_query_to_dict(q)


class EquipmentModel(PhysicalModel):

    def get_ports(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Has]->(port:Port)
            RETURN r, port as node
            """
        return self._basic_read_query_to_dict(q)

    def get_port(self, port_name):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Has]->(port:Port)
            WHERE port.name = {port_name}
            RETURN r, port as node
            """
        return self._basic_read_query_to_dict(q, port_name=port_name)

    def get_dependent_as_types(self):
        # The + [null] is to handle both dep lists being emtpy since UNWIND gives 0 rows on unwind
        q = """
            MATCH (node:Node {handle_id: {handle_id}})
            OPTIONAL MATCH (node)<-[:Depends_on]-(d)
            WITH node, collect(DISTINCT d) as direct
            OPTIONAL MATCH (node)-[:Has*1..20]->()<-[:Part_of|Depends_on*1..20]-(dep)
            OPTIONAL MATCH (node)-[:Has*1..20]->()<-[:Connected_to]-()-[:Connected_to]->()<-[:Depends_on*1..20]-(cable_dep)
            WITH direct, collect(DISTINCT dep) + collect(DISTINCT cable_dep) + direct as coll
            UNWIND coll AS x
            WITH direct, collect(DISTINCT x) as deps
            WITH direct, deps, filter(n in deps WHERE n:Service) as services
            WITH direct, deps, services, filter(n in deps WHERE n:Optical_Path) as paths
            WITH direct, deps, services, paths, filter(n in deps WHERE n:Optical_Multiplex_Section) as oms
            WITH direct, deps, services, paths, oms, filter(n in deps WHERE n:Optical_Link) as links
            RETURN direct, services, paths, oms, links
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)

    def get_connections(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[:Has*1..10]->(porta:Port)
            OPTIONAL MATCH (porta)<-[r0:Connected_to]-(cable)
            OPTIONAL MATCH (cable)-[r1:Connected_to]->(portb:Port)
            WHERE ID(r1) <> ID(r0)
            OPTIONAL MATCH (portb)<-[:Has*1..10]-(end)
            WITH porta, r0, cable, portb, r1, last(collect(end)) as end
            OPTIONAL MATCH (end)-[:Located_in]->(location)
            OPTIONAL MATCH (location)<-[:Has]-(site)
            RETURN porta, r0, cable, r1, portb, end, location, site
            """
        return core.query_to_list(self.manager, q, handle_id=self.handle_id)


class SubEquipmentModel(PhysicalModel):

    def get_location_path(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[:Has]-(parent)
            OPTIONAL MATCH p=()-[:Has*0..20]->(r)<-[:Located_in]-()-[:Has*0..20]->(parent)
            WITH COLLECT(nodes(p)) as paths, MAX(length(nodes(p))) AS maxLength
            WITH FILTER(path IN paths WHERE length(path)=maxLength) AS longestPaths
            UNWIND(longestPaths) as location_path
            RETURN location_path
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)

    def get_connections(self):
        q = """
            MATCH (porta:Node {handle_id: {handle_id}})<-[r0:Connected_to]-(cable)
            OPTIONAL MATCH (porta)<-[r0:Connected_to]-(cable)-[r1:Connected_to]->(portb)
            OPTIONAL MATCH (portb)<-[:Has*1..10]-(end)
            WITH  porta, r0, cable, portb, r1, last(collect(end)) as end
            OPTIONAL MATCH (end)-[:Located_in]->(location)
            OPTIONAL MATCH (location)<-[:Has]-(site)
            RETURN porta, r0, cable, r1, portb, end, location, site
            """
        return core.query_to_list(self.manager, q, handle_id=self.handle_id)


class HostModel(CommonQueries):

    def get_dependent_as_types(self):  # Does not return Host_Service as a direct dependent
        q = """
            MATCH (node:Node {handle_id: {handle_id}})
            OPTIONAL MATCH (node)<-[:Depends_on]-(d)
            WITH node, filter(n in collect(DISTINCT d) WHERE NOT(n:Host_Service)) as direct
            MATCH (node)<-[:Depends_on*1..20]-(dep)
            WITH direct, collect(DISTINCT dep) as deps
            WITH direct, deps, filter(n in deps WHERE n:Service) as services
            WITH direct, deps, services, filter(n in deps WHERE n:Optical_Path) as paths
            WITH direct, deps, services, paths, filter(n in deps WHERE n:Optical_Multiplex_Section) as oms
            WITH direct, deps, services, paths, oms, filter(n in deps WHERE n:Optical_Link) as links
            RETURN direct, services, paths, oms, links
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)

    def get_host_services(self):
        q = """
            MATCH (host:Node {handle_id: {handle_id}})<-[r:Depends_on]-(service:Host_Service)
            RETURN r, service as node
            """
        return self._basic_read_query_to_dict(q)

    def get_host_service(self, service_handle_id, ip_address, port, protocol):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Depends_on]-(host_service:Node {handle_id: {service_handle_id}})
            WHERE r.ip_address={ip_address} AND r.port={port} AND r.protocol={protocol}
            RETURN r, host_service as node
            """
        return self._basic_read_query_to_dict(q, service_handle_id=service_handle_id, ip_address=ip_address, port=port,
                                              protocol=protocol)

    def set_host_service(self, service_handle_id, ip_address, port, protocol):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (host_service:Node {handle_id: {service_handle_id}})
            CREATE (n)<-[r:Depends_on {ip_address:{ip_address}, port:{port}, protocol:{protocol}}]-(host_service)
            RETURN true as created, r, host_service as node
            """
        return self._basic_write_query_to_dict(q, service_handle_id=service_handle_id, ip_address=ip_address,
                                               port=port, protocol=protocol)


class PhysicalHostModel(HostModel, EquipmentModel):
    pass


class LogicalHostModel(HostModel, LogicalModel):
    pass


class PortModel(SubEquipmentModel):

    def get_units(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Part_of]-(unit:Unit)
            RETURN r, unit as node
            """
        return self._basic_read_query_to_dict(q)

    def get_unit(self, unit_name):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Part_of]-(unit:Unit)
            WHERE unit.name = {unit_name}
            RETURN r, unit as node
            """
        return self._basic_read_query_to_dict(q, unit_name=unit_name)

    def get_connected_to(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Connected_to]-(cable:Cable)
            RETURN r, cable as node
            """
        return self._basic_read_query_to_dict(q)

    def get_connection_path(self):
        q = """
            MATCH (n:Port {handle_id: {handle_id}})-[:Connected_to*0..20]-(port:Port)
            OPTIONAL MATCH path=(port)-[:Connected_to*]-()
            WITH nodes(path) AS parts, length(path) AS len
            ORDER BY len DESC
            LIMIT 1
            UNWIND parts AS part
            OPTIONAL MATCH (part)<-[:Has*1..20]-(parent)
            WHERE NOT (parent)<-[:Has]-()
            RETURN part, parent
            """
        return core.query_to_list(self.manager, q, handle_id=self.handle_id)


class OpticalNodeModel(EquipmentModel):
    pass


class RouterModel(EquipmentModel):

    def get_child_form_data(self, node_type=None):
        if node_type:
            type_filter = ':{node_type}'.format(node_type=node_type)
        else:
            type_filter = ':Port'
        q = """
            MATCH (parent:Node {{handle_id:{{handle_id}}}})
            MATCH (parent)-[:Has*]->(child{type_filter})
            RETURN child.handle_id as handle_id, labels(child) as labels, child.name as name,
                   child.description as description
            ORDER BY child.name
            """.format(type_filter=type_filter)
        return core.query_to_list(self.manager, q, handle_id=self.handle_id)


class PeeringPartnerModel(RelationModel):

    def get_peering_groups(self):
        q = """
            MATCH (host:Node {handle_id: {handle_id}})-[r:Uses]->(group:Peering_Group)
            RETURN r, group as node
            """
        return self._basic_read_query_to_dict(q)

    def get_peering_group(self, group_handle_id, ip_address):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Uses]->(group:Node {handle_id: {group_handle_id}})
            WHERE r.ip_address={ip_address}
            RETURN r, group as node
            """
        return self._basic_read_query_to_dict(q, group_handle_id=group_handle_id, ip_address=ip_address)

    def set_peering_group(self, group_handle_id, ip_address):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (group:Node {handle_id: {group_handle_id}})
            CREATE (n)-[r:Uses {ip_address:{ip_address}}]->(group)
            RETURN true as created, r, group as node
            """
        return self._basic_write_query_to_dict(q, group_handle_id=group_handle_id, ip_address=ip_address)


class PeeringGroupModel(LogicalModel):

    def get_group_dependency(self, dependency_handle_id, ip_address):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[r:Depends_on]->(dependency:Node {handle_id: {dependency_handle_id}})
            WHERE r.ip_address={ip_address}
            RETURN r, dependency as node
            """
        return self._basic_read_query_to_dict(q, dependency_handle_id=dependency_handle_id, ip_address=ip_address)

    def set_group_dependency(self, dependency_handle_id, ip_address):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (dependency:Node {handle_id: {dependency_handle_id}})
            CREATE (n)-[r:Depends_on {ip_address:{ip_address}}]->(dependency)
            RETURN true as created, r, dependency as node
            """
        return self._basic_write_query_to_dict(q, dependency_handle_id=dependency_handle_id, ip_address=ip_address)


class CableModel(PhysicalModel):

    def get_connected_equipment(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[rel:Connected_to]->(port)
            OPTIONAL MATCH (port)<-[:Has*1..10]-(end)
            WITH  rel, port, last(collect(end)) as end
            OPTIONAL MATCH (end)-[:Located_in]->(location)
            OPTIONAL MATCH (location)<-[:Has]-(site)
            RETURN id(rel) as rel_id, rel, port, end, location, site
            ORDER BY end.name, port.name
            """
        return core.query_to_list(self.manager, q, handle_id=self.handle_id)

    def get_dependent_as_types(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[:Connected_to*1..20]-(equip)
            WITH DISTINCT equip
            MATCH (equip)<-[:Part_of|Depends_on*1..10]-(dep)
            WITH collect(DISTINCT dep) as deps
            WITH deps, filter(n in deps WHERE n:Service) as services
            WITH deps, services, filter(n in deps WHERE n:Optical_Path) as paths
            WITH deps, services, paths, filter(n in deps WHERE n:Optical_Multiplex_Section) as oms
            WITH deps, services, paths, oms, filter(n in deps WHERE n:Optical_Link) as links
            RETURN services, paths, oms, links
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)

    def get_services(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})
            MATCH (n)-[:Connected_to*1..20]-(equip)
            WITH equip
            MATCH (equip)<-[:Depends_on*1..10]-(service)
            WHERE service:Service
            WITH distinct service
            OPTIONAL MATCH (service)<-[:Uses]-(user)
            RETURN service, collect(user) as users
            """
        return core.query_to_list(self.manager, q, handle_id=self.handle_id)

    def get_connection_path(self):
        q = """
            MATCH (n:Cable {handle_id: {handle_id}})-[:Connected_to*1..10]-(port:Port)
            OPTIONAL MATCH path=(port)-[:Connected_to*]-()
            WITH nodes(path) AS parts, length(path) AS len
            ORDER BY len DESC
            LIMIT 1
            UNWIND parts AS part
            OPTIONAL MATCH (part)<-[:Has*1..10]-(parent)
            WHERE NOT (parent)<-[:Has]-()
            RETURN part, parent
            """
        return core.query_to_list(self.manager, q, handle_id=self.handle_id)

    def set_connected_to(self, connected_to_handle_id):
        q = """
            MATCH (n:Node {handle_id: {handle_id}}), (part:Node {handle_id: {connected_to_handle_id}})
            WITH n, part, NOT EXISTS((n)-[:Connected_to]->(part)) as created
            MERGE (n)-[r:Connected_to]->(part)
            RETURN created, r, part as node
            """
        return self._basic_write_query_to_dict(q, connected_to_handle_id=connected_to_handle_id)


class UnitModel(LogicalModel):

    def get_placement_path(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[:Part_of]->(parent)
            OPTIONAL MATCH p=()-[:Has*0..20]->(parent)
            WITH COLLECT(nodes(p)) as paths, MAX(length(nodes(p))) AS maxLength
            WITH FILTER(path IN paths WHERE length(path)=maxLength) AS longestPaths
            UNWIND(longestPaths) as placement_path
            RETURN placement_path
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)

    def get_location_path(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})-[:Part_of]->(parent)
            OPTIONAL MATCH p=()-[:Has*0..20]->(r)<-[:Located_in]-()-[:Has*0..20]->(parent)
            WITH COLLECT(nodes(p)) as paths, MAX(length(nodes(p))) AS maxLength
            WITH FILTER(path IN paths WHERE length(path)=maxLength) AS longestPaths
            UNWIND(longestPaths) as location_path
            RETURN location_path
            """
        return core.query_to_dict(self.manager, q, handle_id=self.handle_id)


class ServiceModel(LogicalModel):

    def get_customers(self):
        q = """
            MATCH (n:Node {handle_id: {handle_id}})<-[r:Owns|Uses]-(customer:Customer)
            RETURN "customers" as key, r, customer as node
            """
        return self._basic_read_query_to_dict(q)


class OpticalPathModel(LogicalModel):
    pass


class OpticalMultiplexSection(LogicalModel):
    pass


class OpticalLinkModel(LogicalModel):
    pass


class ExternalEquipmentModel(EquipmentModel):
    pass


class ODFModel(EquipmentModel):
    pass


class OpticalFilterModel(EquipmentModel):
    pass


class SwitchModel(EquipmentModel, HostModel):
    pass


class FirewallModel(EquipmentModel, HostModel):
    pass


class PDUModel(EquipmentModel, HostModel):
    pass


class PICModel(SubEquipmentModel):
    pass


class FPCModel(SubEquipmentModel):
    pass


class CustomerModel(RelationModel):
    pass

class OrganizationModel(RelationModel):
    def set_parent(self, org_handle_id):
        q = """
            MATCH (n:Node:Organization {handle_id: {handle_id}}), (m:Node:Organization {handle_id: {org_handle_id}})
            MERGE (m)-[r:Parent_of]->(n)
            RETURN m as created, r, n as node
            """
        return self._basic_write_query_to_dict(q, org_handle_id=org_handle_id)

    def set_child(self, org_handle_id):
        q = """
            MATCH (n:Node:Organization {handle_id: {handle_id}}), (m:Node:Organization {handle_id: {org_handle_id}})
            MERGE (n)-[r:Parent_of]->(m)
            RETURN m as created, r, n as node
            """
        return self._basic_write_query_to_dict(q, org_handle_id=org_handle_id)

    def add_procedure(self, proc_handle_id):
        q = """
            MATCH (n:Node:Organization {handle_id: {handle_id}}), (m:Node:Procedure {handle_id: {proc_handle_id}})
            MERGE (n)-[r:Uses_a]->(m)
            RETURN m as created, r, n as node
            """
        return self._basic_write_query_to_dict(q, proc_handle_id=proc_handle_id)

    def get_outgoing_relations(self):
        q = """
            MATCH (n:Node:Organization {handle_id: {handle_id}})-[r:Parent|Uses_a]->(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)

    def get_contacts(self):
        q = """
            MATCH (c:Node:Contact)-[:Works_for]->(o:Node:Organization)
            WHERE o.handle_id = {handle_id}
            RETURN DISTINCT c.handle_id as handle_id, c.name as name
            """
        return core.query_to_list(self.manager, q, handle_id=self.handle_id)


class ProviderModel(RelationModel):
    pass


class ContactModel(RelationModel):
    def add_group(self, group_handle_id):
        q = """
            MATCH (n:Node:Contact {handle_id: {handle_id}}), (m:Node:Group {handle_id: {group_handle_id}})
            MERGE (n)-[r:Member_of]->(m)
            RETURN m as created, r, n as node
            """
        return self._basic_write_query_to_dict(q, group_handle_id=group_handle_id)

    def get_outgoing_relations(self):
        q = """
            MATCH (n:Node:Contact {handle_id: {handle_id}})-[r:Works_for|Member_of]->(node)
            RETURN r, node
            """
        return self._basic_read_query_to_dict(q)

class GroupModel(LogicalModel):
    def add_member(self, contact_handle_id):
        q = """
            MATCH (n:Node:Contact {handle_id: {contact_handle_id}}), (m:Node:Group {handle_id: {handle_id}})
            MERGE (n)-[r:Member_of]->(m)
            RETURN m as created, r, n as node
            """
        return self._basic_write_query_to_dict(q, contact_handle_id=contact_handle_id)


class RoleRelationship(BaseRelationshipModel):
    RELATION_NAME = 'Works_for'
    DEFAULT_ROLE_NAME = 'Employee'

    def __init__(self, manager):
        super(RoleRelationship, self).__init__(manager)
        self.type = RoleRelationship.RELATION_NAME
        self.name = None
        self.handle_id = None

    def load(self, relationship_bundle):
        super(RoleRelationship, self).load(relationship_bundle)
        self.type = RoleRelationship.RELATION_NAME
        self.name = self.data.get('name', None)
        self.handle_id = self.data.get('handle_id', None)

        return self

    @classmethod
    def get_manager(cls, manager):
        if not manager:
            manager = core.GraphDB.get_instance().manager

        return manager

    @classmethod
    def link_contact_organization(cls, contact_id, organization_id, role_name, manager=None):
        if isinstance(contact_id, six.string_types):
            contact_id = "'{}'".format(contact_id)

        if isinstance(organization_id, six.string_types):
            organization_id = "'{}'".format(organization_id)

        if not role_name:
            role_name = cls.DEFAULT_ROLE_NAME

        # create relation
        manager = cls.get_manager(manager)

        q = """
            MATCH (c:Contact), (o:Organization)
            WHERE c.handle_id = {contact_id} AND o.handle_id = {organization_id}
            MERGE (c)-[r:Works_for {{ name: '{role_name}'}}]->(o)
            RETURN ID(r) as relation_id
            """.format(contact_id=contact_id, organization_id=organization_id, role_name=role_name)
        ret = core.query_to_dict(manager, q)

        # load and return
        if ret:
            relation_id = ret['relation_id']
            relation = cls.get_relationship_model(manager, relationship_id=relation_id)

            return relation

    @classmethod
    def get_role_relation_from_organization(cls, organization_id, role_name, manager=None):
        if isinstance(organization_id, six.string_types):
            organization_id = "'{}'".format(organization_id)

        manager = cls.get_manager(manager)

        q = """
            MATCH (c:Node:Contact)-[r:Works_for]->(o:Node:Organization)
            WHERE r.name = "{role_name}" AND o.handle_id = {organization_id}
            RETURN ID(r) as relation_id
            """.format(role_name=role_name, organization_id=organization_id)
        ret = core.query_to_dict(manager, q)

        if ret:
            relation_id = ret['relation_id']
            relation = cls.get_relationship_model(manager, relationship_id=relation_id)

            return relation

    @classmethod
    def get_contact_with_role_in_organization(cls, organization_id, role_name, manager=None):
        if isinstance(organization_id, six.string_types):
            organization_id = "'{}'".format(organization_id)

        manager = cls.get_manager(manager)

        q = """
            MATCH (c:Node:Contact)-[r:Works_for]->(o:Node:Organization)
            WHERE r.name = "{role_name}" AND o.handle_id = {organization_id}
            RETURN c.handle_id as contact_handle_id
            """.format(role_name=role_name, organization_id=organization_id)
        ret = core.query_to_dict(manager, q)

        if ret:
            return ret['contact_handle_id']

    @classmethod
    def get_role_relation_from_contact_organization(cls, organization_id, role_name, contact_id, manager=None):
        if isinstance(contact_id, six.string_types):
            contact_id = "'{}'".format(contact_id)

        if isinstance(organization_id, six.string_types):
            organization_id = "'{}'".format(organization_id)

        manager = cls.get_manager(manager)

        q = """
            MATCH (c:Node:Contact)-[r:Works_for]->(o:Node:Organization)
            WHERE c.handle_id = {contact_id}
            AND r.name = "{role_name}"
            AND o.handle_id = {organization_id}
            RETURN ID(r) as relation_id
            """.format(contact_id=contact_id, role_name=role_name,
                            organization_id=organization_id)
        ret = core.query_to_dict(manager, q)

        if ret:
            relation_id = ret['relation_id']
            relation = cls.get_relationship_model(manager, relationship_id=relation_id)

            return relation

    @classmethod
    def unlink_contact_with_role_organization(cls, contact_id, organization_id, role_name, manager=None):
        if isinstance(contact_id, six.string_types):
            contact_id = "'{}'".format(contact_id)

        if isinstance(organization_id, six.string_types):
            organization_id = "'{}'".format(organization_id)

        manager = cls.get_manager(manager)

        q = '''
            MATCH (c:Contact)-[r:Works_for]->(o:Organization)
            WHERE c.handle_id = {contact_id}
            AND r.name = "{role_name}"
            AND o.handle_id = {organization_id}
            DELETE r RETURN c
            '''.format(contact_id=contact_id, role_name=role_name, \
                                organization_id=organization_id)
        ret = core.query_to_dict(manager, q)

    @classmethod
    def update_roles_withname(cls, role_name, new_name, manager=None):
        manager = cls.get_manager(manager)

        q = """
            MATCH (c:Contact)-[r:Works_for]->(o:Organization)
            WHERE r.name = "{role_name}"
            SET r.name = "{new_name}"
            RETURN r
            """.format(role_name=role_name, new_name=new_name)

        core.query_to_dict(manager, q)

    @classmethod
    def delete_roles_withname(cls, role_name, manager=None):
        manager = cls.get_manager(manager)

        q = """
            MATCH (c:Contact)-[r:Works_for]->(o:Organization)
            WHERE r.name = "{role_name}"
            DELETE r
            """.format(role_name=role_name)

        core.query_to_dict(manager, q)

    def load_from_nodes(self, contact_id, organization_id):
        if isinstance(contact_id, six.string_types):
            contact_id = "'{}'".format(contact_id)

        if isinstance(organization_id, six.string_types):
            organization_id = "'{}'".format(organization_id)

        q = """
            MATCH (c:Contact)-[r:Works_for]->(o:Organization)
            WHERE c.handle_id = {contact_id} AND o.handle_id = {organization_id}
            RETURN ID(r) as relation_id
            """.format(contact_id=contact_id, organization_id=organization_id)

        ret = core.query_to_dict(self.manager, q)

        bundle = core.get_relationship_bundle(self.manager, ret['relation_id'])
        self.load(bundle)

    @classmethod
    def get_relationship_model(cls, manager, relationship_id):
        """
        :param manager: Context manager to handle transactions
        :type manager: Neo4jDBSessionManager
        :param relationship_id: Internal Neo4j relationship id
        :type relationship_id: int
        :return: Relationship model
        :rtype: models.BaseRelationshipModel
        """
        manager = cls.get_manager(manager)

        bundle = core.get_relationship_bundle(manager, relationship_id)
        return cls(manager).load(bundle)

    @classmethod
    def get_all_role_names(cls, manager=None):
        manager = cls.get_manager(manager)

        q = """MATCH (n:Contact)-[r:Works_for]->(m:Organization)
            WHERE r.name IS NOT NULL
            RETURN DISTINCT r.name as role_name"""

        result = core.query_to_list(manager, q)
        endresult = []
        for r in result:
            endresult.append(r['role_name'])

        return endresult

    @classmethod
    def get_contacts_with_role_name(cls, role_name, manager=None):
        manager = cls.get_manager(manager)

        q = """
            MATCH (c:Contact)-[r:Works_for]->(o:Organization)
            WHERE r.name = "{role_name}"
            RETURN c, o
            """.format(role_name=role_name)

        result = core.query_to_list(manager, q)
        contact_list = []

        for node in result:
            contact = ContactModel(manager)
            contact.data = {}
            contact.data['handle_id'] = node['c'].properties['handle_id']
            contact.reload(node['c'])

            organization = OrganizationModel(manager)
            organization.data = {}
            organization.data['handle_id'] = node['o'].properties['handle_id']
            organization.reload(node['o'])

            contact_list.append((contact, organization))

        return contact_list

class ProcedureModel(LogicalModel):
    pass

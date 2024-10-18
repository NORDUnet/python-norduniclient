# -*- coding: utf-8 -*-

from __future__ import absolute_import

try:
    from neo4j.exceptions import ConstraintError
except ImportError:
    from neo4j.v1.api import CypherError as ConstraintError  # Backwards compatability with version <1.2

from norduniclient.testing import Neo4jTestCase
from norduniclient import core
from norduniclient import exceptions
from norduniclient import models

__author__ = 'lundberg'


class CoreTests(Neo4jTestCase):

    def setUp(self):
        super(CoreTests, self).setUp()
        core.create_node(self.neo4jdb, name='Test Node 1', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='1')
        core.create_node(self.neo4jdb, name='Test Node 2', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='2')

    def test_create_and_get_node(self):
        core.create_node(self.neo4jdb, name='Test Node 3', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='3')
        node = core.get_node(self.neo4jdb, handle_id='3')
        self.assertEqual(node.get('handle_id'), '3')

    def test_create_node_existing_node_handle(self):
        self.assertRaises(ConstraintError, core.create_node, self.neo4jdb, name='Test Node 1',
                          meta_type_label='Logical', type_label='Test_Node', handle_id='1')

    def test_create_node_bad_meta_type(self):
        self.assertRaises(exceptions.MetaLabelNamingError, core.create_node, self.neo4jdb, name='Test Node 1',
                          meta_type_label='No_Such_Label', type_label='Test_Node', handle_id='1')

    def test_get_node_bundle(self):
        node_bundle = core.get_node_bundle(self.neo4jdb, handle_id='1')
        self.assertIsInstance(node_bundle, dict)
        node_data = node_bundle.get('data')
        self.assertEqual(node_data.get('handle_id'), '1')
        self.assertEqual(node_bundle.get('meta_type'), 'Logical')
        self.assertIsInstance(node_bundle.get('labels'), list)
        self.assertIn('Test_Node', node_bundle.get('labels'))

    def test_failing_get_node_bundle(self):
        self.assertRaises(exceptions.NodeNotFound, core.get_node_bundle, self.neo4jdb, handle_id='3')

    def test_delete_node(self):
        core.delete_node(self.neo4jdb, handle_id='1')
        self.assertRaises(exceptions.NodeNotFound, core.get_node, self.neo4jdb, handle_id='1')

    def test_create_and_get_relationship(self):
        relationship_id = core._create_relationship(self.neo4jdb, handle_id='1', other_handle_id='2', rel_type='Tests')
        self.assertIsInstance(relationship_id, int)
        relationship = core.get_relationship_bundle(self.neo4jdb, relationship_id=relationship_id)
        self.assertEqual(relationship['id'], relationship_id)

    def test_failing_get_relationship(self):
        self.assertRaises(exceptions.RelationshipNotFound, core.get_relationship, self.neo4jdb, relationship_id=1)

    def test_get_relationship_bundle(self):
        relationship_id = core._create_relationship(self.neo4jdb, handle_id='1', other_handle_id='2', rel_type='Tests')
        relationship_bundle = core.get_relationship_bundle(self.neo4jdb, relationship_id=relationship_id)
        self.assertIsInstance(relationship_bundle, dict)
        relationship = relationship_bundle.get('data')
        self.assertIsNotNone(relationship)
        self.assertEqual(relationship_bundle.get('id'), relationship_id)
        self.assertEqual(relationship_bundle.get('start')['handle_id'], '1')
        self.assertEqual(relationship_bundle.get('end')['handle_id'], '2')
        self.assertEqual(relationship_bundle.get('type'), 'Tests')

    def test_failing_get_relationship_bundle(self):
        self.assertRaises(exceptions.RelationshipNotFound, core.get_relationship_bundle, self.neo4jdb,
                          relationship_id=1)

    def test_delete_relationship(self):
        relationship_id = core._create_relationship(self.neo4jdb, handle_id='1', other_handle_id='2', rel_type='Tests')
        relationship = core.get_relationship_bundle(self.neo4jdb, relationship_id=relationship_id)
        self.assertEqual(relationship['id'], relationship_id)
        core.delete_relationship(self.neo4jdb, relationship_id=relationship_id)
        self.assertRaises(exceptions.RelationshipNotFound, core.get_relationship, self.neo4jdb,
                          relationship_id=relationship_id)

    def test_create_location_relationship(self):
        core.create_node(self.neo4jdb, name='Location Node 1', meta_type_label='Location',
                         type_label='Test_Node', handle_id='3')
        core.create_node(self.neo4jdb, name='Location Node 2', meta_type_label='Location',
                         type_label='Test_Node', handle_id='4')
        relationship_id = core.create_location_relationship(self.neo4jdb, location_handle_id='3', other_handle_id='4',
                                                            rel_type='Has')
        self.assertIsInstance(relationship_id, int)

    def test_failing_create_location_relationship(self):
        core.create_node(self.neo4jdb, name='Location Node 1', meta_type_label='Location',
                         type_label='Test_Node', handle_id='3')
        core.create_node(self.neo4jdb, name='Logical Node 2', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='4')
        self.assertRaises(exceptions.NoRelationshipPossible, core.create_location_relationship, self.neo4jdb,
                          location_handle_id='3', other_handle_id='4', rel_type='Has')

    def test_create_logical_relationship(self):
        core.create_node(self.neo4jdb, name='Logical Node 1', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='3')
        core.create_node(self.neo4jdb, name='Physical Node 2', meta_type_label='Physical',
                         type_label='Test_Node', handle_id='4')
        core.create_node(self.neo4jdb, name='Logical Node 2', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='5')

        relationship_id = core.create_logical_relationship(self.neo4jdb, logical_handle_id='3', other_handle_id='4',
                                                           rel_type='Depends_on')
        self.assertIsInstance(relationship_id, int)

        relationship_id = core.create_logical_relationship(self.neo4jdb, logical_handle_id='3', other_handle_id='5',
                                                           rel_type='Depends_on')
        self.assertIsInstance(relationship_id, int)

        relationship_id = core.create_logical_relationship(self.neo4jdb, logical_handle_id='3', other_handle_id='4',
                                                           rel_type='Part_of')
        self.assertIsInstance(relationship_id, int)

    def test_failing_create_logical_relationship(self):
        core.create_node(self.neo4jdb, name='Logical Node 1', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='3')
        core.create_node(self.neo4jdb, name='Physical Node 2', meta_type_label='Physical',
                         type_label='Test_Node', handle_id='4')
        core.create_node(self.neo4jdb, name='Logical Node 2', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='5')

        self.assertRaises(exceptions.NoRelationshipPossible, core.create_location_relationship, self.neo4jdb,
                          location_handle_id='3', other_handle_id='4', rel_type='Has')
        self.assertRaises(exceptions.NoRelationshipPossible,core.create_location_relationship, self.neo4jdb,
                          location_handle_id='3', other_handle_id='5', rel_type='Part_of')
        self.assertRaises(exceptions.NoRelationshipPossible,core.create_location_relationship, self.neo4jdb,
                          location_handle_id='3', other_handle_id='5', rel_type='Has')

    def test_create_relation_relationship(self):
        core.create_node(self.neo4jdb, name='Relation Node 1', meta_type_label='Relation',
                         type_label='Test_Node', handle_id='3')
        core.create_node(self.neo4jdb, name='Logical Node 1', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='4')
        core.create_node(self.neo4jdb, name='Location Node 1', meta_type_label='Location',
                         type_label='Test_Node', handle_id='5')
        core.create_node(self.neo4jdb, name='Physical Node 1', meta_type_label='Physical',
                         type_label='Test_Node', handle_id='6')

        relationship_id = core.create_relation_relationship(self.neo4jdb, relation_handle_id='3', other_handle_id='4',
                                                            rel_type='Uses')
        self.assertIsInstance(relationship_id, int)

        relationship_id = core.create_relation_relationship(self.neo4jdb, relation_handle_id='3', other_handle_id='4',
                                                            rel_type='Provides')
        self.assertIsInstance(relationship_id, int)

        relationship_id = core.create_relation_relationship(self.neo4jdb, relation_handle_id='3', other_handle_id='5',
                                                            rel_type='Responsible_for')
        self.assertIsInstance(relationship_id, int)

        relationship_id = core.create_relation_relationship(self.neo4jdb, relation_handle_id='3', other_handle_id='6',
                                                            rel_type='Owns')
        self.assertIsInstance(relationship_id, int)

        relationship_id = core.create_relation_relationship(self.neo4jdb, relation_handle_id='3', other_handle_id='6',
                                                            rel_type='Provides')
        self.assertIsInstance(relationship_id, int)

    def test_failing_create_relation_relationship(self):
        core.create_node(self.neo4jdb, name='Relation Node 1', meta_type_label='Relation',
                         type_label='Test_Node', handle_id='3')
        core.create_node(self.neo4jdb, name='Logical Node 1', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='4')
        core.create_node(self.neo4jdb, name='Location Node 1', meta_type_label='Location',
                         type_label='Test_Node', handle_id='5')
        core.create_node(self.neo4jdb, name='Physical Node 1', meta_type_label='Physical',
                         type_label='Test_Node', handle_id='6')

        self.assertRaises(exceptions.NoRelationshipPossible, core.create_relation_relationship, self.neo4jdb,
                          relation_handle_id='3', other_handle_id='5', rel_type='Uses')

        self.assertRaises(exceptions.NoRelationshipPossible, core.create_relation_relationship, self.neo4jdb,
                          relation_handle_id='3', other_handle_id='6', rel_type='Responsible_for')

        self.assertRaises(exceptions.NoRelationshipPossible, core.create_relation_relationship,
                          self.neo4jdb, relation_handle_id='3', other_handle_id='6', rel_type='Responsible_for')

        self.assertRaises(exceptions.NoRelationshipPossible, core.create_relation_relationship, self.neo4jdb,
                          relation_handle_id='3', other_handle_id='5', rel_type='Owns')

        self.assertRaises(exceptions.NoRelationshipPossible, core.create_relation_relationship, self.neo4jdb,
                          relation_handle_id='3', other_handle_id='5',  rel_type='Provides')

    def test_create_physical_relationship(self):
        core.create_node(self.neo4jdb, name='Physical Node 1', meta_type_label='Physical',
                         type_label='Test_Node', handle_id='3')
        core.create_node(self.neo4jdb, name='Physical Node 2', meta_type_label='Physical',
                         type_label='Test_Node', handle_id='4')
        core.create_node(self.neo4jdb, name='Location Node 1', meta_type_label='Location',
                         type_label='Test_Node', handle_id='5')

        relationship_id = core.create_physical_relationship(self.neo4jdb, physical_handle_id='3', other_handle_id='4',
                                                            rel_type='Has')
        self.assertIsInstance(relationship_id, int)

        relationship_id = core.create_physical_relationship(self.neo4jdb, physical_handle_id='3', other_handle_id='4',
                                                            rel_type='Connected_to')
        self.assertIsInstance(relationship_id, int)

        relationship_id = core.create_physical_relationship(self.neo4jdb, physical_handle_id='3', other_handle_id='5',
                                                            rel_type='Located_in')
        self.assertIsInstance(relationship_id, int)

    def test_failing_create_physical_relationship(self):
        core.create_node(self.neo4jdb, name='Physical Node 1', meta_type_label='Physical',
                         type_label='Test_Node', handle_id='3')
        core.create_node(self.neo4jdb, name='Physical Node 2', meta_type_label='Physical',
                         type_label='Test_Node', handle_id='4')
        core.create_node(self.neo4jdb, name='Location Node 1', meta_type_label='Location',
                         type_label='Test_Node', handle_id='5')

        self.assertRaises(exceptions.NoRelationshipPossible, core.create_physical_relationship, self.neo4jdb,
                          physical_handle_id='3', other_handle_id='4', rel_type='Located_in')

        self.assertRaises(exceptions.NoRelationshipPossible, core.create_physical_relationship, self.neo4jdb,
                          physical_handle_id='3', other_handle_id='4', rel_type='Responsible_for')

        self.assertRaises(exceptions.NoRelationshipPossible, core.create_physical_relationship,
                          self.neo4jdb, physical_handle_id='3', other_handle_id='5', rel_type='Has')

    def test_create_relationship(self):
        core.create_node(self.neo4jdb, name='Location Node 1', meta_type_label='Location',
                         type_label='Test_Node', handle_id='3')
        core.create_node(self.neo4jdb, name='Location Node 2', meta_type_label='Location',
                         type_label='Test_Node', handle_id='4')
        core.create_node(self.neo4jdb, name='Relation Node 1', meta_type_label='Relation',
                         type_label='Test_Node', handle_id='5')
        core.create_node(self.neo4jdb, name='Physical Node 1', meta_type_label='Physical',
                         type_label='Test_Node', handle_id='6')

        relationship_id = core.create_relationship(self.neo4jdb, handle_id='3', other_handle_id='4',
                                                   rel_type='Has')
        self.assertIsInstance(relationship_id, int)

        relationship_id = core.create_relationship(self.neo4jdb, handle_id='5', other_handle_id='4',
                                                   rel_type='Responsible_for')
        self.assertIsInstance(relationship_id, int)

        relationship_id = core.create_relationship(self.neo4jdb, handle_id='6', other_handle_id='4',
                                                   rel_type='Located_in')
        self.assertIsInstance(relationship_id, int)

    def test_failing_create_relationship(self):
        core.create_node(self.neo4jdb, name='Location Node 1', meta_type_label='Location',
                         type_label='Test_Node', handle_id='3')
        core.create_node(self.neo4jdb, name='Location Node 2', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='4')
        self.assertRaises(exceptions.NoRelationshipPossible, core.create_relationship, self.neo4jdb,
                          handle_id='3', other_handle_id='4', rel_type='Has')

    def test_get_relationships(self):
        relationship_id = core.create_relationship(self.neo4jdb, handle_id='1', other_handle_id='2',
                                                   rel_type='Depends_on')

        relationships = core.get_relationships(self.neo4jdb, handle_id1='1', handle_id2='2')
        self.assertIn(relationship_id, [r.id for r in relationships])

        relationships = core.get_relationships(self.neo4jdb, handle_id1='1', handle_id2='2', rel_type='Depends_on')
        self.assertIn(relationship_id, [r.id for r in relationships])

        # No relationship
        core.create_node(self.neo4jdb, name='Location Node 1', meta_type_label='Location',
                         type_label='Test_Node', handle_id='3')
        relationships = core.get_relationships(self.neo4jdb, handle_id1='1', handle_id2='3')
        self.assertEqual(relationships, [])

    def test_set_node_properties(self):
        new_properties = {'test': 'hello world'}
        core.set_node_properties(self.neo4jdb, handle_id='1', new_properties=new_properties)
        node = core.get_node(self.neo4jdb, handle_id='1')
        new_properties.update({'handle_id': '1'})
        self.assertEqual(node['test'], new_properties['test'])

#    def test_fail_set_node_properties(self):
#        new_properties = {'test': set([])}
#        self.assertRaises(exceptions.BadProperties, core.set_node_properties, self.neo4jdb,
#                          handle_id='1', new_properties=new_properties)

    def test_set_relationship_properties(self):
        relationship_id = core.create_relationship(self.neo4jdb, handle_id='1', other_handle_id='2',
                                                   rel_type='Depends_on')
        new_properties = {'test': 'hello world'}
        core.set_relationship_properties(self.neo4jdb, relationship_id=relationship_id, new_properties=new_properties)
        relationship = core.get_relationship(self.neo4jdb, relationship_id=relationship_id)
        self.assertEqual(relationship['test'], new_properties['test'])

#    def test_fail_set_relationship_properties(self):
#        relationship_id = core.create_relationship(self.neo4jdb, handle_id='1', other_handle_id='2',
#                                                   rel_type='Depends_on')
#        new_properties = {'test': set([])}
#        self.assertRaises(exceptions.BadProperties, core.set_relationship_properties, self.neo4jdb,
#                          relationship_id=relationship_id, new_properties=new_properties)

    def test_get_node_model(self):
        node_model = core.get_node_model(self.neo4jdb, handle_id='1')
        self.assertIsInstance(node_model, models.LogicalModel)

    def test_get_relationship_model(self):
        relationship_id = core.create_relationship(self.neo4jdb, handle_id='1', other_handle_id='2',
                                                   rel_type='Depends_on')
        relationship_model = core.get_relationship_model(self.neo4jdb, relationship_id=relationship_id)
        self.assertIsInstance(relationship_model, models.BaseRelationshipModel)

    def test_get_nodes_by_value_and_property(self):
        new_properties = {'test': 'hello world'}
        core.set_node_properties(self.neo4jdb, handle_id='1', new_properties=new_properties)
        result = core.get_nodes_by_value(self.neo4jdb, value='hello world', prop='test')

        all_results = [r for r in result]
        self.assertEqual(len(all_results), 1)
        node = all_results[0]
        self.assertEqual(node.get('test'), 'hello world')

    def test_get_nodes_by_value_and_property_list(self):
        new_properties = {'test': ['hello', 'world']}
        core.set_node_properties(self.neo4jdb, handle_id='1', new_properties=new_properties)
        result = core.get_nodes_by_value(self.neo4jdb, value=['hello', 'world'], prop='test')

        all_results = [r for r in result]
        self.assertEqual(len(all_results), 1)
        node = all_results[0]
        self.assertEqual(node.get('test'), ['hello', 'world'])

    def test_get_nodes_by_value_and_property_bool(self):
        new_properties = {'test': False}
        core.set_node_properties(self.neo4jdb, handle_id='1', new_properties=new_properties)
        result = core.get_nodes_by_value(self.neo4jdb, value=False, prop='test')

        all_results = [r for r in result]
        self.assertEqual(len(all_results), 1)
        node = all_results[0]
        self.assertEqual(node.get('test'), False)

    def test_get_nodes_by_value_and_property_int(self):
        new_properties = {'test': 3}
        core.set_node_properties(self.neo4jdb, handle_id='1', new_properties=new_properties)
        result = core.get_nodes_by_value(self.neo4jdb, value=3, prop='test')

        all_results = [r for r in result]
        self.assertEqual(len(all_results), 1)
        node = all_results[0]
        self.assertEqual(node.get('test'), 3)

    def test_search_nodes_by_value(self):
        new_properties = {'test': 'hello world'}
        core.set_node_properties(self.neo4jdb, handle_id='1', new_properties=new_properties)

        result = core.search_nodes_by_value(self.neo4jdb, value='world')

        all_results = [r for r in result]
        self.assertEqual(len(all_results), 1)
        node = all_results[0]
        self.assertEqual(node.get('test'), 'hello world')

    def test_search_nodes_by_value_and_property(self):
        new_properties = {'test': 'hello world'}
        core.set_node_properties(self.neo4jdb, handle_id='1', new_properties=new_properties)
        result = core.search_nodes_by_value(self.neo4jdb, value='world', prop='test')

        all_results = [r for r in result]
        self.assertEqual(len(all_results), 1)
        node = all_results[0]
        self.assertEqual(node.get('test'), 'hello world')

    def test_search_nodes_by_value_in_list(self):
        new_properties = {'test': ['hello', 'world']}
        core.set_node_properties(self.neo4jdb, handle_id='1', new_properties=new_properties)

        result = core.search_nodes_by_value(self.neo4jdb, value='hel')

        all_results = [r for r in result]
        self.assertEqual(len(all_results), 1)
        node = all_results[0]
        self.assertEqual(node.get('test'), ['hello', 'world'])

    def test_search_nodes_by_value_and_property_in_list(self):
        new_properties = {'test': ['hello', 'world']}
        core.set_node_properties(self.neo4jdb, handle_id='1', new_properties=new_properties)
        result = core.search_nodes_by_value(self.neo4jdb, value='hel', prop='test')

        all_results = [r for r in result]
        self.assertEqual(len(all_results), 1)
        node = all_results[0]
        self.assertEqual(node.get('test'), ['hello', 'world'])

    def test_get_nodes_by_type(self):
        result = core.get_nodes_by_type(self.neo4jdb, 'Test_Node')

        for node in result:
            self.assertIn('Test_Node', node.labels)

    def test_get_nodes_by_name(self):
        result = core.get_nodes_by_name(self.neo4jdb, 'Test Node 1')

        all_results = [r for r in result]
        self.assertEqual(len(all_results), 1)
        node = all_results[0]
        self.assertEqual(node['name'], 'Test Node 1')

    def test_get_unique_node_by_name(self):
        node_model = core.get_unique_node_by_name(self.neo4jdb, node_name='Test Node 1', node_type='Test_Node')
        self.assertIsInstance(node_model, models.LogicalModel)

    def test_failing_get_unique_node_by_name(self):
        core.create_node(self.neo4jdb, name='Test Node 1', meta_type_label='Logical',
                         type_label='Test_Node', handle_id='3')
        self.assertRaises(exceptions.MultipleNodesReturned, core.get_unique_node_by_name, self.neo4jdb,
                          node_name='Test Node 1', node_type='Test_Node')


# -*- coding: utf-8 -*-

from __future__ import absolute_import

from norduniclient.testing import Neo4jTestCase
from norduniclient import core
from norduniclient import exceptions
from norduniclient import models

__author__ = 'lundberg'


class ModelsTests(Neo4jTestCase):

    def setUp(self):
        super(ModelsTests, self).setUp()
        q1 = """
            // Create nodes
            CREATE (router1:Node:Physical:Router{name:'Router1', handle_id:'1'}),
            (port1:Node:Physical:Port{name:'Port1', handle_id:'2'}),
            (unit1:Node:Logical:Unit{name:'Unit1', handle_id:'3'}),
            (port6:Node:Physical:Port{name:'Port6', handle_id:'4'}),
            (unit2:Node:Logical:Unit{name:'Unit2', handle_id:'5'}),
            (provider1:Node:Relation:Provider{name:'Provider1', handle_id:'6'}),
            (peering_group1:Node:Logical:Peering_Group{name:'Peering Group1', handle_id:'7'}),
            (peering_partner1:Node:Relation:Peering_Partner{name:'Peering Partner1', handle_id:'8'}),
            (service2:Node:Logical:Service{name:'Service2', handle_id:'9'}),
            (service3:Node:Logical:Service{name:'Service3', handle_id:'10'}),
            (site1:Node:Location:Site{name:'Site1', handle_id:'11'}),
            (rack1:Node:Location:Rack{name:'Rack1', handle_id:'12'}),
            (optical_node1:Node:Physical:Optical_Node{name:'Optical Node1', handle_id:'13'}),
            (port2:Node:Physical:Port{name:'Port2', handle_id:'14', description:'This is a port'}),
            (rack2:Node:Location:Rack{name:'Rack2', handle_id:'15'}),
            (optical_node2:Node:Physical:Optical_Node{name:'Optical Node2', handle_id:'16'}),
            (port3:Node:Physical:Port{name:'Port3', handle_id:'17'}),
            (site2:Node:Location:Site{name:'Site2', handle_id:'18'}),
            (rack3:Node:Location:Rack{name:'Rack3', handle_id:'19'}),
            (optical_path1:Node:Logical:Optical_Path{name:'Optical Path1', handle_id:'20'}),
            (optical_link1:Node:Logical:Optical_Link{name:'Optical Link1', handle_id:'21'}),
            (optical_link2:Node:Logical:Optical_Link{name:'Optical Link2', handle_id:'22'}),
            (odf1:Node:Physical:ODF{name:'ODF1', handle_id:'23'}),
            (port4:Node:Physical:Port{name:'Port4', handle_id:'24'}),
            (odf2:Node:Physical:ODF{name:'ODF2', handle_id:'25'}),
            (port5:Node:Physical:Port{name:'Port5', handle_id:'26'}),
            (port7:Node:Physical:Port{name:'Port7', handle_id:'27'}),
            (cable1:Node:Physical:Cable{name:'Cable1', handle_id:'28'}),
            (cable2:Node:Physical:Cable{name:'Cable2', handle_id:'29'}),
            (cable3:Node:Physical:Cable{name:'Cable3', handle_id:'30'}),
            (cable4:Node:Physical:Cable{name:'Cable4', handle_id:'31'}),
            (host1:Node:Physical:Host{name:'Host1', handle_id:'32'}),
            (host2:Node:Logical:Host{name:'Host2', handle_id:'33'}),
            (customer1:Node:Relation:Customer{name:'Customer1', handle_id:'34'}),
            (customer2:Node:Relation:Customer{name:'Customer2', handle_id:'35'}),
            (customer3:Node:Relation:Customer{name:'Customer3', handle_id:'36'}),
            (customer4:Node:Relation:Customer{name:'Customer4', handle_id:'37'}),
            (service4:Node:Logical:Service{name:'Service4', handle_id:'38'}),
            (provider2:Node:Relation:Provider{name:'Provider2', handle_id:'39'}),
            (port8:Node:Physical:Port{name:'Port8', handle_id:'40'}),
            (rack4:Node:Location:Rack{name:'Rack4', handle_id:'41'}),
            (cable5:Node:Physical:Cable{name:'Cable5', handle_id:'42'}),
            (host_service1:Node:Logical:Host_Service{name:'Host Service1', handle_id:'43'}),
            (peering_group2:Node:Logical:Peering_Group{name:'Peering Group2', handle_id:'44'}),
            (cable6:Node:Physical:Cable{name:'Cable6', handle_id:'45'}),
            (service5:Node:Logical:Service{name:'Service5', handle_id:'46'}),
            (external_equipment1:Node:Physical:External_Equipment{name:'External Equipment1', handle_id:'47'}),

            // Create relationships
            (router1)-[:Has]->(port1),
            (unit1)-[:Part_of]->(port1),
            (router1)-[:Has]->(port6),
            (unit2)-[:Part_of]->(port6),
            (provider1)-[:Owns]->(router1),
            (provider1)-[:Provides]->(peering_group1),
            (peering_partner1)-[:Uses {ip_address:'127.0.0.1'}]->(peering_group1),
            (peering_group1)-[:Depends_on]->(unit1),
            (site1)-[:Has]->(rack1),
            (router1)-[:Located_in]->(rack1),
            (provider1)-[:Responsible_for]->(rack1),
            (optical_node1)-[:Has]->(port2),
            (site1)-[:Has]->(rack2),
            (optical_node1)-[:Located_in]->(rack2),
            (optical_node2)-[:Has]->(port3),
            (site2)-[:Has]->(rack3),
            (optical_node2)-[:Located_in]->(rack3),
            (provider1)-[:Provides]->(optical_path1),
            (service2)-[:Depends_on]->(optical_path1),
            (service3)-[:Depends_on]->(unit2),
            (odf1)-[:Located_in]->(rack2),
            (odf1)-[:Has]->(port4),
            (odf2)-[:Located_in]->(rack3),
            (odf2)-[:Has]->(port5),
            (odf2)-[:Has]->(port7),
            (port4)<-[:Connected_to]-(cable1)-[:Connected_to]->(port2),
            (port5)<-[:Connected_to]-(cable2)-[:Connected_to]->(port3),
            (port4)<-[:Connected_to]-(cable3)-[:Connected_to]->(port5),
            (port6)<-[:Connected_to]-(cable4)-[:Connected_to]->(port7),
            (port7)<-[:Connected_to]-(cable5),
            (optical_link1)-[:Depends_on]->(port2),
            (optical_link2)-[:Depends_on]->(port3),
            (optical_link1)-[:Depends_on]->(port4),
            (optical_link2)-[:Depends_on]->(port5),
            (optical_path1)-[:Depends_on]->(port4),
            (optical_path1)-[:Depends_on]->(port5),
            (optical_path1)-[:Depends_on]->(optical_link1),
            (optical_path1)-[:Depends_on]->(optical_link2),
            (provider1)-[:Owns]->(host1),
            (host2)-[:Depends_on]->(host1),
            (customer1)-[:Uses]->(host2),
            (customer2)-[:Uses]->(service2),
            (customer2)-[:Uses]->(service3),
            (customer3)-[:Uses]->(service3),
            (host_service1)-[:Depends_on {ip_address:'127.0.0.1',port:'80',protocol:'tcp'}]->(host1),
            (service5)-[:Depends_on]->(external_equipment1)
            """

        q2 = """
            // Create nodes
            CREATE (physical1:Node:Physical:Generic{name:'Physical1', handle_id:'101'}),
            (physical2:Node:Physical:Generic{name:'Physical2', handle_id:'102', description:'This is a port'}),
            (logical1:Node:Logical:Generic{name:'Logical1', handle_id:'103'}),
            (physical3:Node:Physical:Generic{name:'Physical3', handle_id:'104'}),
            (logical2:Node:Logical:Generic{name:'Logical2', handle_id:'105'}),
            (relation1:Node:Relation:Generic{name:'Relation1', handle_id:'106'}),
            (logical3:Node:Logical:Generic{name:'Logical3', handle_id:'107'}),
            (relation2:Node:Relation:Generic{name:'Relation2', handle_id:'108'}),
            (location1:Node:Location:Generic{name:'Location1', handle_id:'109'}),
            (location2:Node:Location:Generic{name:'Location2', handle_id:'110'}),
            (logical4:Node:Logical:Generic{name:'Logical4', handle_id:'111'}),
            (physical4:Node:Physical:Generic{name:'Physical4', handle_id:'112', description:'This is a cable'}),

            // Create relationships
            (physical1)-[:Has]->(physical2),
            (logical1)-[:Part_of]->(physical2),
            (physical1)-[:Has]->(physical3),
            (logical2)-[:Part_of]->(physical3),
            (relation1)-[:Owns]->(physical1),
            (relation1)-[:Provides]->(logical3),
            (relation2)-[:Uses]->(logical3),
            (logical3)-[:Depends_on]->(logical1),
            (location1)-[:Has]->(location2),
            (physical1)-[:Located_in]->(location2),
            (relation1)-[:Responsible_for]->(location2),
            (logical4)-[:Depends_on]->(logical3),
            (physical2)<-[:Connected_to]-(physical4)-[:Connected_to]->(physical3)
            """

        self.role_name_1 = u'IT-Manager'
        self.role_name_2 = u'Abuse Management'

        q3 = """
            // Create organization and contact nodes
            CREATE (organization1:Node:Relation:Organization{name:'Organization1', handle_id:'113'}),
            (organization2:Node:Relation:Organization{name:'Organization2', handle_id:'114'}),
            (contact1:Node:Relation:Contact{name:'Contact1', handle_id:'115'}),
            (contact2:Node:Relation:Contact{name:'Contact2', handle_id:'116'}),
            (procedure1:Node:Logical:Procedure{name:'Procedure1', handle_id:'119'}),
            (procedure2:Node:Logical:Procedure{name:'Procedure2', handle_id:'120'}),
            (group1:Node:Logical:Group{name:'Group1', handle_id:'121'}),


            // Create relationships
            (contact1)-[:Works_for {name: 'IT-Manager' }]->(organization1),
            (contact2)-[:Works_for {name: 'Abuse Management' }]->(organization2),
            (organization1)-[:Uses_a]->(procedure1)
            """

        # Insert mocked network
        with self.neo4jdb.session as s:
            s.run(q1)

        # Insert generic models
        with self.neo4jdb.session as s:
            s.run(q2)

        # Insert organizations and contacts
        with self.neo4jdb.session as s:
            s.run(q3)

    def test_base_node_model(self):
        node_model_1 = core.get_node_model(self.neo4jdb, handle_id='101')
        node_model_2 = core.get_node_model(self.neo4jdb, handle_id='102')

        self.assertIsNotNone(str(node_model_1))
        self.assertIsNotNone(repr(node_model_1))

        self.assertEqual(node_model_1, node_model_1)
        self.assertGreater(node_model_2, node_model_1)
        self.assertLess(node_model_1, node_model_2)

        self.assertEqual(node_model_1.handle_id, '101')
        self.assertIn(node_model_1.meta_type, core.META_TYPES)
        self.assertIsInstance(node_model_1.labels, list)
        self.assertIsNotNone(node_model_1.data)
        self.assertIsInstance(node_model_1.incoming, dict)
        self.assertIsInstance(node_model_1.outgoing, dict)
        self.assertIsInstance(node_model_1.relationships, dict)

    def test_add_label(self):
        node_model_1 = core.get_node_model(self.neo4jdb, handle_id='101')
        initial_labels = node_model_1.labels
        node_model_1.add_label('Test_Label')
        node_model_1 = node_model_1.reload()
        new_labels = node_model_1.labels
        initial_labels.append('Test_Label')
        self.assertEqual(sorted(new_labels), sorted(initial_labels))

    def test_remove_label(self):
        node_model_1 = core.get_node_model(self.neo4jdb, handle_id='101')
        initial_labels = node_model_1.labels
        node_model_1 = node_model_1.add_label('Test_Label')
        new_labels = node_model_1.labels
        expected_labels = initial_labels + ['Test_Label']
        self.assertEqual(sorted(new_labels), sorted(expected_labels))
        node_model_1 = node_model_1.remove_label('Test_Label')
        new_labels = node_model_1.labels
        self.assertEqual(sorted(new_labels), sorted(initial_labels))

    def test_add_remove_property(self):
        node_model_1 = core.get_node_model(self.neo4jdb, handle_id='115')
        initial_data = node_model_1.data
        first_name = 'Smith'
        node_model_1 = node_model_1.add_property('first_name', first_name)
        new_data = node_model_1.data
        new_property = {'first_name': first_name}
        expected_data = initial_data.copy()
        expected_data.update(new_property)
        self.assertEqual(sorted(new_data), sorted(expected_data))
        node_model_1 = node_model_1.remove_property('first_name')
        new_data = node_model_1.data
        self.assertEqual(sorted(new_data), sorted(initial_data))

    def test_change_meta_type(self):
        node_model_1 = core.get_node_model(self.neo4jdb, handle_id='101')
        self.assertEqual(node_model_1.meta_type, 'Physical')
        node_model_1 = node_model_1.change_meta_type('Logical')
        self.assertEqual(node_model_1.meta_type, 'Logical')

    def test_switch_type(self):
        node_model_1 = core.get_node_model(self.neo4jdb, handle_id='101')
        self.assertIn('Generic', node_model_1.labels)
        node_model_1 = node_model_1.switch_type(old_type='Generic', new_type='New_Type')
        self.assertNotIn('Generic', node_model_1.labels)
        self.assertIn('New_Type', node_model_1.labels)

    def test_delete(self):
        node_model_1 = core.get_node_model(self.neo4jdb, handle_id='101')
        node_model_1.delete()
        self.assertRaises(exceptions.NodeNotFound, core.get_node_model, self.neo4jdb, handle_id='101')

    def test_base_relationship_model(self):
        node_model_1 = core.get_node_model(self.neo4jdb, handle_id='101')
        outgoing_relationships = node_model_1.outgoing
        self.assertGreater(len(outgoing_relationships), 0)

        for rel_type, relationships in outgoing_relationships.items():
            self.assertIsNotNone(rel_type)
            for item in relationships:
                relationship_model = core.get_relationship_model(self.neo4jdb, item['relationship_id'])
                self.assertIsNotNone(str(relationship_model))
                self.assertIsNotNone(repr(relationship_model))
                self.assertIsNotNone(relationship_model.type)
                self.assertIsInstance(relationship_model.id, int)
                self.assertIsNotNone(relationship_model.data)
                self.assertEqual(relationship_model.start['handle_id'], node_model_1.handle_id)
                self.assertEqual(relationship_model.end['handle_id'], item['node'].handle_id)

    def test_get_location_path(self):
        # Model with location
        physical1 = core.get_node_model(self.neo4jdb, handle_id='101')
        location_path = physical1.get_location_path()
        self.assertEqual(location_path['location_path'][0]['name'], 'Location1')
        self.assertEqual(location_path['location_path'][1]['name'], 'Location2')

        # Model without location
        relation1 = core.get_node_model(self.neo4jdb, handle_id='106')
        location_path = relation1.get_location_path()
        self.assertEqual(location_path['location_path'], [])

    def test_get_location(self):
        # Model with location
        physical1 = core.get_node_model(self.neo4jdb, handle_id='101')
        location = physical1.get_location()
        self.assertIsInstance(location['Located_in'][0]['node'], models.LocationModel)
        self.assertEqual(location['Located_in'][0]['node'].data['name'], 'Location2')
        self.assertIsInstance(location['Located_in'][0]['relationship_id'], int)

        # Model without location
        relation1 = core.get_node_model(self.neo4jdb, handle_id='106')
        location = relation1.get_location()
        self.assertIsNone(location.get('Located_in'))

    def test_get_placement_path(self):
        # Models with placement path
        physical2 = core.get_node_model(self.neo4jdb, handle_id='102')
        placement_path = physical2.get_placement_path()
        self.assertEqual(placement_path['placement_path'][0]['name'], 'Physical1')

        # Model without placement path
        relation1 = core.get_node_model(self.neo4jdb, handle_id='106')
        location_path = relation1.get_placement_path()
        self.assertEqual(location_path['placement_path'], [])

    def test_get_child_form_data(self):
        physical1 = core.get_node_model(self.neo4jdb, handle_id='101')
        child_form_data = physical1.get_child_form_data(node_type='Generic')
        for data in child_form_data:
            self.assertIn(data['handle_id'], ['102', '104'])
            self.assertIn(data['name'], ['Physical2', 'Physical3'])
            self.assertIn(data['description'], ['This is a port', None])
            self.assertEqual(data['labels'], [u'Node', u'Physical', u'Generic'])

    def test_get_relations(self):
        physical1 = core.get_node_model(self.neo4jdb, handle_id='101')
        relations = physical1.get_relations()
        self.assertEqual(physical1.meta_type, 'Physical')
        self.assertIsInstance(relations['Owns'][0]['node'], models.RelationModel)

        logical3 = core.get_node_model(self.neo4jdb, handle_id='107')
        relations = logical3.get_relations()
        self.assertEqual(logical3.meta_type, 'Logical')
        self.assertIsInstance(relations['Uses'][0]['node'], models.RelationModel)

        logical3 = core.get_node_model(self.neo4jdb, handle_id='107')
        relations = logical3.get_relations()
        self.assertIsInstance(relations['Provides'][0]['node'], models.RelationModel)

        location2 = core.get_node_model(self.neo4jdb, handle_id='110')
        relations = location2.get_relations()
        self.assertIsInstance(relations['Responsible_for'][0]['node'], models.RelationModel)

        organization1 = core.get_node_model(self.neo4jdb, handle_id='113')
        relations = organization1.get_relations()
        self.assertIsInstance(relations['Works_for'][0]['node'], models.RelationModel)

    def test_get_dependencies(self):
        logical3 = core.get_node_model(self.neo4jdb, handle_id='107')
        dependencies = logical3.get_dependencies()
        self.assertEqual(len(dependencies['Depends_on']), 1)
        self.assertEqual(dependencies['Depends_on'][0]['node'].handle_id, '103')
        self.assertIsInstance(dependencies['Depends_on'][0]['node'], models.LogicalModel)

    def test_get_dependents(self):
        logical1 = core.get_node_model(self.neo4jdb, handle_id='103')
        dependents = logical1.get_dependents()
        self.assertEqual(len(dependents['Depends_on']), 1)
        self.assertEqual(dependents['Depends_on'][0]['node'].handle_id, '107')
        self.assertIsInstance(dependents['Depends_on'][0]['node'], models.LogicalModel)

    def test_get_dependent_as_types(self):
        logical1 = core.get_node_model(self.neo4jdb, handle_id='103')
        dependents = logical1.get_dependent_as_types()
        self.assertEqual(dependents['direct'][0]['name'], 'Logical3')
        self.assertEqual(dependents['links'], [])
        self.assertEqual(dependents['oms'], [])
        self.assertEqual(dependents['paths'], [])
        self.assertEqual(dependents['services'], [])

    def test_get_dependent_as_types_port_with_unit_services(self):
        port6 = core.get_node_model(self.neo4jdb, handle_id='4')
        dependent = port6.get_dependent_as_types()
        self.assertEqual(dependent['direct'], [])
        self.assertEqual(dependent['links'], [])
        self.assertEqual(dependent['oms'], [])
        self.assertEqual(dependent['paths'], [])
        self.assertEqual(len(dependent['services']), 1)
        self.assertEqual(dependent['services'][0]['name'], 'Service3')

    def test_get_dependent_as_types_equipment(self):
        external1 = core.get_node_model(self.neo4jdb, handle_id='47')
        # a bit nasty just moving a port
        external1.set_has('24')  # port4
        dependents = external1.get_dependent_as_types()
        self.assertIn('Service5', [n['name'] for n in dependents['direct']])
        self.assertIn('Optical Link1', [n['name'] for n in dependents['links']])
        self.assertIn('Optical Link2', [n['name'] for n in dependents['links']])
        self.assertEqual(dependents['oms'], [])
        self.assertIn('Optical Path1', [n['name'] for n in dependents['paths']])
        self.assertIn('Service2', [n['name'] for n in dependents['services']])
        self.assertIn('Service5', [n['name'] for n in dependents['services']])

    def test_get_dependent_as_types_equipment_only_direct(self):
        external1 = core.get_node_model(self.neo4jdb, handle_id='47')
        dependents = external1.get_dependent_as_types()
        self.assertEqual(dependents['direct'][0]['name'], 'Service5')
        self.assertEqual(dependents['links'], [])
        self.assertEqual(dependents['oms'], [])
        self.assertEqual(dependents['paths'], [])
        self.assertEqual(dependents['services'][0]['name'], 'Service5')

    def test_get_dependencies_as_types(self):
        logical4 = core.get_node_model(self.neo4jdb, handle_id='111')
        dependencies = logical4.get_dependencies_as_types()
        self.assertEqual(dependencies['direct'][0]['name'], 'Logical3')
        self.assertEqual(dependencies['links'], [])
        self.assertEqual(dependencies['oms'], [])
        self.assertEqual(dependencies['paths'], [])
        self.assertEqual(dependencies['services'], [])

    def test_get_ports(self):
        physical4 = core.get_node_model(self.neo4jdb, handle_id='112')
        ports = physical4.get_ports()
        self.assertIsInstance(ports, list)
        self.assertEqual(len(ports), 0)

    def test_get_part_of_logical_model(self):
        unit1 = core.get_node_model(self.neo4jdb, handle_id='3')
        part_of = unit1.get_part_of()
        self.assertEqual(part_of['Part_of'][0]['node'].handle_id, '2')

    def test_set_user_logical_model(self):
        customer4 = core.get_node_model(self.neo4jdb, handle_id='37')
        service4 = core.get_node_model(self.neo4jdb, handle_id='38')

        result = service4.set_user(customer4.handle_id)
        self.assertEqual(result['Uses'][0]['created'], True)
        relations = service4.get_relations()
        self.assertEqual(len(relations['Uses']), 1)
        self.assertEqual(relations['Uses'][0]['node'].handle_id, customer4.handle_id)

        # Do not accept duplicates
        result = service4.set_user(customer4.handle_id)
        self.assertEqual(result['Uses'][0]['created'], False)
        relations = service4.get_relations()
        self.assertEqual(len(relations['Uses']), 1)

    def test_set_provider_logical_model(self):
        provider_1 = core.get_node_model(self.neo4jdb, handle_id='6')
        service4 = core.get_node_model(self.neo4jdb, handle_id='38')

        result = service4.set_provider(provider_1.handle_id)
        self.assertEqual(result['Provides'][0]['created'], True)
        relations = service4.get_relations()
        self.assertEqual(len(relations['Provides']), 1)
        self.assertEqual(relations['Provides'][0]['node'].handle_id, provider_1.handle_id)

        # Do not accept duplicates
        result = service4.set_provider(provider_1.handle_id)
        self.assertEqual(result['Provides'][0]['created'], False)
        relations = service4.get_relations()
        self.assertEqual(len(relations['Provides']), 1)

    def test_set_dependency_logical_model(self):
        optical_path1 = core.get_node_model(self.neo4jdb, handle_id='20')
        service4 = core.get_node_model(self.neo4jdb, handle_id='38')

        result = service4.set_dependency(optical_path1.handle_id)
        self.assertEqual(result['Depends_on'][0]['created'], True)
        relations = service4.get_dependencies()
        self.assertEqual(len(relations['Depends_on']), 1)
        self.assertEqual(relations['Depends_on'][0]['node'].handle_id, optical_path1.handle_id)

        # Do not accept duplicates
        result = service4.set_dependency(optical_path1.handle_id)
        self.assertEqual(result['Depends_on'][0]['created'], False)
        relations = service4.get_dependencies()
        self.assertEqual(len(relations['Depends_on']), 1)

    def test_get_location_physical_model(self):
        router1 = core.get_node_model(self.neo4jdb, handle_id='1')
        location = router1.get_location()
        self.assertIsInstance(location['Located_in'][0]['node'], models.LocationModel)
        self.assertEqual(location['Located_in'][0]['node'].data['name'], 'Rack1')
        self.assertIsInstance(location['Located_in'][0]['relationship_id'], int)

    def test_set_owner_physical_model(self):
        router1 = core.get_node_model(self.neo4jdb, handle_id='1')
        customer4 = core.get_node_model(self.neo4jdb, handle_id='37')

        result = router1.set_owner(customer4.handle_id)
        self.assertEqual(result['Owns'][0]['created'], True)
        relations = router1.get_relations()
        self.assertEqual(len(relations['Owns']), 2)

        # Do not accept duplicates
        result = router1.set_owner(customer4.handle_id)
        self.assertEqual(result['Owns'][0]['created'], False)
        relations = router1.get_relations()
        self.assertEqual(len(relations['Owns']), 2)

    def test_set_provider_physical_model(self):
        router1 = core.get_node_model(self.neo4jdb, handle_id='1')
        provider_2 = core.get_node_model(self.neo4jdb, handle_id='39')

        result = router1.set_provider(provider_2.handle_id)
        self.assertEqual(result['Provides'][0]['created'], True)
        relations = router1.get_relations()
        self.assertEqual(len(relations['Provides']), 1)
        self.assertEqual(relations['Provides'][0]['node'].handle_id, provider_2.handle_id)

        # Do not accept duplicates
        result = router1.set_provider(provider_2.handle_id)
        self.assertEqual(result['Provides'][0]['created'], False)
        relations = router1.get_relations()
        self.assertEqual(len(relations['Provides']), 1)

    def test_set_location_physical_model(self):
        router1 = core.get_node_model(self.neo4jdb, handle_id='1')
        rack_2 = core.get_node_model(self.neo4jdb, handle_id='15')

        result = router1.set_location(rack_2.handle_id)
        self.assertEqual(result['Located_in'][0]['created'], True)
        location = router1.get_location()
        self.assertEqual(len(location['Located_in']), 2)

        # Do not accept duplicates
        result = router1.set_location(rack_2.handle_id)
        self.assertEqual(result['Located_in'][0]['created'], False)
        location = router1.get_location()
        self.assertEqual(len(location['Located_in']), 2)

    def test_set_and_get_has_physical_model(self):
        router1 = core.get_node_model(self.neo4jdb, handle_id='1')
        port8 = core.get_node_model(self.neo4jdb, handle_id='40')

        result = router1.set_has(port8.handle_id)
        self.assertEqual(result['Has'][0]['created'], True)
        children = router1.get_has()
        self.assertEqual(len(children['Has']), 3)

        # Do not accept duplicates
        result = router1.set_has(port8.handle_id)
        self.assertEqual(result['Has'][0]['created'], False)
        children = router1.get_has()
        self.assertEqual(len(children['Has']), 3)

    def test_set_and_get_part_of_physical_model(self):
        port8 = core.get_node_model(self.neo4jdb, handle_id='40')
        unit1 = core.get_node_model(self.neo4jdb, handle_id='3')

        result = port8.set_part_of(unit1.handle_id)
        self.assertEqual(result['Part_of'][0]['created'], True)
        children = port8.get_part_of()
        self.assertEqual(len(children['Part_of']), 1)

        # Do not accept duplicates
        result = port8.set_part_of(unit1.handle_id)
        self.assertEqual(result['Part_of'][0]['created'], False)
        children = port8.get_part_of()
        self.assertEqual(len(children['Part_of']), 1)

    def test_get_parent_physical_model(self):
        port1 = core.get_node_model(self.neo4jdb, handle_id='2')
        parent = port1.get_parent()
        self.assertIsInstance(parent['Has'][0]['node'], models.PhysicalModel)
        self.assertEqual(parent['Has'][0]['node'].data['name'], 'Router1')
        self.assertIsInstance(parent['Has'][0]['relationship_id'], int)

    def test_get_location_path_location_model(self):
        rack_2 = core.get_node_model(self.neo4jdb, handle_id='15')
        location_path = rack_2.get_location_path()
        self.assertEqual(location_path['location_path'][0]['name'], 'Site1')

    def test_get_parent_location_model(self):
        rack_2 = core.get_node_model(self.neo4jdb, handle_id='15')
        parent = rack_2.get_parent()
        self.assertEqual(parent['Has'][0]['node'].data['name'], 'Site1')

    def test_get_located_in_location_model(self):
        rack_2 = core.get_node_model(self.neo4jdb, handle_id='15')
        located_in = rack_2.get_located_in()
        self.assertEqual(len(located_in['Located_in']), 2)
        optical_node = [node for node in located_in['Located_in'] if node['node'].data['name'] == 'Optical Node1'][0]
        self.assertIsInstance(optical_node['node'], models.PhysicalModel)
        self.assertIsInstance(optical_node['relationship_id'], int)

    def test_set_and_get_has_location_model(self):
        site1 = core.get_node_model(self.neo4jdb, handle_id='11')
        rack_4 = core.get_node_model(self.neo4jdb, handle_id='41')

        result = site1.set_has(rack_4.handle_id)
        self.assertEqual(result['Has'][0]['created'], True)
        children = site1.get_has()
        self.assertEqual(len(children['Has']), 3)

        # Do not accept duplicates
        result = site1.set_has(rack_4.handle_id)
        self.assertEqual(result['Has'][0]['created'], False)
        children = site1.get_has()
        self.assertEqual(len(children['Has']), 3)

    def test_set_responsible_for_location_model(self):
        rack_4 = core.get_node_model(self.neo4jdb, handle_id='41')
        provider_2 = core.get_node_model(self.neo4jdb, handle_id='39')

        result = rack_4.set_responsible_for(provider_2.handle_id)
        self.assertEqual(result['Responsible_for'][0]['created'], True)
        relations = rack_4.get_relations()
        self.assertEqual(len(relations['Responsible_for']), 1)
        self.assertEqual(relations['Responsible_for'][0]['node'].handle_id, provider_2.handle_id)

        # Do not accept duplicates
        result = rack_4.set_responsible_for(provider_2.handle_id)
        self.assertEqual(result['Responsible_for'][0]['created'], False)
        relations = rack_4.get_relations()
        self.assertEqual(len(relations['Responsible_for']), 1)

    def test_set_parent(self):
        organization1 = core.get_node_model(self.neo4jdb, handle_id='113')
        organization2 = core.get_node_model(self.neo4jdb, handle_id='114')
        organization2.set_parent(organization1.handle_id)
        relations = organization2.get_relations()
        self.assertIsInstance(relations['Parent_of'][0]['node'], models.OrganizationModel)

    def test_get_outgoing_relations(self):
        contact1 = core.get_node_model(self.neo4jdb, handle_id='115')
        relations = contact1.get_outgoing_relations()
        self.assertIsInstance(relations['Works_for'][0]['node'], models.OrganizationModel)

        expected_value = self.role_name_1
        self.assertEquals(relations['Works_for'][0]['relationship']['name'], expected_value)

    def test_contact_role_org(self):
        contact1 = core.get_node_model(self.neo4jdb, handle_id='115')
        organization1 = core.get_node_model(self.neo4jdb, handle_id='113')

        # unlink
        models.RoleRelationship.unlink_contact_with_role_organization(contact1.handle_id,
            organization1.handle_id, self.role_name_1, self.neo4jdb)

        relations = contact1.get_outgoing_relations()
        self.assertEquals(relations, {})

        # relink
        models.RoleRelationship.link_contact_organization(contact1.handle_id,
            organization1.handle_id, self.role_name_1, self.neo4jdb)
        relations = contact1.get_outgoing_relations()
        expected_value = self.role_name_1
        self.assertEquals(relations['Works_for'][0]['relationship']['name'], expected_value)

        # get contact which holds this role in this organization
        contact_handle_id = models.RoleRelationship.get_contact_with_role_in_organization(
            organization1.handle_id, self.role_name_1, self.neo4jdb)
        self.assertEqual(contact_handle_id, contact1.handle_id)

        # get the relation of a organization with a specific role
        relation = models.RoleRelationship.get_role_relation_from_organization(
            organization1.handle_id, self.role_name_1, self.neo4jdb)
        self.assertEqual(relations['Works_for'][0]['relationship_id'], relation.id)

        # get the relation between contact and organization with a specific role
        relation = models.RoleRelationship.get_role_relation_from_contact_organization(
            organization1.handle_id, self.role_name_1, contact1.handle_id, self.neo4jdb)
        self.assertEqual(relations['Works_for'][0]['relationship_id'], relation.id)

        # check role list
        role_list = models.RoleRelationship.get_all_role_names(self.neo4jdb)
        self.assertEquals(role_list, [self.role_name_1, self.role_name_2])

        # role name change
        new_role_name = u"Abuse Manager"
        models.RoleRelationship.update_roles_withname(self.role_name_2,
            new_role_name, self.neo4jdb)
        role_list = models.RoleRelationship.get_all_role_names(self.neo4jdb)
        self.assertEquals(role_list, [self.role_name_1, new_role_name])

        # delete role
        models.RoleRelationship.delete_roles_withname(new_role_name,
            self.neo4jdb)
        role_list = models.RoleRelationship.get_all_role_names(self.neo4jdb)
        self.assertEquals(role_list, [self.role_name_1])

    def test_uses_a_procedure(self):
        organization1 = core.get_node_model(self.neo4jdb, handle_id='113')
        organization2 = core.get_node_model(self.neo4jdb, handle_id='114')
        procedure1 = core.get_node_model(self.neo4jdb, handle_id='119')
        procedure2 = core.get_node_model(self.neo4jdb, handle_id='120')

        relations1 = procedure1.get_relations()
        self.assertIsInstance(relations1['Uses_a'][0]['node'], models.OrganizationModel)

        organization2.add_procedure(procedure2.handle_id)
        relations2 = procedure2.get_relations()
        self.assertIsInstance(relations2['Uses_a'][0]['node'], models.OrganizationModel)

    def test_organization_outgoingrel(self):
        organization1 = core.get_node_model(self.neo4jdb, handle_id='113')
        relations1 = organization1.get_outgoing_relations()
        self.assertIsInstance(relations1['Uses_a'][0]['node'], models.ProcedureModel)

    def test_organization_contacts(self):
        organization1 = core.get_node_model(self.neo4jdb, handle_id='113')
        contacts = organization1.get_contacts()
        contact1 = core.get_node_model(self.neo4jdb, handle_id='115')
        self.assertEqual(contact1.handle_id, contacts[0]['handle_id'])
        self.assertEqual(contact1.data['name'], contacts[0]['name'])

    def test_groups(self):
        group1 = core.get_node_model(self.neo4jdb, handle_id='121')
        contact1 = core.get_node_model(self.neo4jdb, handle_id='115')
        group1.add_member(contact1.handle_id)
        relations = contact1.get_outgoing_relations()
        self.assertIsInstance(relations['Member_of'][0]['node'], models.GroupModel)

    # TODO: EquipmentModel get_ports should probably work as CommonQueries get_ports
    def test_get_ports_equipment_model(self):
        odf1 = core.get_node_model(self.neo4jdb, handle_id='23')
        ports = odf1.get_ports()
        self.assertIsInstance(ports, dict)
        self.assertEqual(len(ports['Has']), 1)
        for rel_type, items in ports.items():
            self.assertEqual(len(items), 1)

    def test_get_port_equipment_model(self):
        router1 = core.get_node_model(self.neo4jdb, handle_id='1')
        ports = router1.get_port('Port1')
        self.assertEqual(len(ports['Has']), 1)
        self.assertIsInstance(ports['Has'][0]['node'], models.PortModel)
        self.assertEqual(ports['Has'][0]['node'].data['name'], 'Port1')

    def test_get_dependent_as_types_equipment_model(self):
        optical_node2 = core.get_node_model(self.neo4jdb, handle_id='16')
        dependents = optical_node2.get_dependent_as_types()
        self.assertEqual(dependents['direct'], [])
        self.assertEqual(dependents['links'][0]['name'], 'Optical Link2')
        self.assertEqual(dependents['oms'], [])
        self.assertEqual(dependents['paths'][0]['name'], 'Optical Path1')
        self.assertEqual(dependents['services'][0]['name'], 'Service2')

    def test_get_connections_equipment_model(self):
        odf2 = core.get_node_model(self.neo4jdb, handle_id='25')
        connections = odf2.get_connections()
        self.assertEqual(len(connections), 4)
        for connection in connections:
            self.assertIsNotNone(connection['porta'])
            self.assertIsNotNone(connection['cable'])

    def test_get_connections_subequipment_model(self):
        port4 = core.get_node_model(self.neo4jdb, handle_id='24')
        connections = port4.get_connections()
        self.assertEqual(len(connections), 2)
        for connection in connections:
            self.assertIsNotNone(connection['porta'])
            self.assertIsNotNone(connection['cable'])

    def test_get_dependent_as_types_host_model(self):
        host1 = core.get_node_model(self.neo4jdb, handle_id='32')
        dependents = host1.get_dependent_as_types()
        self.assertEqual(dependents['direct'][0]['name'], 'Host2')
        self.assertEqual(dependents['links'], [])
        self.assertEqual(dependents['oms'], [])
        self.assertEqual(dependents['paths'], [])
        self.assertEqual(dependents['services'], [])

    def test_get_host_services_host_model(self):
        host1 = core.get_node_model(self.neo4jdb, handle_id='32')
        host_services = host1.get_host_services()
        self.assertEqual(len(host_services['Depends_on']), 1)
        self.assertIsInstance(host_services['Depends_on'][0]['node'], models.LogicalModel)
        self.assertEqual(host_services['Depends_on'][0]['node'].data['name'], 'Host Service1')
        self.assertEqual(host_services['Depends_on'][0]['relationship']['ip_address'], '127.0.0.1')
        self.assertEqual(host_services['Depends_on'][0]['relationship']['port'], '80')
        self.assertEqual(host_services['Depends_on'][0]['relationship']['protocol'], 'tcp')

    def test_set_and_get_host_service_host_model(self):
        host2 = core.get_node_model(self.neo4jdb, handle_id='33')
        host_service1 = core.get_node_model(self.neo4jdb, handle_id='43')

        result = host2.set_host_service(host_service1.handle_id, ip_address='127.0.0.1', port='443', protocol='tcp')
        self.assertEqual(result['Depends_on'][0]['created'], True)
        host_services = host2.get_host_services()
        self.assertEqual(len(host_services['Depends_on']), 1)

        # TODO: Fix duplicates

    def test_get_units_port_model(self):
        port1 = core.get_node_model(self.neo4jdb, handle_id='2')
        units = port1.get_units()
        self.assertEqual(units['Part_of'][0]['node'].handle_id, '3')

    def test_get_unit_port_model(self):
        port1 = core.get_node_model(self.neo4jdb, handle_id='2')
        units = port1.get_unit('Unit1')
        self.assertEqual(units['Part_of'][0]['node'].handle_id, '3')

    def test_get_connected_to_port_model(self):
        port4 = core.get_node_model(self.neo4jdb, handle_id='24')
        connected_to = port4.get_connected_to()
        self.assertIn(connected_to['Connected_to'][0]['node'].handle_id, ['28', '30'])

    def test_get_connection_path_port_model(self):
        port4 = core.get_node_model(self.neo4jdb, handle_id='24')
        connection_path = port4.get_connection_path()
        self.assertEqual(len(connection_path), 7)

    def test_get_child_form_data_router_model(self):
        physical1 = core.get_node_model(self.neo4jdb, handle_id='1')
        child_form_data = physical1.get_child_form_data(node_type='Port')
        self.assertEqual(child_form_data[0]['handle_id'], '2')
        self.assertEqual(child_form_data[0]['name'], 'Port1')
        self.assertEqual(child_form_data[0]['description'], None)
        self.assertEqual(child_form_data[0]['labels'], [u'Node', u'Physical', u'Port'])

    def test_get_peering_groups_peering_partner_model(self):
        peering_partner1 = core.get_node_model(self.neo4jdb, handle_id='8')
        host_services = peering_partner1.get_peering_groups()
        self.assertEqual(len(host_services['Uses']), 1)
        self.assertIsInstance(host_services['Uses'][0]['node'], models.PeeringGroupModel)
        self.assertEqual(host_services['Uses'][0]['node'].data['name'], 'Peering Group1')
        self.assertEqual(host_services['Uses'][0]['relationship']['ip_address'], '127.0.0.1')

    def test_set_and_get_peering_group_peering_partner_model(self):
        peering_partner1 = core.get_node_model(self.neo4jdb, handle_id='8')
        peering_group2 = core.get_node_model(self.neo4jdb, handle_id='44')

        peering_partner1.set_peering_group(peering_group2.handle_id, ip_address='127.0.0.2')
        peering_groups = peering_partner1.get_peering_group(peering_group2.handle_id, ip_address='127.0.0.2')
        self.assertEqual(len(peering_groups['Uses']), 1)

        # TODO: Fix duplicates

    def test_set_and_get_group_dependency_peering_group_model(self):
        peering_group2 = core.get_node_model(self.neo4jdb, handle_id='44')
        unit2 = core.get_node_model(self.neo4jdb, handle_id='5')

        peering_group2.set_group_dependency(unit2.handle_id, ip_address='127.0.0.3')
        dependencies = peering_group2.get_group_dependency(unit2.handle_id, ip_address='127.0.0.3')
        self.assertEqual(len(dependencies['Depends_on']), 1)

        # TODO: Fix duplicates

    def test_get_connected_equipment_cable_model(self):
        cable1 = core.get_node_model(self.neo4jdb, handle_id='28')
        connections = cable1.get_connected_equipment()
        self.assertEqual(len(connections), 2)
        for connection in connections:
            self.assertIsNotNone(connection['port'])
            self.assertIsNotNone(connection['end'])
            self.assertIsNotNone(connection['location'])
            self.assertIsNotNone(connection['site'])

    def test_get_dependent_as_types_cable_model(self):
        cable1 = core.get_node_model(self.neo4jdb, handle_id='28')
        dependents = cable1.get_dependent_as_types()

        for optical_link in dependents['links']:
            self.assertTrue(optical_link['name'] in ['Optical Link1', 'Optical Link2'])
        self.assertEqual(dependents['oms'], [])
        self.assertEqual(dependents['paths'][0]['name'], 'Optical Path1')
        self.assertEqual(dependents['services'][0]['name'], 'Service2')

    def test_get_services_cable_model(self):
        cable1 = core.get_node_model(self.neo4jdb, handle_id='28')
        services = cable1.get_services()
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]['service']['name'], 'Service2')
        self.assertIsInstance(services[0]['users'], list)
        self.assertEqual(services[0]['users'][0]['name'], 'Customer2')

    def test_get_connection_path_cable_model(self):
        cable1 = core.get_node_model(self.neo4jdb, handle_id='28')
        connection_path = cable1.get_connection_path()
        self.assertEqual(len(connection_path), 7)

    def test_set_connected_to_cable_model(self):
        cable6 = core.get_node_model(self.neo4jdb, handle_id='45')
        port7 = core.get_node_model(self.neo4jdb, handle_id='27')

        result = cable6.set_connected_to(port7.handle_id)
        self.assertEqual(result['Connected_to'][0]['created'], True)
        relationships = cable6.relationships
        self.assertEqual(len(relationships['Connected_to']), 1)

        # Do not accept duplicates
        result = cable6.set_connected_to(port7.handle_id)
        self.assertEqual(result['Connected_to'][0]['created'], False)
        relationships = cable6.relationships
        self.assertEqual(len(relationships['Connected_to']), 1)

    def test_get_placement_path_unit_model(self):
        unit1 = core.get_node_model(self.neo4jdb, handle_id='3')
        placement_path = unit1.get_placement_path()
        self.assertEqual(placement_path['placement_path'][0]['name'], 'Router1')
        self.assertEqual(placement_path['placement_path'][1]['name'], 'Port1')

    def test_get_location_path_unit_model(self):
        unit1 = core.get_node_model(self.neo4jdb, handle_id='3')
        location_path = unit1.get_location_path()
        self.assertEqual(location_path['location_path'][0]['name'], 'Site1')
        self.assertEqual(location_path['location_path'][1]['name'], 'Rack1')
        self.assertEqual(location_path['location_path'][2]['name'], 'Router1')
        self.assertEqual(location_path['location_path'][3]['name'], 'Port1')

    def test_get_customers_service_model(self):
        service2 = core.get_node_model(self.neo4jdb, handle_id='9')
        customers = service2.get_customers()
        self.assertEqual(len(customers['customers']), 1)
        self.assertIsInstance(customers['customers'][0]['node'], models.CustomerModel)

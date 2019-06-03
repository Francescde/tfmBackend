import unittest
import os
import copy
os.chdir('..')
from MapHandeler import MapHandeler

def getGraphKeys( graph, end, start, vehicle):
    route = [end]
    key, j,vehicle = graph.findPredecesor(graph.getKey(end),vehicle)
    route.append(j)
    while j != start:
        #print(vehicle)
        key, j, vehicle = graph.findPredecesor(key,vehicle)
        route.append(j)
    return route

def getVehicles( graph, end, start, vehicle):
    route = [vehicle]
    key, j,vehicle = graph.findPredecesor(graph.getKey(end),vehicle)
    route.append(vehicle)
    while j != start:
        #print(j)
        key, j, vehicle = graph.findPredecesor(key,vehicle)
        route.append(vehicle)
    return route

class TestStringMethods(unittest.TestCase):

    def test_readGraff(self):
        from Tests.FakesVehicles.FakeVehicles import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("maps/connexioGRAPH2.osm", 3007, vehicles)
        start=graph.getNearestNode('41.60448710003', '1.84747999968')
        #start=graph.getNearestNode(lat, lon)
        ends=[-143102, -170904, -123204, -107948, -81882, -44288, -50156]
        graph.solve(start,ends)
        routes={}
        for end in ends:
            routes[str(end) + "To_Position"] =graph.getRoute(end,start,0)
        self.assertTrue(True)

    def test_if_sum_larger_than_direct_root_take_sum_of_nodes(self):
        from Tests.FakesVehicles.FakeVehiclesJustWalking import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf.osm", 7, vehicles)
        start = -26176
        ends = [-26182, -29888]
        graph.solve(start, ends)
        k=0
        for end in ends:
            route = getGraphKeys(graph,end,start,0)
            if k==0:
                self.assertEqual([end,-26181,-26180,-26179,-26178,start],route)
            else:
                self.assertEqual([end,start],route)
            k=k+1

    def test_if_sum_larger_than_direct_root_take_direct_root(self):
        from Tests.FakesVehicles.FakeVehiclesJustWalking import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf2.osm", 7, vehicles)
        start = -26176
        ends = [-26182, -29888]
        graph.solve(start, ends)
        k=0
        for end in ends:
            route = getGraphKeys(graph,end,start,0)
            if k==0:
                self.assertEqual([end,-26179,-26178,start],route)
            else:
                self.assertEqual([end,start],route)
            k=k+1

    def test_if_route_car_is_better_take_car(self):
        from Tests.FakesVehicles.FakeVehicles import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf3.osm", 7, vehicles)
        start = -26176
        ends = [-26182, -29888]
        graph.solve(start, ends)
        k=0
        for end in ends:
            routeCar = getGraphKeys(graph,end,start,1)
            routeWalk = getGraphKeys(graph,end,start,0)
            if k==0:
                self.assertEqual([end,-26181,-26180,-26179,-26178,start],routeCar)
                self.assertEqual([end,-26179,-26178,start],routeWalk)
            else:
                self.assertEqual([end,start],routeCar)
            k=k+1



    def test_if_route_walk_is_better_walk(self):
        from Tests.FakesVehicles.FakeVehicles import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf4.osm", 7, vehicles)
        start = -26176
        ends = [-26182, -29888]
        graph.solve(start, ends)
        k=0
        for end in ends:
            route = getVehicles(graph,end,start,1)
            if k==0:
                self.assertEqual([1,0],route)
            else:
                self.assertEqual([1,1],route)
            k=k+1


    def test_if_you_leaveTheCar_you_cant_take_it_again(self):
        from Tests.FakesVehicles.FakeVehicles import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf5.osm", 7, vehicles)
        start = -26176
        ends = [-26182]
        graph.solve(start, ends)
        route = getVehicles(graph,ends[0],start,1)
        routek = getGraphKeys(graph,ends[0],start,1)
        self.assertEqual([ends[0],-26181,-26180,-26179,-26178,start],routek)
        self.assertEqual([1, 1, 1, 0, 0, 0], route)


    def test_if_you_leaveTheCar_you_can_take_it_again_if_car_is_allowed(self):
        from Tests.FakesVehicles.FakeVehicles import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf5.osm", 7, vehicles)
        start = -26176
        ends = [-26182]
        graph.addVehicle(1,-26178)
        graph.solve(start, ends)
        route = getVehicles(graph,ends[0],start,1)
        self.assertEqual([1, 1, 1, 0, 1, 1], route)
        #self.assertEqual([ends[0],-26181,-26180,-26179,-26178,start],route)


    def test_if_you_leaveTheCar_you_can_take_it_again_if_BRP_is_allowed(self):
        from Tests.FakesVehicles.FakeVehicles import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf5.osm", 7, vehicles)
        start = -26176
        ends = [-26182]
        graph.addVehicle(2,-26178)
        graph.solve(start, ends)
        route = getVehicles(graph,ends[0],start,1)
        routek = getGraphKeys(graph,ends[0],start,1)
        #self.assertEqual([ends[0],-26181,-26180,-26179,-26178,start],routek)
        self.assertEqual([1, 1, 1, 0, 0, 2], route)
        #self.assertEqual([ends[0],-26181,-26180,-26179,-26178,start],route)


    def test_if_you_leaveTheCar_you_can_take_it_again_if_4x4_is_allowed(self):
        from Tests.FakesVehicles.FakeVehicles import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf5.osm", 7, vehicles)
        graph.addVehicle(3,-26178)
        start = -26176
        ends = [-26182]
        graph.solve(start, ends)
        route = getVehicles(graph,ends[0],start,1)
        self.assertEqual([1, 1, 1, 0, 0, 3], route)
        #self.assertEqual([ends[0],-26181,-26180,-26179,-26178,start],route)




    def test_if_you_leaveTheCar_if_you_must_pass_oneway_restricted_path(self):
        from Tests.FakesVehicles.FakeVehicles import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf7.osm", 7, vehicles)
        start = -26176
        ends = [-26182]
        graph.solve(start, ends)
        route = getVehicles(graph,ends[0],start,1)
        routek = getGraphKeys(graph,ends[0],start,1)

        self.assertEqual([ends[0],-26181,-26180,-26179,-26178,start],routek)
        self.assertEqual([1, 1, 1, 0, 0, 0], route)
        #self.assertEqual([ends[0],-26181,-26180,-26179,-26178,start],route)


    def test_if_you_leaveTheCar_if_you_must_pass_oneway_restricted_path2(self):
        from Tests.FakesVehicles.FakeVehicles import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf7.osm", 7, vehicles)
        start = -26176
        ends = [-26182]
        graph.solve(start, ends)
        route = getVehicles(graph,ends[0],start,1)
        routek = getGraphKeys(graph,ends[0],start,1)
        self.assertEqual([ends[0],-26181,-26180,-26179,-26178,start],routek)
        self.assertEqual([1, 1, 1, 0, 0, 0], route)


    def test_if_you_dont_leave_Car_if_you_must_pass_oneway_opiste_restricted_path(self):
        from Tests.FakesVehicles.FakeVehicles import vehicles
        mapHandeler=MapHandeler()
        graph = mapHandeler.read_graph("Tests/maps/simpleGraf7.osm", 7, vehicles)
        start = -26182
        ends = [-26176]
        graph.solve(start, ends)
        route = getVehicles(graph,ends[0],start,1)
        routek = getGraphKeys(graph,ends[0],start,1)
        #self.assertEqual([ends[0],-26181,-26180,-26179,-26178,start],routek)
        self.assertEqual([1, 1, 1, 1, 1, 1], route)




if __name__ == '__main__':
    unittest.main()
import sys
import json


class Link:

    @classmethod
    def createLink(cls, start, end, capacity):
        return cls(start, end, capacity)

    def __init__(self, start, end, capacity):
        self.start = start
        self.end = end
        self.capacity = float(capacity)
        self.used = 0
        self.demands = []

    def demand(self, amount):
        if not self.canDemand(amount):
            return False

        self.allocate(amount)
        return True

    def canDemand(self, amount):
        return self.used + amount <= self.capacity

    def allocate(self, amount):
        self.used += amount

    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end

    def __repr__(self):
        return "<Link {}<->{} {}/{}>".format(self.getStart(), self.getEnd(), self.used, self.capacity)

    def getEndpoints(self):
        ends = [self.getStart(), self.getEnd()]
        ends.sort()
        return ends

    def free(self, amount):
        self.used -= amount


class Route:

    @classmethod
    def createRoute(cls, linkCollection, points):
        usedLinks = []
        for i in range(len(points) - 1):

            pointsSorted = [points[i], points[i+1]]
            pointsSorted.sort()
            linkIndex = [link.getEndpoints()
                         for link in linkCollection].index(pointsSorted)

            usedLinks.append(linkCollection[linkIndex])

        ends = [points[0], points[-1]]
        return cls(usedLinks, ends, points)

    def __init__(self, links, endpoints, points):
        self.links = links
        self.endpoints = endpoints
        self.points = points

    def demand(self, amount):
        if not self.canDemand(amount):
            return False

        self.allocate(amount)
        return True

    def canDemand(self, amount):
        return all([link.canDemand(amount) for link in self.links])

    def allocate(self, amount):
        [link.demand(amount) for link in self.links]

    def __repr__(self):
        return "<Route {}>".format([link.__repr__() for link in self.links])

    def getEndpoints(self):
        return self.endpoints

    def getStart(self):
        return self.getEndpoints()[0]

    def getEnd(self):
        return self.getEndpoints()[1]

    def free(self, amount):
        [link.free(amount) for link in self.links]

    @staticmethod
    def getRoute(endpoints, routes):
        index = [route.getEndpoints() for route in routes].index(endpoints)
        return routes[index]


class Simulation:

    def __init__(self, duration, demands, routes):
        self.duration = duration
        self.time = 0

        self.demands = demands
        self.allocations = []

        self.routes = routes

        self.printer = Printer()

    def run(self):
        while self.time <= self.duration:
            self.free()

            for demand in self.demands:
                if demand['start-time'] != self.time:
                    continue

                success = self.allocate(
                    demand['demand'], demand['end-points'], demand['end-time'])
                
                self.printer.allocation(
                    demand['end-points'], self.time, success)

            self.time += 1

    def allocate(self, amount, points, until):
        route = Route.getRoute(points, self.routes)
        result = route.demand(amount)

        if result:
            self.storeDemand(route, amount, until)

        return result

    def storeDemand(self, route, amount, until):
        self.allocations.append({
            'route': route,
            'amount': amount,
            'until': until
        })

    def free(self):
        for allocation in self.allocations:
            if allocation['until'] != self.time:
                continue

            allocation['route'].free(allocation['amount'])
            self.allocations.remove(allocation)
            self.printer.unAllocation(
                allocation['route'].getEndpoints(), self.time)

    @classmethod
    def createSimulationFromFile(cls):
        data = getInput()
        linkCollection = populateLinks(data['links'])
        routes = populateRoutes(linkCollection, data['possible-circuits'])

        return cls.createFromSimulationData(data['simulation'], routes)


    @classmethod
    def createFromSimulationData(cls, simulationData, routes):
        duration = simulationData['duration']
        demands = simulationData['demands']
        return cls(duration, demands, routes)


class Printer:

    def __init__(self):
        self.eventCount = 0

    def allocation(self, endpoints, time, succes):
        self.eventCount += 1
        print("{}. igény foglalás:: {}<->{} st:{} – {}".format(
            self.eventCount,
            endpoints[0],
            endpoints[1],
            time,
            ('sikeres' if succes else 'sikertelen')
        ))

    def unAllocation(self, endpoints, time):
        self.eventCount += 1
        print("{}. igény felszabadítás: {}<->{} st:{}".format(
            self.eventCount,
            endpoints[0],
            endpoints[1],
            time
        ))




def getInput():
    inputFile = sys.argv[1]

    with open(inputFile, 'r') as f:
        data = json.load(f)

    return data


def populateLinks(links):
    return [Link.createLink(link['points'][0], link['points'][1], link['capacity']) for link in links]


def populateRoutes(links, circuits):
    routes = [Route.createRoute(links, points) for points in circuits]
    return routes


if __name__ == "__main__":

    simulation = Simulation.createSimulationFromFile()
    simulation.run()

    # print(len(routes))
    # [print('->'.join(route.points)) for route in routes]
    # can = [route.demand(10) for route in routes]
    # [print(route) for route in routes]
    # print(can)

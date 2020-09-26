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

    data = getInput()
    linkCollection = populateLinks(data['links'])
    routes = populateRoutes(linkCollection, data['possible-circuits'])

    print(len(routes))
    [print('->'.join(route.points)) for route in routes]
    can = [route.demand(10) for route in routes]
    [print(route) for route in routes]
    print(can)

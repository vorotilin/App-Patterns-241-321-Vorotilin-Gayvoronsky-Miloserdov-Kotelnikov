import heapq
from app.models import RouteGraph

class ShortestPathFinder:
    def __init__(self):
        self.graph = {}
    
    def load_from_db(self):
        """Загружает граф из базы данных"""
        self.graph = {}
        for edge in RouteGraph.objects.all():
            self.graph.setdefault(edge.from_node, []).append((edge.to_node, edge.distance))
            self.graph.setdefault(edge.to_node, []).append((edge.from_node, edge.distance))
    
    def add_edge(self, from_node, to_node, distance):
        self.graph.setdefault(from_node, []).append((to_node, distance))
        self.graph.setdefault(to_node, []).append((from_node, distance))
    
    def find_shortest_path(self, start, end):
        """Алгоритм A* (упрощённая версия без эвристики = Dijkstra)"""
        heap = [(0, start, [start])]
        visited = set()
        
        while heap:
            cost, node, path = heapq.heappop(heap)
            
            if node in visited:
                continue
            visited.add(node)
            
            if node == end:
                return path, cost
            
            for neighbor, dist in self.graph.get(node, []):
                if neighbor not in visited:
                    heapq.heappush(heap, (cost + dist, neighbor, path + [neighbor]))
        
        return None, float('inf')
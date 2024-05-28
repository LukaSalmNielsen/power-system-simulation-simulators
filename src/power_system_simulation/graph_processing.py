"""
Graph Processing Assignment

This script defines a GraphProcessor class for processing undirected graphs. 
It provides functionality to initialize a graph, find downstream vertices of an edge, 
and identify alternative edges for ensuring graph connectivity.

Authors: Rick Eversdijk, ...
Date: 30/04/2024

"""

import copy
from typing import List, Tuple

import networkx as nx


class IDNotFoundError(Exception):
    """Exception raised when source_vertex_id is not a valid vertex id"""


class InputLengthDoesNotMatchError(Exception):
    """2. Exception raised when the length of the edge_enabled does not match the input lists edge_ids."""


class IDNotUniqueError(Exception):
    """1. Exception raised when there is duplicate vertex or edge id"""


class GraphNotFullyConnectedError(Exception):
    """Exception raised when there is a non connected node"""


class GraphCycleError(Exception):
    """Exception raised when the graph contains a cycle"""


class EdgeAlreadyDisabledError(Exception):
    """Exception raised when an edge is already disabled"""


class GraphProcessor:
    """
    A class for processing undirected graphs.

    This class provides functionality to initialize a graph, find downstream vertices
    of an edge, and identify alternative edges for ensuring graph connectivity.

    Attributes:
        graph: A NetworkX graph representing the processed graph.
    """

    def __init__(
        self,
        vertex_ids: List[int],
        edge_ids: List[int],
        edge_vertex_id_pairs: List[Tuple[int, int]],
        edge_enabled: List[bool],
        source_vertex_id: int,
    ) -> None:
        self.vertex_ids = vertex_ids
        self.edge_ids = edge_ids
        self.edge_vertex_id_pairs = edge_vertex_id_pairs
        self.edge_enabled = edge_enabled
        self.source_vertex_id = source_vertex_id

        # 1. check for redundant vertex or edge ids
        seen_vertex = set()
        for i in vertex_ids:
            if i in seen_vertex:
                raise IDNotUniqueError("vertex and edge ids are not unique.")
            seen_vertex.add(i)

        seen_edge = set()
        for i in edge_ids:
            if i in seen_edge:
                raise IDNotUniqueError("vertex and edge ids are not unique.")
            seen_edge.add(i)

        # 2. check if length of edge_vertex_id_pairs is equal to length of edge_ids
        if len(edge_vertex_id_pairs) != len(edge_ids):
            raise InputLengthDoesNotMatchError("The amount of vertex pairs is not equal to the amount of edges.")

        # 3. check if edge_vertex_id_pairs contain existing vertex ids
        for pair in edge_vertex_id_pairs:
            for vertex_id in pair:
                if vertex_id not in vertex_ids:
                    raise IDNotFoundError("Vertex ID present in edge_vertex_id_pairs does not exist.")

        # 4. Check if lengths of input lists match
        if len(edge_enabled) != len(edge_ids):
            raise InputLengthDoesNotMatchError("Length of edge IDs does not match number initialized edges.")

        # 5. Check if source vertex exists in the graph
        if source_vertex_id not in vertex_ids:
            raise IDNotFoundError("Source vertex ID not found.")

        # Initialize a NetworkX graph
        self.graph = nx.Graph()

        # Add nodes/vertexes to the graph
        self.graph.add_nodes_from(vertex_ids)

        # Add edges to the graph
        for edge_pair, enabled, edge_ids in zip(edge_vertex_id_pairs, edge_enabled, edge_ids):
            if enabled:
                self.graph.add_edge(*edge_pair, id=edge_ids)

        # 6. The graph should be fully connected. (GraphNotFullyConnectedError) (with nx)
        if not nx.is_connected(self.graph):
            raise GraphNotFullyConnectedError("Graph not fully connected")

        # 7. The graph should not contain cycles. (GraphCycleError)
        # self.graph.add_edge(2, 6) #(uncomment to test)
        try:
            nx.find_cycle(self.graph)
            raise GraphCycleError("The graph contains cycles.")
        except nx.NetworkXNoCycle:
            pass

    def find_downstream_vertices(self, starting_edge_id: int) -> List[int]:
        # Verify that the edge ID exists
        if starting_edge_id not in self.edge_ids:
            raise IDNotFoundError("The edge ID provided does not exist.")

        # Check if the edge is already disabled, which would be incorrect for this operation
        index = self.edge_ids.index(starting_edge_id)
        if not self.edge_enabled[index]:
            return []
        # Get the vertices of the edge
        u, v = self.edge_vertex_id_pairs[index]
    
        # Simulate the edge being disabled by temporarily removing it
        self.graph.remove_edge(u, v)
    
        # Find all connected components after the removal
        components = list(nx.connected_components(self.graph))
    
        # Restore the edge to maintain original graph state
        self.graph.add_edge(u, v)

        # Determine which component contains the source vertex
        source_component = next(comp for comp in components if self.source_vertex_id in comp)
    
        # Return the nodes in the component that does not contain the source vertex
        for comp in components:
            if comp != source_component:
                return list(comp)

    def find_alternative_edges(self, disabled_edge_id: int) -> List[int]:

        ############################################################
        "Done by Carmelo Vella, 02/05/2024"

        # Explanaition:
        # 1. errors are checked and empty output list is initialised
        # 2. a list of ORIGINALLY disabled edges is created
        # 3. a list of UPDATED disabled edges is made with disabled_edge_id considered

        # 4. a list of edges is created: the list(zip()) functions pair each edge_id with
        # the corresponding vertex pair and status-enables/disabled
        # 5. a new list is made where disabled_edge_id considered (it becomes disabled)
        # 6. the ORIGINALLY disabled edges are taken one by one (while loop). For each
        # iteration, the edge is now ENABLED "temporarily" and a new graph is made. This graph
        # is then checked for cyclicity and completeness. If satisfactory, the ORIGINALLY disabled
        # index is added to the output list alt_list[]
        # 7. after iterations end, the output list is printed

        # 1. check if edge is not already disabled
        if disabled_edge_id not in self.edge_ids:
            raise IDNotFoundError
        if disabled_edge_id not in self.edge_enabled and disabled_edge_id in self.edge_ids:
            raise EdgeAlreadyDisabledError
        alt_list = []

        # 2. create a list of currently disabled edge IDs
        disabled_edges = [self.edge_ids[i] for i in range(len(self.edge_ids)) if not self.edge_enabled[i]]

        # 3. create copy of list and update list
        disabled_edges_new = copy.copy(disabled_edges)
        disabled_edges_new.append(disabled_edge_id)

        # 4. create list of all edges with vertex pairs, enabling and ID (vertex_pair,(dis)/(en)abled,id)
        full_edge_list = list(zip(self.edge_vertex_id_pairs, self.edge_enabled, self.edge_ids))
        # 5. the edge with id = disabled_edge_id is disabled and list is updated
        new_full_edge_list = [
            (vertex_pair, False if edge_id == disabled_edge_id else enabled, edge_id)
            for vertex_pair, enabled, edge_id in full_edge_list
        ]

        # 6. the originally disabled edges are iterated through and enabled in sequence
        # iterate disabled_edges:
        i = 0
        while i < len(disabled_edges):

            # for each originally disabled edge, a new graph is created in which a new list of edges is
            # created (i.e. said edge is now enabled)
            temp_full_edge_list = [
                (vertex_pair, True if edge_id == disabled_edges[i] else enabled, edge_id)
                for vertex_pair, enabled, edge_id in new_full_edge_list
            ]

            # new graph is made // all vertices are added // edges are added from previously updated edge list
            new_graph = nx.Graph()
            new_graph.add_nodes_from(self.vertex_ids)

            for vertex_pair, enabled, edge_id in temp_full_edge_list:
                if enabled:
                    new_graph.add_edge(*vertex_pair, id=self.edge_ids)

            nx.draw(new_graph)

        try:
            nr_cycles = nx.find_cycle(new_graph)
        except nx.NetworkXNoCycle:
            nr_cycles = 0
        connected = nx.is_connected(new_graph)

        if nr_cycles == 0 and connected is True:
            alt_list.append(disabled_edges[i])
            i += 1
        # 7. print output
        return alt_list

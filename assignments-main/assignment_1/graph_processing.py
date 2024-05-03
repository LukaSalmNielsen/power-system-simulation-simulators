"""
Graph Processing Assignment

This script defines a GraphProcessor class for processing undirected graphs. 
It provides functionality to initialize a graph, find downstream vertices of an edge, 
and identify alternative edges for ensuring graph connectivity.

Authors: Rick Eversdijk, ...
Date: 30/04/2024

"""
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import contextlib
from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx


class IDNotFoundError(Exception):
    """Exception raised when source_vertex_id is not a valid vertex id"""

    pass


class InputLengthDoesNotMatchError(Exception):
    """2. Exception raised when the length of the edge_enabled does not match the input lists edge_ids."""

    pass


class IDNotUniqueError(Exception):
    """1. Exception raised when there is duplicate vertex or edge id"""

    pass


class GraphNotFullyConnectedError(Exception):
    pass


class GraphCycleError(Exception):
    pass


class EdgeAlreadyDisabledError(Exception):
    pass


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
        """
        Initialize a graph processor object with an undirected graph.
        Only the edges which are enabled are taken into account.

        Args:
            vertex_ids: list of vertex ids
            edge_ids: list of edge ids
            edge_vertex_id_pairs: list of tuples of two integer
                Each tuple is a vertex id pair of the edge.
            edge_enabled: list of bools indicating of an edge is enabled or not
            source_vertex_id: vertex id of the source in the graph

        Raises:
            1. vertex_ids and edge_ids should be unique. (IDNotUniqueError)
            2. edge_vertex_id_pairs should have the same length as edge_ids. (InputLengthDoesNotMatchError)
            3. edge_vertex_id_pairs should contain valid vertex ids. (IDNotFoundError)
            4. edge_enabled should have the same length as edge_ids. (InputLengthDoesNotMatchError)
            5. source_vertex_id should be a valid vertex id. (IDNotFoundError)
            6. The graph should be fully connected. (GraphNotFullyConnectedError)
            7. The graph should not contain cycles. (GraphCycleError)
        """

        # 1. check for redundant vertex or edge ids
        seen_vertex = set()
        for id in vertex_ids:
            if id in seen_vertex:
                raise IDNotUniqueError("vertex and edge ids are not unique.")
            seen_vertex.add(id)

        seen_edge = set()
        for id in edge_ids:
            if id in seen_edge:
                raise IDNotUniqueError("vertex and edge ids are not unique.")
            seen_edge.add(id)

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

        # 6. The graph should be fully connected. (GraphNotFullyConnectedError) (with nx)
        # tests the below code by adding a disconnected node
        # self.graph.add_node(5) (uncomment to test)
        if not nx.is_connected(self.graph):
            raise GraphNotFullyConnectedError("Graph not fully connected")

        # 7. The graph should not contain cycles. (GraphCycleError)
        # self.graph.add_edge(2, 6) #(uncomment to test)
        try:
            nx.find_cycle(self.graph)
            raise GraphCycleError("The graph contains cycles.")
        except nx.NetworkXNoCycle:
            pass

        # Initialize a NetworkX graph
        self.graph = nx.Graph()

        # Add nodes/vertexes to the graph
        self.graph.add_nodes_from(vertex_ids)

        # Add edges to the graph
        for edge_pair, enabled, edge_ids in zip(edge_vertex_id_pairs, edge_enabled, edge_ids):
            if enabled:
                self.graph.add_edge(*edge_pair, id=edge_ids)

    def find_downstream_vertices(self, edge_id: int) -> List[int]:
        """
        Given an edge id, return all the vertices which are in the downstream of the edge,
            with respect to the source vertex.
            Including the downstream vertex of the edge itself!

        Only enabled edges should be taken into account in the analysis.
        If the given edge_id is a disabled edge, it should return empty list.
        If the given edge_id does not exist, it should raise IDNotFoundError.


        For example, given the following graph (all edges enabled):

            vertex_0 (source) --edge_1-- vertex_2 --edge_3-- vertex_4

        Call find_downstream_vertices with edge_id=1 will return [2, 4]
        Call find_downstream_vertices with edge_id=3 will return [4]

        Args:
            edge_id: edge id to be searched

        Returns:
            A list of all downstream vertices.
        """
        # put your implementation here
        pass
    
    def find_alternative_edges(self, disabled_edge_id: int) -> List[int]:
        """
        Given an enabled edge, do the following analysis:
            If the edge is going to be disabled,
                which (currently disabled) edge can be enabled to ensure
                that the graph is again fully connected and acyclic?
            Return a list of all alternative edges.
        If the disabled_edge_id is not a valid edge id, it should raise IDNotFoundError.
        If the disabled_edge_id is already disabled, it should raise EdgeAlreadyDisabledError.
        If there are no alternative to make the graph fully connected again, it should return empty list.


        For example, given the following graph:

        vertex_0 (source) --edge_1(enabled)-- vertex_2 --edge_9(enabled)-- vertex_10
                 |                               |
                 |                           edge_7(disabled)
                 |                               |
                 -----------edge_3(enabled)-- vertex_4
                 |                               |
                 |                           edge_8(disabled)
                 |                               |
                 -----------edge_5(enabled)-- vertex_6

        Call find_alternative_edges with disabled_edge_id=1 will return [7]
        Call find_alternative_edges with disabled_edge_id=3 will return [7, 8]
        Call find_alternative_edges with disabled_edge_id=5 will return [8]
        Call find_alternative_edges with disabled_edge_id=9 will return []

        Args:
            disabled_edge_id: edge id (which is currently enabled) to be disabled

        Returns:
            A list of alternative edge ids.
        """

############################################################
        'Done by Carmelo Vella, 02/05/2024'

        #Explanaition:
        #1. errors are checked and empty output list is initialised
        #2. a list of ORIGINALLY disabled edges is created
        #3. a list of UPDATED disabled edges is made with disabled_edge_id considered
        
        #4. a list of edges is created: the list(zip()) functions pair each edge_id with
        # the corresponding vertex pair and status-enables/disabled
        #5. a new list is made where disabled_edge_id considered (it becomes disabled)
        #6. the ORIGINALLY disabled edges are taken one by one (while loop). For each
        # iteration, the edge is now ENABLED "temporarily" and a new graph is made. This graph
        # is then checked for cyclicity and completeness. If satisfactory, the ORIGINALLY disabled
        #index is added to the output list alt_list[]
        #7. after iterations end, the output list is printed

        #1. check errors & output list (i.e. the alternate edges that will be enabled)
        '''if disabled_edge_id not in edge_ids:
            raise IDNotFoundError
        if disabled_edge_id not in edge_enabled and disabled_edge_id in edge_ids:
            raise EdgeAlreadyDisabledError'''
        
        alt_list = []

        #2. create a list of currently disabled edge IDs
        disabled_edges = [edge_ids[i] for i in range(len(edge_ids)) if not edge_enabled[i]]  
        
        #3. create copy of list and update list
        disabled_edges_new = copy.copy(disabled_edges)
        disabled_edges_new.append(disabled_edge_id)

        #4. create list of all edges with vertex pairs, enabling and ID (vertex_pair,(dis)/(en)abled,id)
        full_edge_list = list(zip(edge_vertex_id_pairs, edge_enabled, edge_ids))
        
        #5. the edge with id = disabled_edge_id is disabled and list is updated
        new_full_edge_list = [(vertex_pair, False if edge_id == disabled_edge_id else enabled, edge_id) for vertex_pair, enabled, edge_id in full_edge_list]
        
        
        #6. the originally disabled edges are iterated through and enabled in sequence 
        # iterate disabled_edges:
        i = 0
        while i < len(disabled_edges):

            # for each originally disabled edge, a new graph is created in which a new list of edges is 
            # created (i.e. said edge is now enabled)
            temp_full_edge_list = [(vertex_pair, True if edge_id == disabled_edges[i] else enabled, edge_id) for vertex_pair, enabled, edge_id in new_full_edge_list]
            
            # new graph is made // all vertices are added // edges are added from previously updated edge list
            new_graph = nx.Graph()
            new_graph.add_nodes_from(vertex_ids)

            for vertex_pair, enabled, edge_id in temp_full_edge_list:
                if enabled:
                    new_graph.add_edge(*vertex_pair, id=edge_ids)
                pass
            nx.draw(new_graph)
            
            try:
                nr_cycles = nx.find_cycle(new_graph)
                connected = nx.is_connected(new_graph)
            except:
                nr_cycles = 0
                connected = nx.is_connected(new_graph)
            
            if nr_cycles == 0 and connected == True:
                alt_list.append(disabled_edges[i])
            i += 1
        #7. print output
        print(alt_list)
    pass


        # put your implementation here
        pass


# Testing same graph as above, but the disabled are not drawn
vertex_ids = [0, 2, 4, 6, 10]
edge_ids = [1, 3, 5, 7, 8, 9]
edge_vertex_id_pairs = [(0, 2), (0, 4), (0, 6), (2, 4), (4, 6), (2, 10)]
edge_enabled = [True, True, True, False, False, True]
source_vertex_id = 10
# source_vertex_id = 9 #to raise 5. IDNotFoundError
# edge_ids = [1, 3, 5, 7, 8] #to raise 4 and 2. InputLengthDoesNotMatchError
# edge_vertex_id_pairs = [(0, 2), (0, 5), (0, 6), (2, 4), (4, 6), (2, 10)] #raise 3. IDNotFoundError
# vertex_ids = [0, 2, 4, 4, 6, 10] #to raise 1. IDNotUniqueError
# edge_ids = [1, 3, 3, 7, 8, 9] #to raise 1. IDNotUniqueError

grid = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

plt.figure(figsize=(8, 6))
pos = nx.spring_layout(grid.graph)  # Position nodes using the spring layout algorithm
nx.draw(grid.graph, pos, with_labels=True)
plt.title("Graph Visualization")
plt.show()
grid.graph.nodes.data()

downstream_vertices = grid.find_downstream_vertices(1)
print("Downstream vertices of edge 1:", downstream_vertices)

alternative_edges = grid.find_alternative_edges(1)
print("Alternative edges for disabling edge 1:", alternative_edges)

nodes = grid.graph.nodes(data=True)
print("Nodes:", nodes)

edges = grid.graph.edges(data=True)
print("Edges:", edges)


"""
Graph Processing Assignment

This script defines a GraphProcessor class for processing undirected graphs. 
It provides functionality to initialize a graph, find downstream vertices of an edge, 
and identify alternative edges for ensuring graph connectivity.

Authors: Rick Eversdijk, ...
Date: 30/04/2024

"""

import contextlib
import copy
from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


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
        try:
            nx.find_cycle(self.graph)
            raise GraphCycleError("The graph contains cycles.")
        except nx.NetworkXNoCycle:
            pass

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

        # 1. check errors & output list (i.e. the alternate edges that will be enabled)
        """if disabled_edge_id not in edge_ids:
            raise IDNotFoundError
        if disabled_edge_id not in edge_enabled and disabled_edge_id in edge_ids:
            raise EdgeAlreadyDisabledError"""

        alt_list = []

        # 2. create a list of currently disabled edge IDs
        disabled_edges = [edge_ids[i] for i in range(len(edge_ids)) if not edge_enabled[i]]

        # 3. create copy of list and update list
        disabled_edges_new = copy.copy(disabled_edges)
        disabled_edges_new.append(disabled_edge_id)

        # 4. create list of all edges with vertex pairs, enabling and ID (vertex_pair,(dis)/(en)abled,id)
        full_edge_list = list(zip(edge_vertex_id_pairs, edge_enabled, edge_ids))
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
        # 7. print output
        print(alt_list)

    pass

    # put your implementation here

"""
This is a skeleton for the graph processing assignment.

We define a graph processor class with some function skeletons.
"""
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import contextlib
from typing import List, Tuple


class IDNotFoundError(Exception):
    pass


class InputLengthDoesNotMatchError(Exception):
    pass


class IDNotUniqueError(Exception):
    pass


class GraphNotFullyConnectedError(Exception):
    pass


class GraphCycleError(Exception):
    pass


class EdgeAlreadyDisabledError(Exception):
    pass


class GraphProcessor:
    """
    General documentation of this class.
    You need to describe the purpose of this class and the functions in it.
    We are using an undirected graph in the processor.
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
        Check if the input is valid and raise exceptions if not.
        The following conditions should be checked:
            1. vertex_ids and edge_ids should be unique. (IDNotUniqueError)
            2. edge_vertex_id_pairs should have the same length as edge_ids. (InputLengthDoesNotMatchError)
            3. edge_vertex_id_pairs should contain valid vertex ids. (IDNotFoundError)
            4. edge_enabled should have the same length as edge_ids. (InputLengthDoesNotMatchError)
            5. source_vertex_id should be a valid vertex id. (IDNotFoundError)
            6. The graph should be fully connected. (GraphNotFullyConnectedError)
            7. The graph should not contain cycles. (GraphCycleError)
        If one certain condition is not satisfied, the error in the parentheses should be raised.

        Args:
            vertex_ids: list of vertex ids
            edge_ids: liest of edge ids
            edge_vertex_id_pairs: list of tuples of two integer
                Each tuple is a vertex id pair of the edge.
            edge_enabled: list of bools indicating of an edge is enabled or not
            source_vertex_id: vertex id of the source in the graph
        """
       
        self.graph = nx.Graph()

        # Add nodes/vertexes to the graph
        self.graph.add_nodes_from(vertex_ids)

        # Add edges to the graph
        for edge_pair, enabled, edge_ids in zip(edge_vertex_id_pairs, edge_enabled, edge_ids):
            if enabled:
                self.graph.add_edge(*edge_pair, id=edge_ids)
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
        print(full_edge)
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




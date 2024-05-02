"""
Graph Processing Assignment

This script defines a GraphProcessor class for processing undirected graphs. 
It provides functionality to initialize a graph, find downstream vertices of an edge, 
and identify alternative edges for ensuring graph connectivity.

Authors: Rick Eversdijk, Luka Nielsen
Date: 02/05/2024

"""

from typing import List, Tuple

import matplotlib.pyplot as plt
import networkx as nx


class IDNotFoundError(Exception):
    """Exception raised when source_vertex_id is not a valid vertex id"""


class InputLengthDoesNotMatchError(Exception):
    """Exception raised when the length of the edge_enabled does not match the input lists edge_ids."""


class IDNotUniqueError(Exception):
    pass


class GraphNotFullyConnectedError(Exception):
    """Exception raised when the graph is not fully connected meaning there are floating vertices."""


class GraphCycleError(Exception):
    """Exception raised when the graph contains cycles."""


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

        # 4. Check if lengths of input lists match
        if len(edge_enabled) != len(edge_ids):
            raise InputLengthDoesNotMatchError(
                "Length of vertex IDs does not match number of vertices."
            )

        # 5. Check if source vertex exists in the graph
        if source_vertex_id not in vertex_ids:
            raise IDNotFoundError("Source vertex ID not found.")

        # Initialize a NetworkX graph
        self.graph = nx.Graph()

        # Add nodes/vertexes to the graph
        self.graph.add_nodes_from(vertex_ids)

        # Add edges to the graph
        for edge_pair, enabled, edge_ids in zip(
            edge_vertex_id_pairs, edge_enabled, edge_ids
        ):
            if enabled:
                self.graph.add_edge(*edge_pair, id=edge_ids)

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
        # put your implementation here


# Testing same graph as above, but the disabled are not drawn
vertex_ids = [0, 2, 4, 6, 10]
edge_ids = [1, 3, 5, 7, 8, 9]
edge_vertex_id_pairs = [(0, 2), (0, 4), (0, 6), (2, 4), (4, 6), (2, 10)]
edge_enabled = [True, True, True, False, False, True]
source_vertex_id = 10
# source_vertex_id = 9 #to raise 5. IDNotFoundError
# edge_ids = [1, 3, 5, 7, 8] #to raise 4. InputLengthDoesNotMatchError

grid = GraphProcessor(
    vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id
)

plt.figure(figsize=(8, 6))
pos = nx.spring_layout(grid.graph)  # Position nodes using the spring layout algorithm
nx.draw(grid.graph, pos, with_labels=True)
plt.title("Graph Visualization")
plt.show()
grid.graph.nodes.data()

# downstream_vertices = grid.find_downstream_vertices(1)
# print("Downstream vertices of edge 1:", downstream_vertices)

# alternative_edges = grid.find_alternative_edges(1)
# print("Alternative edges for disabling edge 1:", alternative_edges)

nodes = grid.graph.nodes(data=True)
print("Nodes:", nodes)

edges = grid.graph.edges(data=True)
print("Edges:", edges)

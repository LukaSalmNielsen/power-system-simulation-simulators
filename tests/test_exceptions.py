import pytest

from power_system_simulation.graph_processing import (
    GraphProcessor,
    IDNotFoundError,
    IDNotUniqueError,
    InputLengthDoesNotMatchError
)

vertex_ids = [0, 2, 4, 6, 10]
edge_ids = [1, 3, 5, 7, 8, 9]
edge_vertex_id_pairs = [(0, 2), (0, 4), (0, 6), (2, 4), (4, 6), (2, 10)]
edge_enabled = [True, True, True, False, False, True]
source_vertex_id = 10


def test_IDNotFoundError():
    with pytest.raises(IDNotFoundError):
        source_vertex_id = 9
        grid = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)


def test_InputLengthDoesNotMatchError():
    with pytest.raises(InputLengthDoesNotMatchError):
        edge_ids = [1, 3, 5, 7, 8]
        grid = GraphProcessor(vertex_ids, edge_ids, edge_vertex_id_pairs, edge_enabled, source_vertex_id)

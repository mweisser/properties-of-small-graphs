import networkx as nx
import numpy as np
import math
from functools import total_ordering
import hashlib


@total_ordering
class Graph(object):
    def __init__(self, signature=None, adj=None, row=None):
        if signature is not None and adj is not None:
            raise ValueError("Either signature or array must be provided, not both")

        if signature is not None:
            self.signature = signature
            self.adj = matrix_from_signature(signature)
        elif adj is not None:
            self.signature = signature_from_matrix(adj)
            self.adj = adj
        else:
            raise ValueError("Either signature or array must be provided")

        self.g = nx.from_numpy_array(self.adj)
        if not nx.is_connected(self.g):
            raise GraphIsNotConnectedError()

        if row is None:
            self.order = len(self.adj)
            self.size = self.g.number_of_edges()
            self.max_degree = max(d for _, d in self.g.degree())
            degrees = sorted([d for u, d in self.g.degree()])
            self.degrees = ",".join([str(d) for d in degrees])
            self.is_tree = nx.is_tree(self.g)
            self.is_bipartite = nx.is_bipartite(self.g)
            self.has_bridge = nx.has_bridges(self.g)
            try:
                c = nx.is_chordal(self.g)
            except nx.exception.NetworkXError:
                c = False
            self.is_chordal = c
            self.is_complete = self.size == self.order * (self.order - 1) / 2
            cycle_basis = nx.minimum_cycle_basis(self.g)
            self.min_cycle_basis_weight = sum(len(cycle) for cycle in cycle_basis)
            self.min_cycle_basis_size = len(cycle_basis)
            self.diameter = nx.diameter(self.g)
            self.radius = nx.radius(self.g)
            self.is_eulerian = nx.is_eulerian(self.g)
            self.is_planar = nx.is_planar(self.g)
            self.number_of_faces = 2 - self.order + self.size
            self.is_regular = nx.is_regular(self.g)
            self.p3 = self.number_of_p3()
            self.p4 = self.number_of_p4()
            self.property_hash = self.compute_property_hash()
        else:
            self.order = row["graph_order"]
            self.size = row["graph_size"]
            self.max_degree = row["max_degree"]
            self.degrees = row["degrees"]
            self.is_tree = row["is_tree"]
            self.is_bipartite = row["is_bipartite"]
            self.has_bridge = row["has_bridge"]
            self.is_chordal = row["is_chordal"]
            self.is_complete = row["is_complete"]
            self.min_cycle_basis_weight = row["min_cycle_basis_weight"]
            self.min_cycle_basis_size = row["min_cycle_basis_size"]
            self.diameter = row["diameter"]
            self.radius = row["radius"]
            self.is_eulerian = row["is_eulerian"]
            self.is_planar = row["is_planar"]
            self.number_of_faces = row["number_of_faces"]
            self.is_regular = row["is_regular"]
            self.p3 = row["p3"]
            self.p4 = row["p4"]
            self.property_hash = row["property_hash"]

    def compute_property_hash(self):
        m = hashlib.sha256()
        m.update(",".join([
            str(self.order),
            str(self.size),
            str(self.max_degree),
            self.degrees,
            str(self.is_tree),
            str(self.is_bipartite),
            str(self.has_bridge),
            str(self.is_chordal),
            str(self.is_complete),
            str(self.min_cycle_basis_weight),
            str(self.min_cycle_basis_size),
            str(self.diameter),
            str(self.radius),
            str(self.is_eulerian),
            str(self.is_planar),
            str(self.number_of_faces),
            str(self.is_regular),
            str(self.p3),
            str(self.p4)
        ]).encode())
        return m.hexdigest()

    def is_connected(self):
        return nx.is_connected(self.g)

    def number_of_p4(self):
        count = 0
        covering = set()
        visited = set()
        for a, b in self.g.edges:
            for u, v in self.g.edges:
                e = self.adj[a, u] + self.adj[a, v] + self.adj[b, u] + self.adj[b, v]
                if tuple(sorted((a, b, u, v))) in visited:
                    continue
                elif e == 1:
                    count += 1
                    covering.add(tuple(sorted((a, b))))
                    covering.add(tuple(sorted((u, v))))
                    visited.add(tuple(sorted((a, b, u, v))))
                    if self.adj[a, u] == 1:
                        covering.add(tuple(sorted((a, u))))
                    elif self.adj[a, v] == 1:
                        covering.add(tuple(sorted((a, v))))
                    elif self.adj[b, u] == 1:
                        covering.add(tuple(sorted((b, u))))
                    elif self.adj[b, v] == 1:
                        covering.add(tuple(sorted((b, v))))

        if len(covering) == self.size:
            return count
        else:
            return None

    def number_of_p3(self):
        # On cherche le nombre de chaine de longueur 3 mais dont les sommets ne forment pas
        # un triangle induit.
        # Cette valeur vaut None si toutes les arêtes ne sont pas couvertes.
        count = 0
        covering = set()
        visited = set()
        for a, b in self.g.edges:
            for c in self.g.nodes - {a, b}:
                if self.adj[a, b] and self.adj[b, c] and self.adj[a, c]:
                    continue
                if self.adj[a, c]:
                    if tuple(sorted((a, b, c))) in visited:
                        continue
                    else:
                        count += 1
                        covering.add(tuple(sorted((a, b))))
                        covering.add(tuple(sorted((a, c))))
                        visited.add(tuple(sorted((a, b, c))))
                if self.adj[b, c]:
                    if tuple(sorted((a, b, c))) in visited:
                        continue
                    else:
                        count += 1
                        covering.add(tuple(sorted((a, b))))
                        covering.add(tuple(sorted((b, c))))
                        visited.add(tuple(sorted((a, b, c))))

        if len(covering) == self.size:
            return count
        else:
            return None

    def __eq__(self, other):
        b = ((
                 self.order,
                 self.size,
                 self.max_degree,
                 self.is_tree,
                 self.is_bipartite,
                 self.has_bridge,
                 self.is_chordal,
                 self.is_complete,
                 self.min_cycle_basis_weight,
                 self.min_cycle_basis_size,
                 self.diameter,
                 self.radius,
                 self.is_eulerian,
                 self.is_planar,
                 self.number_of_faces,
                 self.is_regular,
                 self.p3
             ) == (
                 other.order,
                 other.size,
                 other.max_degree,
                 other.is_tree,
                 other.is_bipartite,
                 other.has_bridge,
                 other.is_chordal,
                 other.is_complete,
                 other.min_cycle_basis_weight,
                 other.min_cycle_basis_size,
                 other.diameter,
                 other.radius,
                 other.is_eulerian,
                 other.is_planar,
                 other.number_of_faces,
                 other.is_regular,
                 other.p3
             )
             )
        if not b:
            return False
        else:
            return nx.is_isomorphic(self.g, other.g)

    def __lt__(self, other):
        return ((
                    self.order,
                    self.size,
                    self.max_degree,
                    self.is_tree,
                    self.is_bipartite,
                    self.has_bridge,
                    self.is_chordal,
                    self.is_complete,
                    self.min_cycle_basis_weight,
                    self.min_cycle_basis_size,
                    self.diameter,
                    self.radius,
                    self.is_eulerian,
                    self.is_planar,
                    self.number_of_faces,
                    self.is_regular,
                    self.p3
                ) < (
                    other.order,
                    other.size,
                    other.max_degree,
                    other.is_tree,
                    other.is_bipartite,
                    other.has_bridge,
                    other.is_chordal,
                    other.is_complete,
                    other.min_cycle_basis_weight,
                    other.min_cycle_basis_size,
                    other.diameter,
                    other.radius,
                    other.is_eulerian,
                    other.is_planar,
                    other.number_of_faces,
                    other.is_regular,
                    other.p3
                )
                )

    def isomorph_with(self, other):
        return self.property_hash == other.property_hash and nx.is_isomorphic(self.g, other.g)


class GraphIsNotConnectedError(Exception):
    pass


def signature_from_matrix(matrix):
    return "".join(["".join(str(int(i)) for i in l[j + 1:]) for j, l in enumerate(matrix[:-1])])


def matrix_from_signature(s):
    r = get_root_of_triangular_number(len(s)) + 1
    matrix = np.zeros((r, r), dtype=int)
    c = 0
    for i in range(r - 1):
        for j in range(i + 1, r):
            matrix[i, j] = int(s[c])
            matrix[j, i] = int(s[c])
            c += 1
    return matrix


def get_root_of_triangular_number(n):
    t = int(math.sqrt(2 * n))
    if t * (t + 1) == 2 * n:
        return t
    else:
        raise ValueError(f"{n} is not a triangular number")



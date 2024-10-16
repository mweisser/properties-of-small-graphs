"""
Dans la base de données, on stocke les graphs et leur propriétés.
La clef d'un graphe est sa signature, les valeurs supérieures de la matrice d'adjacence. Idéalement, on ne stocke
qu'un représentant pour chaque graphe isomorphe, le master. Si on ajoute un graphe isomorphe, on le lie au master par la
colonne isomorph.
"""

import sqlite3
from graph import Graph, GraphIsNotConnectedError


def open_db():
    con = sqlite3.connect("graphs.db")
    con.row_factory = sqlite3.Row
    create_table(con)
    return con


def close_db(con):
    con.close()


def iterate_over_graphs_of_order(con, n):
    cur = con.cursor()
    graphs = cur.execute("SELECT * FROM graphs WHERE graph_order = ?", (n,))
    rows = cur.fetchall()
    for row in rows:
        yield Graph(signature=row["signature"], adj=None, row=row)


def get_isomorph(con, g):
    """
    Return the master graph isomorph with g. The master graph is representative of isomorphic graphs.
    In the database, the master graph is the one with the isomoprh column associated to itself.
    """
    cur = con.cursor()
    graphs = cur.execute("SELECT * FROM graphs WHERE property_hash = ? and isomorph = signature", (g.property_hash,))
    if g is None:
        return None
    else:
        rows = cur.fetchall()
        if len(rows) == 0:
            return None
        else:
            for row in rows:
                o = Graph(signature=row["signature"], adj=None, row=row)
                if g.isomorph_with(o):
                    return o.signature

            return None


def insert_graph(con, g, isomorph=None):
    if g.is_connected() is False:
        raise GraphIsNotConnectedError("Graph is not connected")

    cur = con.cursor()
    SQL = """INSERT OR REPLACE INTO graphs (signature, property_hash, graph_order, graph_size, isomorph, max_degree, degrees, is_tree, is_bipartite, has_bridge, is_chordal, is_complete, min_cycle_basis_weight, min_cycle_basis_size, diameter, radius, is_eulerian, is_planar, number_of_faces, is_regular, p3, p4)
                VALUES (:signature, :property_hash, :graph_order,:graph_size, :isomorph, :max_degree, :degrees, :is_tree, :is_bipartite, :has_bridge, :is_chordal, :is_complete, :min_cycle_basis_weight, :min_cycle_basis_size, :diameter, :radius, :is_eulerian, :is_planar, :number_of_faces, :is_regular, :p3, :p4)"""
    dict = {
        'signature': "".join(str(i) for i in g.signature),
        'property_hash': g.property_hash,
        'graph_order': g.order,
        'graph_size': g.size,
        'isomorph': isomorph,
        "max_degree": g.max_degree,
        "degrees": g.degrees,
        "is_tree": g.is_tree,
        "is_bipartite": g.is_bipartite,
        "has_bridge": g.has_bridge,
        "is_chordal": g.is_chordal,
        "is_complete": g.is_complete,
        "min_cycle_basis_weight": g.min_cycle_basis_weight,
        "min_cycle_basis_size": g.min_cycle_basis_size,
        "diameter": g.diameter,
        "radius": g.radius,
        "is_eulerian": g.is_eulerian,
        "is_planar": g.is_planar,
        "number_of_faces": g.number_of_faces,
        "is_regular": g.is_regular,
        "p3": g.p3,
        "p4": g.p4
    }
    con.execute(SQL, dict)
    con.commit()


def get_graph(con, signature):
    cur = con.cursor()

    g = cur.execute("SELECT * FROM graphs WHERE signature = ?", (signature,))
    if g is None:
        return None
    else:
        return cur.fetchone()


def create_table(con):
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS graphs (
                         signature TEXT NOT NULL PRIMARY KEY,
                         property_hash TEXT NOT NULL,
                         graph_order INTEGER,
                         graph_size INTEGER,
                         isomorph TEXT,
                         max_degree INTEGER,
                         degrees TEXT,
                         is_tree BOOLEAN,
                         is_bipartite BOOLEAN,
                         has_bridge BOOLEAN,
                         is_chordal BOOLEAN,
                         is_complete BOOLEAN,   
                         min_cycle_basis_weight INTEGER,
                         min_cycle_basis_size INTEGER,
                         diameter INTEGER,
                         radius INTEGER,
                         is_eulerian BOOLEAN,
                         is_planar BOOLEAN,
                         number_of_faces INTEGER,
                         is_regular BOOLEAN,
                         p3 INTEGER,
                         p4 INTEGER,
                         FOREIGN KEY(isomorph) REFERENCES graphs(signature)                                                                   
    )
    """)

    con.commit()


if __name__ == "__main__":
    con = open_db()
    create_table(con)
    g = Graph(signature="011100", adj=None)
    print(g.signature)
    insert_graph(con, g)
    close_db(con)

from graph import Graph, GraphIsNotConnectedError
from database import insert_graph, get_isomorph, iterate_over_graphs_of_order, open_db, close_db
from itertools import product
from tqdm import tqdm
import networkx as nx
from graph import matrix_from_signature, signature_from_matrix

nb_of_graphs = [1, 1, 1, 2, 6, 21, 112, 853, 11117, 261080, 11716571, 1006700565, 164059830476, 50335907869219, 29003487462848061, 31397381142761241960, 63969560113225176176277, 245871831682084026519528568, 1787331725248899088890200576580]


def enumerate_all_signature():
    con = open_db()
    for size in tqdm(range(6, 7)):
        repeat = sum(range(1, size + 1))

        for signature in tqdm(product("01", repeat=repeat)):
            try:
                g = Graph(signature="".join(signature))
                signature = get_isomorph(con, g)
                if signature is None:
                    signature = g.signature
                    insert_graph(con, g, isomorph=signature)
            except GraphIsNotConnectedError:
                continue

    close_db(con)


def extend_db_with_one_node(n):
    con = open_db()

    if n <= 1:
        s = "1"
        ngraph = Graph(signature=s)
        insert_graph(con, ngraph, isomorph=s)
    else:
        for current in tqdm(iterate_over_graphs_of_order(con, n), total=nb_of_graphs[n]):
            s = signature_from_matrix(nx.adjacency_matrix(current.g).todense())
            for l in product("01", repeat=n):
                try:
                    if sum([int(i) for i in l]) == 0:
                        continue
                    ns = "".join(l) + s
                    ngraph = Graph(signature=ns)
                    signature = get_isomorph(con, ngraph)
                    if signature is None:
                        signature = ngraph.signature
                        insert_graph(con, ngraph, isomorph=signature)
                except GraphIsNotConnectedError:
                    print("Not connected")

    close_db(con)


if __name__ == "__main__":
    # enumerate_all_signature()
    extend_db_with_one_node(8)

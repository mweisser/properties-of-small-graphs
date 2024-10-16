from database import open_db, close_db, iterate_over_graphs_of_order, insert_graph
from tqdm import tqdm


if __name__ == "__main__":
    con = open_db()
    for i in range(2, 10):
        print(f"Order : {i}")
        graphs = []
        for g in tqdm(iterate_over_graphs_of_order(con, i)):
            g.p4 = g.number_of_p4()
            g.property_hash = g.compute_property_hash()
            graphs.append(g)
        for g in graphs:
            insert_graph(con, g)

    close_db(con)

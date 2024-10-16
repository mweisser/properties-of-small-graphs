from graph import Graph, GraphIsNotConnectedError
from database import insert_graph, get_graph, open_db, close_db
from show import write_graphs, write_document
import networkx.algorithms.isomorphism as iso
from tqdm import tqdm

pdf_header = """
#!/bin/bash

cd results_P4
for f in *.tex; do
  pdflatex $f
done

rm *.aux
rm *.log

cd ..
"""

pdf_join = "/System/Library/Automator/Combine\ PDF\ Pages.action/Contents/MacOS/join -o"

def filter_ismorphs(graphs):
    graphs = sorted(graphs)
    filtered = {}

    for i in range(len(graphs)):
        filtered[graphs[i].signature] = False

    for i in range(len(graphs)):
        if filtered[graphs[i].signature]:
            continue
        for j in range(i+1, len(graphs)):
            if filtered[graphs[j].signature]:
                continue
            if graphs[i] != graphs[j]:
                continue

            if iso.is_isomorphic(graphs[i].g, graphs[j].g):
                filtered[graphs[j].signature] = True

    graphs = [g for g in graphs if not filtered[g.signature]]
    return graphs


if __name__ == "__main__":
    con = open_db()
    limit=50
    names = []
    numbers = {}
    for p4 in tqdm(range(1, limit)):
        # for a given value of 'p4', select in database signature of graphs with smallest 'order'
        cur = con.cursor()
        g = cur.execute("SELECT * FROM graphs WHERE p4 = ? ORDER BY graph_order", (p4,))
        rows = g.fetchall()
        if rows is None:
            print(f"No graphs found with p4 = {p4}")
        else:
            try:
                g1 = Graph(signature=rows[0]["signature"], adj=None, row=rows[0])
                graphs = [Graph(signature=r["signature"], adj=None, row=r) for r in rows if r["graph_order"] == g1.order]
                graphs = filter_ismorphs(graphs)
                numbers[p4] = f"{len(graphs)} graphs of order {g1.order}"
                write_graphs(graphs, f"p4_{p4}", title=f"p4 = {p4} ({len(graphs)} graphs)", folder="results_P4")
                names.append(f"p4_{p4}")
            except IndexError:
                print(f"No graphs with p4={p4}")
    for p4 in tqdm(range(1, limit)):
        print(p4, numbers[p4])
    write_document(names, file="results_P4.tex", folder="results_P4")
    close_db(con)

    #with open("pdf.sh", "w") as f:
    #    f.write(pdf_header)
    #    pdfs = [f"results_P3/p3_{p3}.pdf" for p3 in range(1, limit)]
    #    f.write(f"{pdf_join} results_P3.pdf {' '.join(pdfs)}")



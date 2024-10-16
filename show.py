from graph import Graph, GraphIsNotConnectedError
from database import insert_graph, get_graph, open_db, close_db
import networkx as nx

latex_header = """
\\documentclass{report}
\\usepackage{tikz}
\\usepackage{subcaption}
\\footnotesize

\\title{Min order graphs for a given p3}
\\date{\\today}

\\begin{document}
\\maketitle
\\tableofcontents
\\newpage
"""

latex_footer = """
\\end{document}
"""


def graph_to_latex(graph):
    # display graph g using matplotlib
    tex = nx.to_latex(graph.g, as_document=False)
    tex += "\n\\begin{itemize}\n"
    for key in graph.__dict__.keys():
        if not key == "adj":
            tex += f"\\item {key.replace('_', ' ')}: {graph.__dict__[key]}\n"
    tex += "\\end{itemize}\n"
    tex += "\\newpage\n"

    return tex


def signature_to_latex(signature, con=None):
    if con is None:
        con = open_db()

    row = get_graph(con, signature)
    if row is None:
        graph = Graph(signature=signature, adj=None)
        insert_graph(con, graph)
    else:
        graph = Graph(signature=row["signature"], adj=None, row=row)

    # display graph g using matplotlib
    tex = nx.to_latex(graph.g, as_document=False)
    with open(f"graph_{signature}.tex", "w") as f:
        tex += "\n\\begin{itemize}\n"
        for key in row.keys():
            tex += f"\\item {key.replace('_', ' ')}: {row[key]}\n"
        tex += "\\end{itemize}\n"

    if con is None:
        close_db(con)
    return tex


def write_graphs(graphs, name, folder="results_P3", title=None):
    with open(folder+"/"+f"{name}.tex", "w") as f:

        if title:
            f.write("\\chapter{" + title + "}\n")
            f.write("\\newpage")
        for g in graphs:
            tex = graph_to_latex(g)
            f.write(tex)



def write_document(names, file="results_P3.tex", folder="results_P3"):
    with open(folder+"/"+file, "w") as f:
        f.write(latex_header)
        for name in names:
            f.write("\input{"+name+"}\n")
        f.write(latex_footer)


if __name__ == "__main__":
    con = open_db()
    signatures = ["011", "110011", "1110001011", "011101110001011", "011110111100001001011", "0011110011110111100001001011"]
    with open(f"graph_with_largest_p3.tex", "w") as f:
        f.write(latex_header)
        for s in signatures:
            tex = signature_to_latex(s, con)
            f.write(tex)
        f.write(latex_footer)




    close_db(con)

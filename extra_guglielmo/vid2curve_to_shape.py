import networkx as nx
import argparse
import visualize
import graph_utils as graph
import time

parser = argparse.ArgumentParser(
    description='Converts Vid2curve output to an OBJ mesh')

parser.add_argument('input_file')
parser.add_argument('-o', '--out_file', dest='out_file',
                    help='store output in OUT_FILE. Default is "out"', default='out')
parser.add_argument("-p", "--plot", dest='plot', type=str, choices=["reduction", "merging", "all"],
                    help="Visualize algorithms")
args = parser.parse_args()
if args.plot:
    visualize.init_window()
g = graph.graph_from_obj(args.input_file)
graph.simplify_edges(g,
                     visualize=args.plot == 'reduction' or args.plot == 'all')
graph.merge_close_vecs(g,
                       visualize=args.plot == 'merging' or args.plot == 'all')
graph.graph_to_obj(g, (args.out_file)+'.obj')

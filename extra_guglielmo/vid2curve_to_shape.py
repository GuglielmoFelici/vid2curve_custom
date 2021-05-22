import argparse
import visualize
import v2c_graph as graph
from mesh import Mesh


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Converts Vid2curve output to an OBJ mesh')
    parser.add_argument('input_file')
    parser.add_argument('-s', '--sensitivity', dest='sens', type=int,
                        help='Sensitivity of the merging algorithm. Lower values mean farther nodes will be merged. Values in [1,10]. Default is 8.', default=8)
    parser.add_argument('-o', '--out_file', dest='out_file',
                        help='store output in OUT_FILE. Default is "out"', default='out')

    parser.add_argument("-p", "--plot", dest='plot', type=str, choices=["reduction", "merging", "triangles", "all"],
                        help="Visualize algorithms")
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.plot:
        visualize.init_window()
    g = graph.V2CGraph.from_obj(args.input_file)
    g.simplify_edges(visualize=args.plot == 'reduction' or args.plot == 'all')
    g.merge_close_vecs(min(max(args.sens, 0), 10),
                       visualize=args.plot == 'merging' or args.plot == 'all')
    g = g.relabel_nodes()
    g.to_obj(args.out_file + '_graph.obj')
    mesh = Mesh.from_graph(g,
                           visualize=args.plot == 'triangles' or args.plot == 'all')
    mesh.to_obj(args.out_file + '_triangles.obj')


if __name__ == "__main__":
    main()

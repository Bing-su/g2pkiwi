import argparse
from .g2pk import G2p

g2p = G2p()


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="input string", type=str, nargs="+")
    parser.add_argument("-v", "--verbose", help="verbose", action="store_true")
    parser.add_argument("-d", "--descriptive", help="descriptive", action="store_true")
    args = parser.parse_args()
    string = " ".join(args.text)
    print(g2p(string, descriptive=args.descriptive, verbose=args.verbose))


if __name__ == "__main__":
    cli()

import argparse
from vcg import Auction, pprint_auction

parser = argparse.ArgumentParser()
parser.add_argument('file', type=argparse.FileType('r'))

def main(args: argparse.Namespace):
    auction = Auction.from_csv(args.file)
    pprint_auction(auction)

    print('\n...solving...\n')
    soln = auction.solve()
    pprint_auction(auction, soln)


if __name__ == '__main__':
    main(parser.parse_args())

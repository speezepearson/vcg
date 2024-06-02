import dataclasses
from typing import List, Mapping, Optional

Price = int
PlayerId = str
ItemId = str

@dataclasses.dataclass(frozen=True)
class Bid:
    price: Price
    item_counts: Mapping[ItemId, int]

@dataclasses.dataclass(frozen=True)
class Soln:
    revenue: Price
    winning_bids: Mapping[PlayerId, Bid]

@dataclasses.dataclass(frozen=True)
class Auction:
    item_counts: Mapping[ItemId, int]
    bids: Mapping[PlayerId, List[Bid]]

    def solve(self) -> Soln:
        if not self.bids:
            return Soln(revenue=0, winning_bids={})
        
        (first_player_id, first_player_bids), *rest_bids = self.bids.items()
        best_soln = Auction(
            item_counts=self.item_counts,
            bids=dict(rest_bids)
        ).solve()

        for bid in first_player_bids:
            if all(
                self.item_counts[item_id] >= count
                for item_id, count in bid.item_counts.items()
            ):
                subsoln = Auction(
                    item_counts={
                        item_id: count - bid.item_counts.get(item_id, 0)
                        for item_id, count in self.item_counts.items()
                    },
                    bids=dict(rest_bids)
                ).solve()
                if subsoln.revenue + bid.price > best_soln.revenue:
                    best_soln = Soln(
                        revenue=subsoln.revenue + bid.price,
                        winning_bids={first_player_id: bid, **subsoln.winning_bids}
                    )

        return best_soln
    
def make_fake_auction(seed=None):
    import random
    if seed is not None:
        random.seed(seed)
    n_item_kinds = int(random.binomialvariate(n=30, p=0.3))
    item_counts = {f'i{i}': random.randint(1, 10) for i in range(n_item_kinds)}
    n_players = int(random.binomialvariate(n=40, p=0.5))
    bids = {
        f'p{i}': [
            Bid(
                price=random.randint(1, 100),
                item_counts={
                    item_id: random.randint(1, item_counts[item_id]+1)
                    for item_id in item_counts
                    if random.random() < 1/3
                }
            )
            for _ in range(random.randint(1, 5))
        ]
        for i in range(n_players)
    }
    # breakpoint()
    return Auction(item_counts=item_counts, bids=bids)

def pprint_auction(auction: Auction, soln: Optional[Soln]):
    pnamew = max(len(player_id) for player_id in auction.bids.keys())
    countw = max(len(str(count)) for count in auction.item_counts.values())
    pricew = max(len(str(bid.price)) for bids in auction.bids.values() for bid in bids)
    item_ids = sorted(auction.item_counts.keys())
    print('pricew:', pricew)
    for player_id, bids in auction.bids.items():
        for bid in bids:
            if soln is not None:
                print('X' if bid == soln.winning_bids.get(player_id) else ' ', end=' ')
            print(f'{player_id: <{pnamew}s} {bid.price: {pricew}d}: ', end='')
            for item_id in item_ids:
                print(f'{bid.item_counts.get(item_id, 0): {countw}d}', end=' ')
            print()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int)

def main(args: argparse.Namespace):
    seed: Optional[int] = args.seed
    print(Auction(
        item_counts={'apple': 2},
        bids={
            'Spencer': [
                Bid(price=10, item_counts={'apple': 1}),
                Bid(price=20, item_counts={'apple': 2}),
            ],
            'Yam': [
                Bid(price=15, item_counts={'apple': 1}),
            ],
        }
    ).solve())
    
    fake = make_fake_auction(seed=seed)
    print()
    pprint_auction(fake, None)
    print()
    pprint_auction(fake, fake.solve())


if __name__ == '__main__':
    main(parser.parse_args())

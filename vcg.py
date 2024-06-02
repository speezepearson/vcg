import csv
from collections import Counter, defaultdict
import dataclasses
from typing import List, Mapping, MutableMapping, Optional

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

        assert best_soln.revenue >= 0
        
        item_sold_counts: MutableMapping[ItemId, int] = Counter()
        for bid in best_soln.winning_bids.values():
            for item, count in bid.item_counts.items():
                item_sold_counts[item] += count
        assert all(
            item_sold_counts[item] <= count
            for item, count in self.item_counts.items()
        )
        return best_soln
    
    @classmethod
    def from_csv(cls, file):
        rows = list(csv.DictReader(file))

        assert rows[0]['Bidder'] == '__QUANTITY__' and rows[0]['Price'] == ''
        quantity_row, *rows = rows
        item_quantities = {k: int(v) for k, v in quantity_row.items() if k not in {'Bidder', 'Price'}}

        bids = defaultdict(list)
        for row in rows:
            bids[row['Bidder']].append(Bid(
                price=int(row['Price']),
                item_counts={item: int(row[item]) for item in item_quantities}
            ))

        return cls(item_counts=item_quantities, bids=dict(bids))
    
def pprint_auction(auction: Auction, soln: Optional[Soln] = None):
    pnamew = max(len(player_id) for player_id in auction.bids.keys())
    countw = max(len(str(count)) for count in auction.item_counts.values())
    pricew = max(len(str(bid.price)) for bids in auction.bids.values() for bid in bids)
    item_ids = sorted(auction.item_counts.keys())
    for player_id, bids in auction.bids.items():
        for bid in bids:
            if soln is not None:
                print('X' if bid == soln.winning_bids.get(player_id) else ' ', end=' ')
            print(f'{player_id: <{pnamew}s} {bid.price: {pricew}d}: ', end='')
            for item_id in item_ids:
                print(f'{bid.item_counts.get(item_id, 0): {countw}d}', end=' ')
            print()

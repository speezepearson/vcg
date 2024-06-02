import pytest

from vcg import Auction, Bid, Soln, pprint_auction

def make_fake_auction(seed=None, size: int = 10):
    import random
    if seed is not None:
        random.seed(seed)
    n_item_kinds = 1+int(random.binomialvariate(n=3*size, p=0.3))
    item_counts = {f'i{i}': random.randint(1, 10) for i in range(n_item_kinds)}
    n_players = int(random.binomialvariate(n=4*size, p=0.5))
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
    return Auction(item_counts=item_counts, bids=bids)


def test_simple_auction():
    auction = Auction(
        item_counts={'apple': 2},
        bids={
            'Alice': [
                Bid(price=10, item_counts={'apple': 1}),
                Bid(price=20, item_counts={'apple': 2}),
            ],
            'Bob': [
                Bid(price=15, item_counts={'apple': 1}),
            ],
            'Charlie': [
                Bid(price=8, item_counts={'apple': 1}),
            ],
        }
    )

    assert auction.solve() == Soln(
        revenue=25,
        winning_bids={
            'Alice': Bid(price=10, item_counts={'apple': 1}),
            'Bob': Bid(price=15, item_counts={'apple': 1}),
        },
    )

@pytest.mark.parametrize('seed', range(3))
@pytest.mark.parametrize('size', [1, 3, 5])
def test_benchmark(benchmark, seed:int, size: int):
    auction = make_fake_auction(seed=seed, size=size)
    pprint_auction(auction)
    benchmark(auction.solve)

def test_auction_from_csv():

    with open('example.csv') as f:
        auction = Auction.from_csv(f)

    assert auction.item_counts == {'Apple': 2, 'Orange': 1}
    assert auction.bids['Spencer'] == [
        Bid(price=10, item_counts={'Apple': 1, 'Orange': 0}),
        Bid(price=20, item_counts={'Apple': 2, 'Orange': 0}),
        Bid(price=30, item_counts={'Apple': 3, 'Orange': 0}),
        Bid(price=5, item_counts={'Apple': 0, 'Orange': 1}),
        Bid(price=15, item_counts={'Apple': 1, 'Orange': 1}),
        Bid(price=25, item_counts={'Apple': 2, 'Orange': 1}),
    ]
    assert auction.bids['Yam'] == [
        Bid(price=15, item_counts={'Apple': 1, 'Orange': 0}),
        Bid(price=8, item_counts={'Apple': 0, 'Orange': 1}),
        Bid(price=23, item_counts={'Apple': 1, 'Orange': 1}),
    ]

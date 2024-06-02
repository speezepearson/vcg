Usage:

```bash
python3 . example.csv
```

To develop:

```bash
pip install -r requirements.txt
pytest
# or, to not-run the slow benchmarks,
pytest -k "not benchmark"
```

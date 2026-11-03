### rustc-hash

1. **Use `FxHashMap` and `FxHashSet` for lookup-only maps on keys an attacker doesn't choose.** They hash much faster than std's SipHash but don't resist hash flooding, so keep std's `HashMap` for keys from requests or uploaded files. Neither map's iteration order may reach output.

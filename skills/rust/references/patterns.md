# Advanced patterns

Read when the code has or needs typestate, a marker parameter, a branded id family, a sealed or extension trait, an associated type, or a `#[must_use]` plan or guard, or when a profile points at allocation, hashing or dispatch.

Each pattern names when it pays and when to skip it. The bar from SKILL.md holds: a pattern goes in only where it removes code, a runtime check or a measured cost, or turns a likely mistake into a compile error. A pattern that needs a new crate also passes the library test in [libraries.md](libraries.md).

| Pattern | Use it when | Skip it when |
|---|---|---|
| Typestate, one type per state | a multi-step process must not run out of order, and the states hold different data | one runtime check in one place covers it |
| Typestate with a marker parameter | the states share most fields and methods, and a wrong order must not compile | the states hold different data: one type per state |
| Branded id family (`Id<K>`) | several id kinds share one representation and every method, and travel together in one struct or signature | the kinds differ in validation or behaviour: separate newtypes |
| Sealed trait | other crates use a trait but must not implement it | the trait is a seam other crates exist to implement |
| Extension trait (`<Type>Ext`) | a foreign type needs the same domain methods in two or more crates | one crate needs them (a free function), or the value lives in your own structs (a newtype) |
| Associated type | each implementation picks exactly one type | one type implements the trait for several types: a generic parameter |
| `#[must_use]` plan or guard | dropping the value unused loses work or ends a guarded state early | reading the result is optional |
| `Cow<'a, str>` | most inputs pass through unchanged, on a measured path | no profile shows the allocation: return `String` |
| `SmallVec` | lists are usually short, and their allocation shows in a profile | no profile: `Vec` |
| Zero-copy deserialisation | large inputs parse on a hot path | the parsed value outlives the input buffer |
| Lending iterator (GATs) | an iterator yields borrows of its own buffer, and generic code consumes several such types | one type: an inherent `next_*` method |
| Channels between stages | producers and consumers run at different rates | the stages run at one rate: call the next stage directly |
| Arena allocation | many small nodes live and die together | nodes have separate lifetimes |
| Typed index vectors | a `Vec` is indexed by a domain id | the `Vec` is only iterated |
| String interning | the same keys are hashed and compared many times | keys are compared once or twice |
| Bit sets | sets of small dense ids are unioned or intersected in a loop | ids are sparse or the sets are small and rare |
| Worklist to a fixpoint | results depend on each other through cycles | the dependencies are acyclic: process in topological order |
| Incremental queries (salsa) | an edit must re-derive only what depends on it | each run computes everything once |
| Enum dispatch | a closed set needs one interface, and `dyn` shows in a profile | the set is open at run time |

## Typestate, one type per state

Each state is its own type, and each transition takes `self` and returns the next state, so a call in the wrong order doesn't compile.

```rust
#[must_use = "a plan does nothing until `apply` runs it"]
struct MigrationPlan { steps: Box<[Step]> }

impl MigrationPlan {
    fn describe(&self) -> impl Iterator<Item = &Step> { self.steps.iter() }
    fn apply(self, db: &mut Db) -> Result<SchemaVersion, ApplyError> { /* … */ }
}

// Before: fn migrate(db: &mut Db, target: SchemaVersion, dry_run: bool)
// After: a dry run prints plan.describe(); a real run calls plan.apply(&mut db)
let plan = migrator.plan(target)?;
```

## Typestate with a marker parameter

When the states share most fields and methods, write one type with a zero-sized marker parameter and put each state's methods on its own `impl` block.

```rust
enum Draft {}
enum Issued {}

struct Invoice<State> { lines: Vec<Line>, customer: CustomerId, state: PhantomData<State> }

impl<State> Invoice<State> {
    fn total(&self) -> Money { /* … */ }
}
impl Invoice<Draft> {
    fn add_line(&mut self, line: Line) { self.lines.push(line); }
    fn issue(self) -> Invoice<Issued> {
        let Invoice { lines, customer, state: _ } = self;
        Invoice { lines, customer, state: PhantomData }
    }
}
impl Invoice<Issued> {
    fn record_payment(&self, payment: &Payment) -> Result<Receipt, PaymentError> { /* … */ }
}
```

- `add_line` on an issued invoice and `record_payment` on a draft fail to compile.
- Destructure in the transition, so a new field must be moved on by hand.

## Branded id family

When several kinds of id have one representation and the same methods, and values of different kinds travel in one struct or signature, write one `Id<K>` with a sealed marker trait and an alias per kind, so a swapped id fails to compile.

```rust
mod sealed {
    pub trait Sealed {}
}

/// An entity kind an [`Id`] can name.
pub trait IdKind: sealed::Sealed {}

/// The id of one entity of kind `K`.
pub struct Id<K> { raw: u64, kind: PhantomData<fn() -> K> }

/// An id whose kind is known only at run time, such as a column that may point at several kinds.
pub enum AnyKind {}

impl sealed::Sealed for User {}
impl IdKind for User {}
impl sealed::Sealed for Order {}
impl IdKind for Order {}

/// The id of a [`User`].
pub type UserId = Id<User>;
/// The id of an [`Order`].
pub type OrderId = Id<Order>;

impl<K: IdKind> From<Id<K>> for Id<AnyKind> {
    fn from(id: Id<K>) -> Self { Self { raw: id.raw, kind: PhantomData } }
}

// Hand-written, because #[derive] would require K: Clone, K: PartialEq, ...
impl<K> Clone for Id<K> { fn clone(&self) -> Self { *self } }
impl<K> Copy for Id<K> {}
impl<K> PartialEq for Id<K> { fn eq(&self, other: &Self) -> bool { self.raw == other.raw } }
impl<K> Eq for Id<K> {}
impl<K> Hash for Id<K> { fn hash<H: Hasher>(&self, state: &mut H) { self.raw.hash(state); } }
impl<K> fmt::Debug for Id<K> { fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { write!(f, "Id({})", self.raw) } }
```

- `PhantomData<fn() -> K>` keeps `Id<K>` `Send`, `Sync` and covariant whatever `K` is, and owns no `K`.
- `AnyKind` doesn't implement `IdKind`, so the erasing `From` doesn't overlap std's `From<T> for T`.
- Use separate newtypes when the kinds differ in validation or behaviour; the shared methods are the point of the family.

## Sealed traits

Seal a public trait that other crates use but must not implement: a marker or capability trait whose implementations the crate owns. A private supertrait does it:

```rust
mod sealed {
    pub trait Sealed {}
}

/// A table this crate knows how to write.
pub trait Table: sealed::Sealed {
    /// The table's name in the database.
    const NAME: &'static str;
}

impl sealed::Sealed for OrderRow {}
impl Table for OrderRow { const NAME: &'static str = "orders"; }
```

- The crate can add methods to the trait without a breaking change, because no outside impl exists.
- Never seal a seam other crates exist to implement (a plugin or backend trait).

## Extension traits

Write an extension trait only when a foreign type needs the same domain methods in two or more crates. Name it `<Type>Ext` and put it in the lowest crate both use.

```rust
/// Domain helpers on [`Path`].
pub trait PathExt {
    /// Whether the final component starts with a dot.
    fn is_hidden(&self) -> bool;
}

impl PathExt for Path {
    fn is_hidden(&self) -> bool {
        self.file_name().is_some_and(|name| name.as_encoded_bytes().starts_with(b"."))
    }
}
```

When the value lives in your own structs, write a newtype instead: it can also keep an invariant, which an extension trait can't.

## Associated types against generic parameters

Use an associated type when each implementation picks exactly one type (`Iterator::Item`), and a generic parameter when one type implements the trait for several (`From<T>`).

```rust
trait Parser {
    type Output;
    fn parse(&self, input: &str) -> Result<Self::Output, ParseError>;
}

struct Money { cents: i64 }
impl From<Cents> for Money { /* … */ }
impl From<WholeUnits> for Money { /* … */ }
```

- An associated type keeps call sites free of type arguments and lets the compiler infer the output.
- A trait used as `dyn` takes neither, unless every object names the same type (`Box<dyn Parser<Output = Order>>`). For a closed set of outputs, return an enum.

## `#[must_use]` plans and guards

Mark a type `#[must_use]` when dropping it unused loses work: a plan whose later `apply` does the writing, a staged result, or a guard. Put the attribute on the type, not on each function that returns it, so every constructor is covered.

```rust
/// Holds the lock file until dropped.
#[must_use = "the lock is released when the guard drops"]
pub struct LockGuard { path: PathBuf }

impl Drop for LockGuard {
    fn drop(&mut self) {
        // Drop can't return the error, so record it for whoever reads the logs.
        if let Err(error) = fs::remove_file(&self.path) {
            tracing::debug!(path = %self.path.display(), %error, "lock file not removed");
        }
    }
}
```

## `Cow<'a, str>`

Return `Cow` on a measured path where most inputs pass through unchanged, so the common case allocates nothing.

```rust
fn lowercased(name: &str) -> Cow<'_, str> {
    if name.chars().any(char::is_uppercase) { Cow::Owned(name.to_lowercase()) } else { Cow::Borrowed(name) }
}
```

Without a profile, return `String`: `Cow` spreads a lifetime through every caller.

## `SmallVec`

`SmallVec<[T; N]>` keeps up to `N` items inline and moves to the heap past that. Pick `N` from measured lengths, and use it where a profile shows the allocation of many short lists:

```rust
struct Order { tags: SmallVec<[Tag; 4]> } // 95% of orders carry four tags or fewer
```

An inline buffer makes the value larger to move. Without a profile, use `Vec`.

## Zero-copy deserialisation

Borrow strings from the input buffer instead of allocating each one. Use `Cow<'a, str>` with `#[serde(borrow)]` for any string that may contain escapes: a `&'a str` field fails to deserialise when the JSON string has one.

```rust
#[derive(Deserialize)]
struct LogLine<'a> {
    level: Level,
    #[serde(borrow)]
    message: Cow<'a, str>,
}

for raw_line in buffer.lines() {
    let line: LogLine<'_> = serde_json::from_str(raw_line)?;
    // Copy out what outlives the buffer.
    counts.record(line.level);
}
```

The struct is a short-lived view (SKILL.md, own the data): convert to owned types before the buffer drops.

## Lending iterators (GATs)

A std `Iterator` can't yield a borrow of its own buffer. A generic associated type can:

```rust
trait LendingIterator {
    type Item<'a> where Self: 'a;
    fn next(&mut self) -> Option<Self::Item<'_>>;
}

struct LineReader<R> { reader: R, buffer: String }

impl<R: BufRead> LendingIterator for LineReader<R> {
    type Item<'a> = io::Result<&'a str> where Self: 'a;

    fn next(&mut self) -> Option<Self::Item<'_>> {
        self.buffer.clear();
        match self.reader.read_line(&mut self.buffer) {
            Ok(0) => None,
            Ok(_) => Some(Ok(self.buffer.trim_end())),
            Err(error) => Some(Err(error)),
        }
    }
}
```

`for` loops and iterator adapters don't work on it; callers write `while let Some(line) = lines.next()`. For one type, an inherent `next_line(&mut self)` method does the same with no trait.

## Channels between stages

When a producer and a consumer run at different rates, connect them with a bounded channel, so a slow consumer slows the producer instead of growing memory. Each stage owns its state and listens for cancellation.

```rust
async fn write_batches(mut batches: mpsc::Receiver<Batch>, store: Store, token: CancellationToken) -> Result<(), WriteError> {
    loop {
        tokio::select! {
            () = token.cancelled() => return Ok(()),
            received = batches.recv() => {
                let Some(batch) = received else { return Ok(()) };
                store.write(&batch).await?;
            }
        }
    }
}

let (sender, receiver) = mpsc::channel::<Batch>(64);
let writer = tracker.spawn(write_batches(receiver, store, token.clone()));
```

- Make each `select!` branch a cancel-safe future (`recv` is). The arm body runs to completion, so the write goes there, not in a branch.
- Decide what a full channel means: `send().await` waits; `try_send` lets the producer drop and count.
- Await each stage's handle (`writer`) and handle its `Result`: a dropped handle drops the error.

## Arena allocation

Allocate many small nodes that live and die together from one arena (`bumpalo`, `typed-arena`), and free them all at once.

```rust
enum Expr<'a> { Number(i64), Add(&'a Expr<'a>, &'a Expr<'a>) }

let arena = Bump::new();
let one: &Expr<'_> = arena.alloc(Expr::Number(1));
let sum: &Expr<'_> = arena.alloc(Expr::Add(one, one));
```

Nodes borrow the arena, so the arena must outlive every reference to them. Skip it when nodes are freed one by one.

## Typed index vectors

Index a `Vec` with a domain index type, so an index into one table can't read another (`typed-index-collections`, or a few lines by hand):

```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
struct CustomerIdx(u32);

struct Customers { rows: Vec<Customer> }

impl Customers {
    fn push(&mut self, customer: Customer) -> CustomerIdx {
        let idx = u32::try_from(self.rows.len()).expect("a run holds fewer than 2^32 customers");
        self.rows.push(customer);
        CustomerIdx(idx)
    }

    fn get(&self, idx: CustomerIdx) -> &Customer { &self.rows[idx.0 as usize] }
}
```

`CustomerIdx` is made only by `push`, so an index from this table is always in bounds. An index from another `Customers` value can still panic; when several tables of one type coexist, give each its own index type with a marker parameter ([branded id family](#branded-id-family)).

## String interning

When the same keys are hashed and compared many times, store each distinct string once and pass a small `Copy` symbol (`lasso`, or a `Vec<Box<str>>` plus a map). Comparing symbols is an integer compare.

```rust
let mut names = Rodeo::default();
let sku = names.get_or_intern("SKU-1042"); // Spur: Copy, 4 bytes
```

Skip it when a key is compared once or twice: the interner's map costs more than it saves.

## Bit sets

Represent a set of small dense ids as bits (`fixedbitset`), so union and intersection run a word at a time.

```rust
let mut reachable = FixedBitSet::with_capacity(node_count);
reachable.union_with(&successors[node.0 as usize]);
```

Skip it for sparse or large ids: a `BTreeSet` or hash set uses less memory.

## Worklist to a fixpoint

When results depend on each other through cycles, keep a queue of items whose inputs changed, and process until it is empty.

```rust
let mut pending: VecDeque<NodeIdx> = graph.nodes().collect();
while let Some(node) = pending.pop_front() {
    let updated = transfer(&facts, node);
    if updated != facts[node] {
        facts[node] = updated;
        pending.extend(graph.successors(node));
    }
}
```

The facts must only grow (a lattice) so the loop ends. When the dependencies are acyclic, process in topological order instead.

## Incremental queries (salsa)

`salsa` memoises functions of inputs and re-runs only those whose inputs changed. It fits long-lived processes that re-derive after small edits (language servers, watch-mode builds). It is a framework: every derived value becomes a query, so adopt it for a whole subsystem or not at all.

## Enum dispatch

For a closed set that needs one interface, write an enum whose methods `match` on the variant. Calls inline, and the compiler checks every case.

```rust
enum Exporter { Csv(CsvExporter), Json(JsonExporter) }

impl Exporter {
    fn export(&mut self, row: &Row) -> Result<(), ExportError> {
        match self {
            Self::Csv(csv) => csv.export(row),
            Self::Json(json) => json.export(row),
        }
    }
}
```

Use it when `dyn` shows in a profile or the set is closed anyway. Keep `dyn` for sets open at run time.

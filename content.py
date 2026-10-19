"""Site content for draconyx.org: the single source for index.html, index.md and llms.txt.

Reasons 1-8 were fact-checked against the spec and the compiler on 2026-10-18 (adversarial
verifier per reason, code samples run through the compiler); reason 9 (context) and the name section were
checked by the site review the same day. Keep it that way:
change a claim only together with its citation.
"""

AS_OF = "18 October 2026"
CONTACT = "info@draconyx.ai"
# Set to the listmonk list UUID once the public "Draconyx updates" list exists; None keeps the form disabled.
LISTMONK_LIST_UUID = "240235c8-27a5-472b-b775-904925a1ceb6"
LISTMONK_FORM_URL = "https://lists.draconyx.ai/subscription/form"
SPEC_PDF = None  # "/draconyx-spec.pdf" once the renamed spec is published

HERO = {
    "eyebrow": "The programming language for AI authors",
    "headline": "Built for the machines that write your code.",
    "subhead": (
        "Python, Rust and Go were designed for a human at a keyboard. Draconyx was designed for the "
        "model in the loop: errors that come back as data, edits addressed by name and checked before they land, "
        "laws no release build ships without passing, and every service a function uses printed in its outline."
    ),
}

PROBLEM = [
    "Models now write code by the million lines, and they don't work like people. In the spec's words, a "
    "model does not read the documentation first and then write correct code: it generates, observes and "
    "repairs, hundreds of times, unattended.",
    "Python, Rust and Go hand that agent error text or half-structured JSON, make it patch files "
    "by string match, route it through tooling built around an editor cursor, and run its code where any import "
    "can open a socket. Every fix for that lives outside the language: a flag, a server, a sandbox. In Draconyx, "
    "the agent's interface is in the spec.",
    "Draconyx flips it. What the AI author needs is the language: \u201cnot leniency but a fast, precise, "
    "machine-readable verdict.\u201d The compiler never calls a model, and its agent daemon is a "
    "deterministic oracle: same tree, same answer, every time.",
]
PROBLEM_CITES = ["01-vision:71", "01-vision:77", "26-agent-interface:91-103"]

# Each reason: title, body paragraphs, unlike, sample (kind, text, caption), cites, status tag.
REASONS = [
    {
        "id": "diagnostics",
        "state": "ships",
        "title": "Errors are data. Not prose.",
        "body": [
            "Every checker emits one Diagnostic value: a stable AXnnnn code, byte-precise spans, an "
            "explanation, and suggested edits. Each edit carries an applicability (`always` or `maybe`), can carry "
            "`also` spans that apply all-or-nothing across files, and a `consequence`: the fact about the program "
            "that the edit makes true.",
            "When a name doesn't resolve, the spec's “hallucination contract” requires ranked candidates "
            "to come back as `maybe` edits. A model repairs from data instead of parsing prose. "
            "`drx explain` answers for every code the toolchain can emit, and a test enforces it.",
        ],
        "ships": "Ships today: the JSON channel, the ownership checker's two-file edits with consequences, ranked candidates "
                 "(by edit distance so far), explain for all 129 catalogued codes.",
        "unlike": "rustc's JSON has applicability but no per-edit consequence, and many diagnostics have no "
                  "code. CPython's “Did you mean” is prose. Go's compiler errors carry neither codes nor edits; fixes "
                  "come from gopls.",
        "sample": ("json", """$ drx check pkg --json
{"code": "AX0234", "severity": "error",
 "message": "unresolved name `add_amount`",
 "primary_span": {"file": "src/money.ax", "start": [7,5], "end": [7,15],
                  "bytes": [95,105]},
 "secondary_spans": [],
 "explanation": "a name resolves lexically: enclosing bindings, ...",
 "suggested_edits": [{"span": {..., "bytes": [95,105]},
   "replacement": "add_amounts", "applicability": "maybe",
   "description": "replace `add_amount` with `add_amounts`"}]}""",
                   "Real compiler output, trimmed."),
        "cites": ["25-tooling:9-26", "25-tooling:65-106", "25-tooling:143-165", "26-agent-interface:387-400"],
    },
    {
        "id": "edit-by-name",
        "state": "gaps",
        "title": "Edit by name. Never by line number.",
        "body": [
            "The agent daemon addresses code by qualified name (`inventory.reprice`), never by file and line. "
            "Writes are transactional: a write may carry the tree hash it was based on, and if the tree has "
            "moved, it is refused with the current hash and the current text.",
            "A fragment that doesn't parse never reaches the tree. The whole program is checked before a write "
            "is installed, so a batch that adds new errors is refused whole. The formatter splices canonical "
            "bytes and re-parses its own output. A failed check replies in the same shape as a success, with "
            "an applied flag, the tree hash, the diagnostics and an impact diff, so the agent never needs a "
            "second query to learn what its edit did.",
        ],
        "ships": "Ships today in `drx serve` and `drx rpc`. Still owed: auto-import, canonical splicing "
                 "of nested members, a crash-atomic disk mirror, and re-reading the workspace before a write "
                 "(today `base` is checked against the daemon's in-memory tree, so edits made outside it are missed).",
        "unlike": "Python, Rust and Go define no such write interface. Agents patch text by string "
                  "match, diff hunks or range-keyed LSP edits. Codemod tools (LibCST, rust-analyzer "
                  "SSR) are add-ons with no tree-hash precondition, no type check before the bytes land and no "
                  "impact report.",
        "sample": ("shell", """$ drx rpc . put-def '{"address": "inventory.reprice",
    "base": "deadbeef", "text": "def reprice(...) -> Int: ..."}'

# the workspace moved since `base`: refused, with the current text
{"code": -32000, "message": "the workspace has moved since `base`",
 "data": {"kind": "conflict", "detail": {"base": "deadbeef",
   "current_tree": "19c75982...", "addresses": ["inventory.reprice"],
   "current": [{"address": "shop.inventory.reprice",
     "text": "def reprice(price: Int, pct: Int) -> Int:\\n    price + price * pct / 100\\n"}]}}}

# a write that fails the check: same shape as success, nothing written
{"tree": "19c75982...", "applied": false, "new_errors": 1,
 "diagnostics": [{"code": "AX1001",
   "message": "type mismatch: expected `Int`, found `String`"}],
 "impact": {"broken_consumers": [{"address": "shop.inventory.reprice",
   "codes": ["AX1001"]}]}}""", "Real daemon replies, abridged (hashes trimmed, fields elided)."),
        "cites": ["26-agent-interface:66-89", "26-agent-interface:412-494", "25-tooling:565"],
    },
    {
        "id": "authority",
        "state": "gaps",
        "title": "No global open(). Every service on the record.",
        "body": [
            "The rule is “no ambient permission”: there is no global `open` and no standard function that "
            "reaches the world on its own authority. Every permission comes from the `System` passed into `main` "
            "and flows down by explicit provision.",
            "The compiler works out which services each definition reaches, through callees and function "
            "values. A gap is compile error AX0501, naming the whole call chain, and `drx outline` prints "
            "each definition's uses and needs. A host can wrap an AI-written plan in `scope_to(...)` and know "
            "from the outline exactly which services it can reach.",
        ],
        "ships": "Ships today: AX0501 with call chains, uses/needs in the outline. Specified, not yet enforced: "
                 "unforgeable handles. Today's checker still lets user code construct standard handles such "
                 "as `File(descriptor)`; closing that comes before we claim “by construction”.",
        "unlike": "In Python, Go and Rust any imported module can open files or sockets on ambient "
                  "process authority. Confinement comes from outside the type system (containers, seccomp, "
                  "the third-party cap-std crate for Rust). None checks per function, at "
                  "compile time, what a function can reach.",
        "sample": ("draconyx", """provide locally:
    FileSystem = scope_to(fs = borrow system.filesystem, root = Path("/tmp/agent-sandbox"))
    Clock      = system.clock
in:
    run_generated_plan()
// If the plan reaches Network, compilation fails:
//   error[AX0501]: Missing provider: service 'Network'
//     required by  main
//     reached from run_generated_plan
//     reached from upload
//     no 'provide Network' in any enclosing scope""", "Checked with the compiler."),
        "cites": ["12-services-di-permissions:221-263", "12-services-di-permissions:83-106", "12-services-di-permissions:299-314", "26-agent-interface:228-234"],
    },
    {
        "id": "tainted",
        "state": "gaps",
        "title": "Prompt injection meets the type checker.",
        "body": [
            "`tainted` is a type qualifier. Model completions, console input, network reads and process "
            "arguments are born tainted at their standard-library signatures. A tainted value where a plain "
            "type is expected is compile error AX1022, and every parameter that steers what the program does "
            "is such a position: a prompt's instruction, SQL identifiers, process arguments, permission-minting "
            "arguments.",
            "The only way out is `endorse` with a mandatory rationale, so every place untrusted text becomes "
            "trusted is one line you can grep for.",
        ],
        "ships": "Ships today: AX1022 at every argument, field, return, binding and collection element; taint "
                 "through field projection and generic code; the prompt-instruction barrier. Specified, not "
                 "yet built: the SQL and process-argument barriers, and taint through string interpolation.",
        "unlike": "Python, Go and Rust treat model output as a plain string. A newtype can imitate "
                  "a taint marker by convention, but the standard library never marks its sources and nothing "
                  "makes unwrapping state a reason. Real defences are runtime libraries or separate analysers "
                  "such as CodeQL and Semgrep.",
        "sample": ("draconyx", """def hijacked(email: tainted String) -> Prompt:
    // AX1022: `instruction` is an unmarked String,
    // a control-plane position no tainted value may occupy
    prompt(instruction = email, data = [])

def summarize(transfer email: tainted String) -> Prompt:
    prompt(instruction = "Summarize the message.", data = [transfer email])  // OK""", "Checked with the compiler."),
        "cites": ["12-services-di-permissions:460-517"],
    },
    {
        "id": "laws",
        "state": "ships",
        "title": "Laws are checked. Not trusted.",
        "body": [
            "Capabilities carry algebraic laws as syntax, and a law with no mode is checked. `drx test` "
            "synthesizes a property test for it, draws inputs from a fixed seed, shrinks any failure to a "
            "minimal counter-example and records it in a regression file that later runs replay first. "
            "Release builds require checked laws to pass; skipping one takes an explicit `trust`, and the test "
            "target warns about each.",
            "Dispatch picks implementations by the laws a type asserts, so the spec counts a false law as a "
            "miscompilation. An obligation the toolchain could not evaluate is reported as “not run”, never as "
            "a pass, and a `todo()` body gets its own `UNIMPLEMENTED` verdict instead of a fake failure.",
        ],
        "ships": "Ships today in the v0 toolchain. Specified, not yet built: the violation report that lists "
                 "every site resting on the law and offers exactly two repairs.",
        "unlike": "Python, Rust and Go state laws like Ord/Hash consistency only in documentation; "
                  "the compiler never sees them. Property testing is a third-party library (Hypothesis, "
                  "proptest) or, in Go, stdlib testing/quick and fuzzing, and someone must restate each law as a "
                  "test by hand.",
        "sample": ("draconyx", """capability Monoid:
    def add(transfer self: Self, transfer other: Self) -> Self
    def zero() -> Self
    law associative: add(self = add(self = left, other = middle), other = right)
        == add(self = left, other = add(self = middle, other = right))
    law identity: add(self = value, other = zero()) == value

def median(values: List<Float>) -> Float:
    todo()  // verdict UNIMPLEMENTED, not a failure
example median(values = [1.0, 3.0, 2.0]) == 2.0""", "Checked with the compiler."),
        "cites": ["13-law-verification:4-97", "13-law-verification:319-345", "13-law-verification:400-409", "10-capabilities:88-101"],
    },
    {
        "id": "calls",
        "state": "ships",
        "title": "Every named call tells the truth.",
        "body": [
            "Named arguments are mandatory at every call of a declared function with two or more arguments; an unlabelled one is "
            "AX0256, and the error lists the callee's labels. Ownership is spelled the same at both ends of a "
            "call: unmarked is read-only, `borrow` is exclusive mutation, `transfer` consumes. A mismatch is "
            "AX0306, and using a value after it moved is AX0312.",
            "A positional swap of a declared function's arguments can't be written, a mislabelled argument shows on the call line, and a mutation "
            "or consumption the call doesn't spell won't compile. An agent reads what happens to each argument "
            "from the call alone.",
        ],
        "ships": "Ships today: all three diagnostics.",
        "unlike": "Rust and Go have no named arguments, so `resize(height, width)` compiles and looks right. "
                  "Python's keywords are optional unless the author opts in. Rust marks `&mut` but not a move, and method calls auto-borrow "
                  "their receiver unmarked. Go passes slices, maps and pointers unmarked while the callee "
                  "mutates through them.",
        "sample": ("draconyx", """def open(url: String, timeout: Duration) -> Result<Connection>
def close(transfer conn: Connection) -> Unit
def send(borrow conn: Connection, request: Request) -> Result<Unit>

def ping_once(address: String, ping: Request) -> Result<Unit>:
    let conn = open(url = address, timeout = seconds(5))?
    send(borrow conn, request = ping)?  // mutation is spelled here
    close(transfer conn)  // consumption is spelled here
    close(transfer conn)  // AX0312: use of moved value `conn`
    Ok(unit)""", "Checked with the compiler."),
        "cites": ["05-syntax-conventions:3-4", "04-core-language:251-272", "04-core-language:1624-1640", "07-memory-model:253-285"],
    },
    {
        "id": "failure",
        "state": "ships",
        "title": "No exceptions. No missing arms. No mercy.",
        "body": [
            "There are no exceptions and no try/catch. Failure is `Ok/Err`, and `?` has an exact desugaring into a "
            "match. A panic is for bugs only, no construct catches it locally, and every panicking operation "
            "has a total twin that returns `Option`.",
            "`match` is checked with the constructor-matrix algorithm: a missing case is error AX0601, naming the "
            "uncovered constructors, and a redundant arm is error AX0602, not a warning. An agent sees every "
            "recoverable failure in a call's type and gets an exact to-do list for any case it missed.",
        ],
        "ships": "Ships today: AX0601 and AX0602 as errors.",
        "unlike": "In Python and C++ exceptions are invisible in signatures: you meet them in production. "
                  "Go hands you `err` and hopes you check it. Rust comes closest, but `catch_unwind` can catch a panic "
                  "on the spot, and an unreachable arm is only a warn-by-default lint. In Draconyx a redundant arm is "
                  "a hard error.",
        "sample": ("draconyx", """enum PaymentState:
    Pending
    Authorized(Money)
    Captured(Money)
    Refunded(reason: String, amount: Money)

def label(payment_state: PaymentState) -> String:
    match payment_state:
        Pending       -> "pending"
        Authorized(_) -> "authorized"
        Captured(_)   -> "captured"
// error[AX0601]: non-exhaustive match: missing `Refunded(_, _)`""", "Checked with the compiler."),
        "cites": ["04-core-language:545-645", "11-type-system:444-498"],
    },
    {
        "id": "determinism",
        "state": "ships",
        "title": "Same tree, same answer. Every time.",
        "body": [
            "`drx serve` is a local JSON-RPC 2.0 daemon. Every response is a pure function of the toolchain "
            "hash, the lockfile and the source-tree hash, and carries that tree hash; the one exception is a "
            "verify cut short by its time budget, and the response says so. Lists paginate deterministically "
            "and are never silently truncated, and errors carry a stable kind that code can branch on.",
            "Each definition is hashed over its typed core: comments, layout and local variable names leave the "
            "hash unchanged, while `count * 2` becoming `2 * count` moves it. The daemon holds no ambient authority, and "
            "its handshake lists everything it can reach.",
        ],
        "ships": "Ships today.",
        "unlike": "pyright, rust-analyzer and gopls speak LSP: definitions addressed by file and "
                  "cursor, per-document versions but no whole-tree hash, no byte-identical guarantee, no "
                  "authority model. rust-analyzer routinely runs cargo, build scripts and proc macros.",
        "sample": ("json", """→ {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
← {"jsonrpc": "2.0", "id": 1, "result": {"protocol": "jsonrpc-2.0/ndjson",
   "toolchain": "25bb73aed9ee4627...", "tree": "c002b18c7945ac6c...",
   "methods": ["delete-def", "delta-card", "diagnostics", "fork", "get-def", ...],
   "authority": ["read: the workspace source tree",
     "read: the synthesized standard library",
     "write: workspace source under the package root",
     "no network", "no home directory", "no process spawning"]}}""",
                   "Real daemon handshake, abridged."),
        "cites": ["26-agent-interface:31-61", "26-agent-interface:91-127", "25-tooling:501-522"],
    },
    {
        "id": "context",
        "state": "gaps",
        "title": "Every surprise in the language, on one 2,000-token card.",
        "body": [
            "Draconyx doesn't wait for models to learn it from the internet: the toolchain brings the knowledge "
            "straight into the context window, in name-shaped, budgeted pieces. `outline` gives each definition's signature, "
            "derived facts such as uses and needs, its evidence line and the first line of its documentation. "
            "`slice` returns the minimal reading set for editing one definition and degrades deterministically "
            "to fit a token budget (docs first, then private helper signatures, never public ones); `search` "
            "returns ranked results that paginate deterministically.",
            "Two hard-capped cards brief an agent directly: the delta card, at most 2,000 tokens, lists where "
            "the language departs from what a model expects; the resume card lets an agent pick up work where "
            "it left off.",
        ],
        "ships": "Ships today: outline, slice, search, `delta-card` and `resume-card` as daemon methods. Card "
                 "contents are partial: the dialect grammar cards the spec requires are not emitted yet, and the "
                 "resume card's budget is still measured over its JSON envelope. Token budgets use a declared "
                 "bytes/4 estimate until the specified reference tokenizer is pinned.",
        "unlike": "Assembling context is the agent framework's job (repository maps, embeddings, file reads); "
                  "the language defines no briefing format and no token budget.",
        "sample": None,
        "cites": ["26-agent-interface:183", "26-agent-interface:228-234", "26-agent-interface:648", "26-agent-interface:306-324", "26-agent-interface:739-740"],
    },
]

# Big numbers for the stats band (all from STATUS, as of AS_OF).
STATS = [
    ("522", "pages of normative spec"),
    ("51k", "lines of compiler written in Draconyx"),
    ("129", "diagnostic codes, each explained"),
    ("5", "compiler stages also written in the language"),
    ("209", "design rulings ratified"),
]

# The loop the language is built for (spec 01-vision:71: generate, observe, repair).
LOOP = [
    ("Generate", "The model writes one definition, addressed by its name."),
    ("Check", "The whole program is checked before a single byte lands."),
    ("Verdict", "Errors come back as data: a stable code, exact spans, ranked fixes."),
    ("Repair", "The model applies the fix, or reads the counter-example a law produced."),
]

# The whole language: (group title, [(name, pitch, status)]). status: ships | partial | specified.
FEATURE_GROUPS = [
    ('Types and algebra', [
        ('Capabilities: named, but never declared', 'Write the functions and the type conforms. No impl blocks, and no two modules can give one type two meanings.', 'ships'),
        ('Algebraic laws as code, checked at build time', 'In C++ and Rust, associativity is a line in the docs. In Draconyx it is a `law` line, and a false one fails the build with a shrunk counter-example.', 'partial'),
        ('Dispatch on algebra', 'Write the parallel reduction once. The compiler picks it only for types that assert the laws that make it correct.', 'ships'),
        ('Generics that infer the hard parts', 'Variance, associated types and const-generic shapes are worked out by the compiler, not annotated by the model.', 'partial'),
    ]),
    ('Memory and ownership', [
        ('Ownership spelled at both ends', 'Every handover is written where the value is given and again where it is taken, so a model never has to guess who owns what.', 'ships'),
        ('Borrow checking with zero lifetime syntax', "Rust-grade memory safety without a single `'a`: you never write a lifetime, and the compiler works out every one.", 'ships'),
        ('Views inferred, not annotated', 'Put a borrow in a struct and it becomes a safe view on its own: no keyword, no lifetime parameter.', 'ships'),
        ('No garbage collector, deterministic drops', 'No tracing GC and no pauses: each value is freed the moment its last owner lets go.', 'partial'),
    ]),
    ('Concurrency and distribution', [
        ('Data-race freedom by construction', 'No Send, no Sync, no annotations: the ownership authorities you already write decide what may cross a task boundary.', 'partial'),
        ('Structured concurrency with `with nursery`', "Tasks can't leak, and child tasks may mutably borrow the parent's data with no locks.", 'partial'),
        ('Move-only channels and a fair, replayable `select`', 'Every message exists in exactly one place at a time, and `select` timeouts run on a Clock you can fast-forward in tests.', 'partial'),
        ('Actors and OTP supervision without exceptions', 'Erlang-style let-it-crash supervision trees, with errors staying plain Ok/Err data.', 'partial'),
        ('Remote values that cannot hide failure', 'In Draconyx a network call never looks like a local call: `remote` is in the type, and every way it can fail is a value you have to match on.', 'partial'),
        ('Bundled distributed runtime', 'Cluster membership, Raft consensus and CRDTs live in every binary as ordinary types: no ZooKeeper, no Consul, no sidecar.', 'specified'),
        ('Hot code swap with checked state migration', 'Erlang-style hot swap for compiled code: the swap point is proven safe, state is handed over as a linear move, and migrations are functions the compiler checks.', 'specified'),
        ('Native binaries today; unikernel and Wasm next', '`drx build` produces a native executable; the same source targets a unikernel that needs no OS underneath, or a WebAssembly module.', 'partial'),
    ]),
    ('Safety and effects', [
        ('Services and dependency injection', 'Declare a service, `provide` it once in main, and every function underneath can use it. You get no constructor plumbing, no effect rows, and a compile error if a provider is missing.', 'ships'),
        ('Object-capability permissions (no ambient authority)', "No global `open` and no importable `Network`: the only way code gets authority is to be handed it. Starting from main's `System` powerbox, it can only be narrowed, never widened.", 'partial'),
        ('`tainted`: a typed defense against prompt injection', "Model output, console input and the command line are born `tainted`. Passing one to an unmarked parameter, or to a prompt's instruction slot, is compile error AX1022.", 'partial'),
        ('`trust` blocks: unsafe code that names its reason', 'Draconyx has no `unsafe`. It has `trust "why this holds":`, where every unchecked call site carries a mandatory written rationale an auditor can grep.', 'partial'),
        ('With blocks: one keyword for receiver, destructuring and scoped release', "One `with` covers Python's context managers, Rust's RAII and multi-value destructuring, even at the end of a pipeline.", 'ships'),
    ]),
    ('AI and numerics', [
        ('Shapes and named axes in the type', "A tensor's dtype, axis names and sizes belong to its type, so a mismatched matmul fails at compile time, before any array is allocated.", 'partial'),
        ('grad, vmap, jit as typed function transforms, with schedules certified by laws', 'Autodiff, auto-batching and fusion are plain functions over functions, and schedule rewrites are gated by laws instead of being trusted.', 'specified'),
        ('Hygienic, typed dialects (macros, elab, comptime)', 'Dialects extend the syntax with Racket-grade hygiene and type-directed elaboration, without textual macros.', 'specified'),
    ]),
]

# Head-to-head: only rows where Draconyx ships today. Cells verified per language (2026-10-18).
VERSUS_LANGS = ['Draconyx', 'Python', 'Java', 'Kotlin', 'C#', 'C++', 'Rust', 'Go', 'Swift', 'Zig', 'Elixir', 'Haskell', 'Mojo']
VERSUS = [
    ('Every error has a code and an explain entry, with JSON repair edits from the compiler itself', ['yes', 'no', 'part', 'part', 'part', 'part', 'part', 'no', 'part', 'no', 'no', 'part', 'no']),
    ("Edits addressed by definition name, type-checked before they're written", ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
    ('Compiler-computed map of the services each function reaches, through the whole call chain', ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
    ('Model output typed untrusted at its standard-library source', ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
    ("Algebraic laws property-tested by default by the compiler's own test command", ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
    ('Named arguments required at every multi-argument call of a declared function', ['yes', 'part', 'no', 'no', 'no', 'no', 'no', 'no', 'part', 'no', 'no', 'no', 'part']),
    ('Mutation and moves spelled at the call site', ['yes', 'no', 'no', 'no', 'part', 'part', 'part', 'no', 'part', 'part', 'no', 'no', 'part']),
    ('Missing and redundant match arms both rejected, on every match', ['yes', 'no', 'part', 'part', 'part', 'part', 'part', 'no', 'part', 'yes', 'no', 'part', 'no']),
    ('Deterministic agent protocol: same source tree, byte-identical answers', ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
    ('Ownership and borrows checked at compile time, with no tracing garbage collector and no lifetime annotations', ['yes', 'no', 'no', 'no', 'no', 'no', 'part', 'no', 'part', 'no', 'no', 'no', 'part']),
    ('Generic code dispatches on the algebraic laws a type satisfies, with arm totality checked', ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
]
# The fine print for every "part"/"yes" a competitor gets, so nobody has to take our word for it.
VERSUS_NOTES = {
    'Python': [
        'Named arguments required at every multi-argument call of a declared function: The author can opt in with keyword-only parameters after a bare `*` (PEP 3102), and calling them positionally is then a TypeError. But that is opt-in, and the error comes at run time, not compile time.',
    ],
    'Java': [
        'Every error has a code and an explain entry: javac has stable internal diagnostic keys (e.g. compiler.err.cant.resolve), shown with -XDrawDiagnostics, but has no explain command and no machine-readable fixes. Quick-fixes come from IDEs (Eclipse JDT problem IDs, IntelliJ).',
        'Missing and redundant match arms both rejected: Switch expressions and pattern switches must be exhaustive over enums and sealed types (compile error). Dominated case labels and duplicate constants are compile errors too.',
    ],
    'Kotlin': [
        'Every error has a code and an explain entry: K2 diagnostics have internal names such as UNRESOLVED_REFERENCE. The documented -Xrender-internal-diagnostic-names flag prints them alongside warnings, and @Suppress and -Xwarning-level accept warning names. kotlinc has no explain command and no machine-readable repair edits; quick-fixes come from the IDE, not the compiler.',
        'Missing and redundant match arms both rejected: A when used as an expression must be exhaustive on any subject (a compile error otherwise), and since Kotlin 1.7 a when statement on an enum, sealed or Boolean subject must be too. A when statement on other subjects, such as Int or String, can leave cases out. Duplicate conditions and a redundant else only get warnings.',
    ],
    'C#': [
        'Every error has a code and an explain entry: Every Roslyn diagnostic has a stable CSxxxx ID, and analyzers/code fixes ship in the SDK (dotnet format applies them). There is no built-in explain command; explanations live in the docs on learn.microsoft.com.',
        'Mutation and moves spelled at the call site: `ref`/`out` (and optionally `in`) must be written at the call site. Mutation through reference-type arguments and receivers is unmarked, and there is no move semantics.',
        'Missing and redundant match arms both rejected: A subsumed/unreachable arm is an error (CS8510 in switch expressions, CS8120 in switch statements). A non-exhaustive switch expression is only warning CS8509, switch statements get no exhaustiveness check, and there are no closed union types even in C# 14.',
    ],
    'C++': [
        'Every error has a code and an explain entry: There is no single reference compiler. MSVC gives errors stable codes (C2065, C2440...) with an online docs entry for each, but it has no built-in explain command. Clang and GCC emit machine-readable fix-its (clang -fdiagnostics-parseable-fixits;',
        'Mutation and moves spelled at the call site: To move from a named lvalue you must write std::move/std::forward at the call site. Moves of temporaries and return values are implicit, and std::move is only a cast, so a moved-from object stays usable. Mutation through a non-const reference parameter or a method receiver is not marked.',
        'Missing and redundant match arms both rejected: A duplicate case label in a switch is always a compile ERROR. A missing enumerator in an enum switch is a warning (-Wswitch, on in -Wall) and becomes an error only by opt-in (-Werror=switch).',
    ],
    'Rust': [
        'Every error has a code and an explain entry: Many rustc errors carry stable E-codes with `rustc --explain`, and `--error-format=json` emits suggestions marked MachineApplicable, which `cargo fix` / `cargo clippy --fix` apply. Not every diagnostic has a code: many errors and all lints lack E-codes.',
        'Mutation and moves spelled at the call site: `&mut buffer` is written at the call site for free-function args. Moves are not marked, and method calls auto-borrow `&mut self` without a marker.',
        'Missing and redundant match arms both rejected: A non-exhaustive match is a hard error (E0004) on every match. Unreachable or redundant arms only trigger the warn-by-default `unreachable_patterns` lint (an error only with deny/-D warnings).',
        "Ownership and borrows checked at compile time: Use-after-move and aliased &mut are rejected statically, with no tracing GC. But Rust has lifetime annotation syntax ('a), so it meets two of the three conditions.",
    ],
    'Swift': [
        'Every error has a code and an explain entry: Swift 6.1/6.2 diagnostic groups (e.g. [#StrictMemorySafety]) have names and documentation pages, but most errors have no code. Fix-its are built in and can be exported in machine-readable form (serialized diagnostics, -emit-fixits-path).',
        'Named arguments required at every multi-argument call of a declared function: Argument labels are required by default at every call, but the author can opt out per parameter with _.',
        'Mutation and moves spelled at the call site: & is required at the call site for inout. consume (SE-0366) is optional. Mutating method calls on receivers are not marked.',
        "Missing and redundant match arms both rejected: A non-exhaustive switch is a compile error. A duplicate or unreachable case is only a warning ('case is already handled by previous patterns').",
        'Ownership and borrows checked at compile time: Swift uses ARC, not a tracing GC. It has no stable lifetime syntax (@lifetime for ~Escapable is still experimental). ~Copyable types reject use-after-consume statically.',
    ],
    'Zig': [
        "Mutation and moves spelled at the call site: This goes against the rule's 'no' on purpose. Zig parameters are immutable, so a caller has to write &x at the call site to let a callee mutate a local, much like Rust's &mut. Method receivers auto-take the address, an already-held pointer passes unmarked, and moves don't exist.",
        'Missing and redundant match arms both rejected: On an enum or tagged-union switch, a missing prong is a compile error, so is a duplicate prong, and so is an else prong once every case is handled. (Integer switches need an else.)',
    ],
    'Haskell': [
        "Every error has a code and an explain entry: Since 9.6, GHC tags most diagnostics with [GHC-nnnnn] codes, and -fdiagnostics-as-json emits them, but GHC ships no explain command. The Haskell Foundation's separate error index documents only about 141 codes, and the JSON hints are prose strings, not machine-applicable repair edits.",
        'Missing and redundant match arms both rejected: -Woverlapping-patterns (redundant arms) is on by default and -Wincomplete-patterns (missing arms) comes with -W or -Wall, but both are warnings; rejecting a match takes -Werror or -Werror=incomplete-patterns.',
    ],
    'Mojo': [
        "Named arguments required at every multi-argument call of a declared function: Mojo supports Python-style keyword-only parameters (after `*` in the signature), so an author can opt in to required labels, as in Python. The default is optional. The rule's draft lists Mojo as no, but scoring it the same as Python means part.",
        'Mutation and moves spelled at the call site: Ownership transfer is written `buffer^` at the call site, but passing to a `mut` parameter is unmarked.',
        "Ownership and borrows checked at compile time: Static move and borrow checking (use-after-move, argument exclusivity, and reference-invalidation diagnostics in 1.0), ASAP destruction with no tracing GC, but explicit origin parameters (Mojo's lifetimes) exist. That is two of three.",
    ],
}

NAME = [
    "Draconyx (“dragon claw”) is a Late Jurassic ornithopod dinosaur from Portugal: a real creature.",
    "Its first half, Latin draco from Greek drákōn, is also the name of Draco, who around 621 BC gave Athens its first "
    "written laws: rules set down in public for every citizen to read, instead of kept and interpreted by "
    "a few. That is the idea here, laws written in the code and enforced by the machine.",
    "Athens inscribed its laws on rotating wooden tablets called axones. When Draco's homicide law was "
    "republished in 409/8 BC, the stone copy was headed “first axon”. Draconyx source files end in `.ax`.",
    "And yes, draconian: about correctness, so your agents don't have to be.",
]
NAME_SOURCE = ("Attic Inscriptions Online, ML 86: decree to republish Draco's law on homicide",
               "https://atticinscriptions.com/inscription/ML/86")

STATUS = [
    ("Specification", "31 normative sections, a 522-page PDF with 563 code blocks that the corpus tool turns into test oracles."),
    ("Toolchain", "Lexer, parser, resolver, type checker, ownership checker, interpreter with law runner, canonical formatter, agent daemon and native code generation."),
    ("Agent daemon", "20 JSON-RPC methods, among them outline, get-def, slice, search, put-def, put-defs, fork, verify, `delta-card` and `resume-card`."),
    ("Diagnostics", "129 codes, each with an explain entry; a test enforces the coverage."),
    ("Self-hosting", "The lexer, parser, resolver, type checker and ownership checker are written in Draconyx itself, about 51,000 lines. The ownership checker port is the stage in progress."),
    ("Latest full gate", "9 October 2026, all green on the shared test corpus: lexer 775/775, parser 1270/1270, resolver 966/966, type checker 1015/1015, ownership 1015/1015, native code vs interpreter 105/105."),
    ("Design record", "209 numbered rulings ratified into the spec; four example packages, among them an online shop, event sourcing and FlashAttention, and a 3,426-line standard library generated from the spec."),
    ("Release", "Pre-release research project, first commit 20 July 2026. The first public release comes when the first compiler written entirely in Draconyx is ready."),
]


SIGNUP_TITLE = "Stay tuned"
SIGNUP_LEAD = (
    "The dragon is hatching. Be first to know when Draconyx launches, and hear about every new feature "
    "the moment it lands. Updates only, straight from the source. One click to leave."
)
SIGNUP_FINE = "We send a confirmation link first. Nothing arrives until you click it."

INVOLVED = (
    "Want in early? For design discussion, collaboration, or to train or evaluate models on Draconyx, write to "
    f"{CONTACT}."
)

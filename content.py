"""Site content for draconyx.ai: the single source for index.html, index.md, llms.txt, the opinions page and the
changelog page.

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
    FileSystem = scope_to(filesystem = borrow system.filesystem, root = Path("/tmp/agent-sandbox"))
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

# Footer note. Keep it true of the server (infra runbook, "Website statistics"; listmonk privacy settings):
# Caddy access log rolled daily and deleted after about 14 days, monthly/all-time totals with anonymised IPs,
# listmonk record_optin_ip off, view/click tracking off, double opt-in.
PRIVACY = (
    "This site sets no cookies, runs no tracking scripts and loads nothing from other sites. Its web server logs each "
    "request: your IP address, the time, the page, and what your browser sends with it, such as its name and the page "
    "that linked here. The logs are kept about 14 days for security and visitor statistics, then deleted; after that, "
    "the statistics keep only totals, without full IP addresses. The signup form sends your email address to the "
    "Draconyx list at lists.draconyx.ai, on the same server: you get a confirmation email first and nothing else until "
    "you confirm, the list does not record your IP address or which emails you open or links you click, and every "
    f"update has an unsubscribe link. Questions: {CONTACT}."
)

# Second opinions: what AI models said about the spec. Six models were given the specification (and the site)
# between 29 October and 2 November 2026 (the dates of the saved answers) and asked the four questions below. The
# questions went through a service that calls the models, so none knew who was asking (the spec itself carries the
# author's name; the models did not know the asker was him). DeepSeek and Muse Spark
# answered twice, on two revisions of the spec. The full answers are kept by the author. Every quote is verbatim: "…" marks a cut, [Draconyx] stands where an answer used the earlier working
# title, a nested quotation gets single quotes, a cut sentence may start with a capital or end on a full stop, and
# `backticks` only set code in monospace. Nothing else is changed. Keep it that way: add a quote only from an answer,
# word for word. Models in alphabetical order; tags name the question each quote answers.
OPINIONS_URL = "/what-models-think/"
OPINIONS_TITLE = "What AI models think of Draconyx"
OPINIONS_HEADLINE = "What the models think"
OPINIONS_LEDE = ("We gave the Draconyx specification to six AI models and asked them the same four questions. "
                 "None knew who was asking.")
OPINIONS_METHOD = (
    "The questions went through a service that calls each model. Asked between "
    "29 October and 2 November 2026. The excerpts are verbatim: \u201c\u2026\u201d marks a cut, and [Draconyx] stands "
    "where an answer used the language's earlier working title."
)
OPINIONS_CREDITS = "Logos are trademarks of their owners and only identify the models quoted."
OPINIONS_ICONS_SOURCE = ("Lobe Icons", "https://github.com/lobehub/lobe-icons")  # MIT; see assets/models/
OPINIONS_QUESTIONS = [
    "What do you think of this programming language?",
    "Is it the future?",
    "On paper, is it better than Rust?",
    "Is dependency injection built into the language a good idea?",
]
OPINIONS = [
    {"id": "deepseek", "name": "DeepSeek", "maker": "DeepSeek", "note": "read two revisions of the spec",
     "headline": "Draconyx is the most complete and intellectually serious language specification I have ever read.",
     "quotes": [
         ("The language", "The language is a magnificent blueprint. Whether the building can be constructed is the "
                          "grand experiment."),
         ("The language", "The `when T : Add associative -> parallel_tree_reduce` dispatch is what Haskell type "
                          "classes wish they were — the compiler acts on laws, so a false assertion is a "
                          "miscompilation…"),
         ("The future", "If it pans out, Draconyx (or something built on its ideas) is the language the AI age "
                        "deserves. If it doesn't, it's still the most important language design document of the "
                        "2020s, and its ideas will shape whatever comes next."),
         ("Versus Rust", "The question is not whether Draconyx is better than Rust on paper — it is."),
         ("Dependency injection", "Draconyx's design is, I think, the best balance I've seen."),
     ]},
    {"id": "gemini", "name": "Gemini", "maker": "Google",
     "headline": "Embedding Dependency Injection directly into the language is a brilliant evolution of effect "
                 "systems.",
     "quotes": [
         ("The language", "By replacing prose documentation with compiler-verified algebraic laws and treating LLM "
                          "invocations as secure, isolated services, it natively treats AI as both the primary "
                          "developer and a first-class component of the software."),
         ("The future", "…the current shift toward AI-generated systems gives [Draconyx] a unique wedge."),
         ("Versus Rust", "On paper, [Draconyx] takes direct aim at Rust's steepest learning curves."),
         ("Dependency injection", "This makes executing untrusted or hallucinated AI-generated code fundamentally "
                                  "safer by default."),
     ]},
    {"id": "grok", "name": "Grok", "maker": "xAI",
     "headline": "This is one of the most ambitious, coherent language designs I’ve seen in years.",
     "quotes": [
         ("The language", "That inversion (model proposes, compiler judges and is cacheable/replayable) is the "
                          "strongest part of the vision."),
         ("The language", "This is serious, high-quality language design work aimed at a real shift in how "
                          "software is written. It is not vapor…"),
         ("The future", "I would not bet against the direction."),
         ("Versus Rust", "Rust’s trait contracts are documentation. Here they gate algorithm selection and "
                         "optimizations and are verified… That is a genuine step beyond what Rust (or any "
                         "mainstream language) does."),
         ("Dependency injection", "The design also makes the model itself just another service (with taint, "
                                  "budgets, and recorded transcripts). That is the right abstraction if models are "
                                  "going to be first-class components of programs."),
     ]},
    {"id": "kimi", "name": "Kimi K3", "maker": "Moonshot AI",
     "headline": "This is a 522-page act of unusually disciplined ambition: the best-conceived ‘AI-native language’ "
                 "design I’ve seen…",
     "quotes": [
         ("The language", "The spec is unusually self-aware. … That kind of epistemic honesty is vanishingly rare "
                          "in language projects, and it makes me trust the document’s other claims more, not less."),
         ("The language", "Laws as compiler-consumed objects. … This is the one feature with no real analogue in "
                          "any mainstream language…"),
         ("The future", "Verified authorship loops … are a real gap nobody else is filling."),
         ("Versus Rust", "This is arguably a better surface syntax than Rust’s `&T`/`&mut T`/move-by-default, "
                         "because a reader can tell from the call alone whether a value is consumed, mutated, or "
                         "shared — no signature lookup needed."),
         ("Dependency injection", "…no ambient `open()` anywhere is a property every language should have and "
                                  "almost none do."),
     ]},
    {"id": "muse-spark", "name": "Muse Spark", "maker": "Meta", "note": "read two revisions of the spec",
     "headline": "Draconyx is the most intellectually serious ‘universal language’ attempt since Rust…",
     "quotes": [
         ("The language", "On paper it is one of the most coherent language visions in years, because it stacks "
                          "mechanisms that other languages bolt on outside the type system."),
         ("The language", "On paper it’s brilliant. It’s also honest in a way most vision docs aren’t, which is why "
                          "I take it seriously."),
         ("The future", "…as a research programme that could define the next generation of AI-native toolchains — "
                        "yes, it could be."),
         ("Versus Rust", "If your problem is ‘let an untrusted model write and continuously regenerate whole "
                         "services safely,’ Draconyx is better designed on paper."),
         ("Dependency injection", "…this is the best justification of DI in a language I’ve seen, because it isn’t "
                                  "framework DI."),
     ]},
    {"id": "qwen", "name": "Qwen", "maker": "Alibaba",
     "headline": "It is a masterpiece of language design on paper.",
     "quotes": [
         ("The language", "It reads like the language we should have designed if we started today with the "
                          "knowledge of Rust's pain points, JAX's elegance, and the reality of AI-assisted "
                          "development."),
         ("The language", "[Draconyx] is arguably the first language spec I’ve seen that treats the AI agent as a "
                          "first-class citizen of the toolchain."),
         ("The future", "The concepts are absolutely the future, even if this specific language doesn't achieve "
                        "total dominance."),
         ("Versus Rust", "On paper, yes, in several critical dimensions. In practice, Rust has a massive head "
                         "start."),
         ("Dependency injection", "Yes, emphatically, if it is done exactly as [Draconyx] specifies."),
     ]},
]

# The changelog: what changed in the language, its spec and its toolchain, newest first. Pre-release, so no versions:
# each entry is dated by the day the change landed on the main line of the language repository. Each change is
# (area, text, evidence): the evidence (commit hashes in the language repository) is not rendered; it is there so
# every line can be audited. Keep it that way: add a line only together with its evidence. Public wording only: no
# earlier working title, no internal card, decision or question numbers, no process.
CHANGELOG_URL = "/changelog/"
CHANGELOG_TITLE = "Draconyx changelog"
CHANGELOG_HEADLINE = "What changed"
CHANGELOG_LEDE = "Changes to the Draconyx language, its specification and its toolchain, newest first."
CHANGELOG_NOTE = (
    "Draconyx is pre-release, so there are no version numbers yet. Each entry is dated by the day its changes landed "
    "on the main line of the spec and the compiler. Commands carry today's name, `drx`, in every entry, including "
    "those before 18 October 2026, when the language took its name."
)
CHANGELOG = [
    {"date": "2026-11-02", "title": "User-built standard handles refused; secret values lose Show; consts copied", "items": [
        ("Safety", "The checker now refuses standard handles built by user code: a literal of a standard-library "
                   "`strict` type, such as `File(descriptor)`, `Task` or `Sender`, is `AX0241`, and writing a field "
                   "of `System` is `AX0242`. For now, a `std.kernel.launch` outside a `trust` block is the new "
                   "`AX0802`.",
                   "44850f86 45af468a 848dfae2"),
        ("Agent daemon", "The resume and package cards are now measured against their token budgets over their own "
                         "rendered text, not the JSON that carries them, and now return that text. A package card "
                         "over its budget is served whole and says so (`over_cap`).",
                         "5a18275f"),
        ("Safety", "The checker now denies `Show` and `Serializable` to any value that is or holds a `secret`, such "
                   "as a `List<secret Int>`, so interpolating one into a string is `AX0420`. A `strict` struct "
                   "holding a permission at any depth, as in an `Option<Network>` field, is now `AX0510`.",
                   "aa20abc6 95e7133f"),
        ("Ownership", "Every read of a heap `const` now yields a fresh copy, in `drx run` and in built binaries, so "
                      "changing a copy no longer changes the `const`, and each copy runs its destructor. Writing to "
                      "a `const`, or borrowing one exclusively, is the new `AX1024`.",
                      "0dcc55ce"),
        ("Types", "Capability arguments now count in more places: a type that includes or asserts `Conv<Int>`, or "
                  "an `any Conv<Int>`, no longer meets `Conv<Bool>`, at check time or in `when` dispatch. `x + "
                  "true` under `T: Add<Int>` is refused, and `when` arms differing only in `Item =` bindings no "
                  "longer clash.",
                  "7c04cfac d543f41d a1f50c1b 3ec17c0c 44290e89"),
        ("Services", "The checker now follows the services a function value needs through more routes: `with` and "
                     "`select` binders, fields that store it (also inside a `List` or `Option`), lambda parameters, "
                     "loops and `when`-dispatched returns. A missing provider (`AX0501`) or an exceeded `requires` "
                     "(`AX0502`) reached that way is now reported.",
                     "ee6d7646"),
        ("Concurrency", "A field write through a `MutexGuard` is now checked as a write to the value it protects, "
                        "so the spec's `Mutex` example checks; through a `ReadGuard`, writes and exclusive borrows "
                        "are refused. The spec's producer/consumer example now hands the producer its `Sender`, so "
                        "the channel closes.",
                        "6318a002 6c7b7912"),
        ("Formatter", "`drx fmt` now lays out `select`, `provide locally` and `syntax-parameterize` statements "
                      "instead of copying them verbatim, aligning `select` arms as it aligns `match` arms. Law "
                      "qualifiers not joined with `+`, as in `Add associative commutative`, are now the parse error "
                      "`AX0260`; before, only `drx fmt` rewrote them.",
                      "85b91fd8 d4a1d34d"),
    ]},
    {"date": "2026-11-01", "title": "Agent daemon re-reads the workspace; operators consume; values drop at block end", "items": [
        ("Agent daemon", "The agent daemon now re-reads the workspace before every request, so a write whose `base` "
                         "predates an edit made outside it is refused as a conflict. Its disk mirror is all or "
                         "nothing: files are staged first, and a failed rename restores those already replaced.",
                         "c53765b4"),
        ("Ownership", "The ownership checker now makes `+`, `-`, `*`, `/`, `++` and unary `-` consume heap-backed "
                      "operands, as the spec requires, so a later use is `AX0312`. A value still wanted is cloned "
                      "at the operator: `clone greeting ++ name`. Copy-class values such as `Int` are read as "
                      "before.",
                      "acf18cdd"),
        ("Ownership", "Owned values are now released at the end of the block that declares them, not of the "
                      "function, and temporaries at the end of their full expression, on every exit path. "
                      "Destructors that never ran now do: for `transfer` arguments, moved `match` payloads, "
                      "discarded temporaries and chains over 64 deep.",
                      "e2aecbe6 4cad4e03"),
        ("Testing", "`drx test` and `drx verify` now fail when an obligation could not be evaluated, unless "
                    "`--allow-unsupported` is passed; a law violation fails either way. `AX0707` is now titled "
                    "“coverage shortfall” and names its cause, such as a definition with no body, in the JSON "
                    "output.",
                    "21d082be"),
        ("Interpreter", "At run time, `==`, `compare`, `show` and capability operations now use the witness written "
                        "for the full type. With witnesses for `Box<Int>` and `Box<Bool>`, the interpreter and "
                        "native code used to run the first for every `Box`. A `when` arm's associated-type bindings "
                        "are now part of its test.",
                        "6c60f15b"),
        ("Types", "A written type with the wrong number of arguments, such as `Duo<Int>` for `struct Duo<A, B>`, is "
                  "now `AX0429`. An alias fills a left-out parameter from its default, as a struct does: with `type "
                  "Pair<A, B = A> = (A, B)`, `Pair<Int>` is `(Int, Int)`.",
                  "128f1395"),
        ("Diagnostics", "A dependency cycle (`AX0211`) is now reported at the `use` that enters it or the manifest "
                        "row that closes it, with the cycle printed; an import whose root is no module or declared "
                        "dependency (`AX0231`) names the `[dependencies]` row to add. A single fault in a core "
                        "construct, such as a chained comparison, gives one diagnostic.",
                        "c07338ea 6075459c 4d65c705"),
        ("Toolchain", "A redundant parenthesis no longer changes a definition's content hash; most existing hashes "
                      "changed once as a result. A member of a type-dispatched family is now addressed by its "
                      "canonical type (`@Loud`, not `@(Loud)`), so `drx fmt` no longer moves its address.",
                      "62225a84 e21a972a"),
    ]},
    {"date": "2026-10-30", "title": "Stricter type and borrow checks; two new diagnostic codes", "items": [
        ("Types", "A value lent at an exclusive `borrow` position now keeps its type arguments exactly: a "
                  "`Box<Cat>` can no longer be lent as `borrow Box<any Animal>`, which let a `Dog` be written in "
                  "and crashed `drx run`. The refusal is `AX1001` where the borrow is taken.",
                  "76f55ef9 e21a972a"),
        ("Types", "A bound now meets a requirement only when the capability arguments agree: `where T: Conv<Int>` "
                  "no longer satisfies `T: Conv<Bool>` (`AX0421`). Coherence is judged per instance: `Box: "
                  "Conv<Int>` and `Box: Conv<Float>` from two modules no longer clash, while two origins of one "
                  "instance are `AX0422`.",
                  "505ec66f 9061202a"),
        ("Types", "Two kinds of silently accepted code are now errors. Explicit type arguments at a call are "
                  "checked: `id<Int>(x = true)` is `AX1001`, too many arguments the new `AX0429`. A string pattern "
                  "with an interpolation, which could never match, is the new `AX0606`.",
                  "9c5b1945 5b9100ac"),
        ("Ownership", "The ownership checker now follows real control flow (`return`, `break`, `continue`, `elif`, "
                      "`let ... else`), so correct code it refused with `AX0301` or `AX0302` passes. It also keeps "
                      "the borrows a view or closure carries through copies and constructors; copying a view "
                      "holding an exclusive borrow is `AX0321`.",
                      "8a224b75 1ba7ae53"),
        ("Formatter", "Two things `drx fmt` drops no longer change a program's meaning. A redundant parenthesis no "
                      "longer affects the checkers or run-time behaviour (`parse(s)?` could trap where "
                      "`(parse(s))?` passed), and a `transfer` before a fresh temporary is typed, hashed and "
                      "ownership-checked as the temporary itself.",
                      "41dfb38a 01cdaa8c"),
        ("Syntax", "In a type, `transfer` is now accepted only in a function type's parameter list, as the grammar "
                   "says; elsewhere it is `AX0260`. `share remote` and `observe remote` are refused in every "
                   "position, `let` annotations and parameter qualifiers included (`AX0308`).",
                   "8e0ab049"),
        ("Standard library", "`Map`, `Set`, `OrdMap` and `OrdSet` now find, insert and remove keys through the key "
                             "type's own `eq` or `compare`, in both the interpreter and native code. A key type "
                             "with its own equality could hold two equal keys and miss a key just stored.",
                             "18a6cc15"),
        ("Diagnostics", "Three layout and lexical errors now give one diagnostic instead of a cascade: a body at "
                        "the continuation column is only `AX0114`, a stray character only the lexer's error, and "
                        "nesting too deep one `AX0270`. `AX0266` now reads “expected the def body as an indented "
                        "block”.",
                        "7d991874"),
    ]},
    {"date": "2026-10-29", "title": "Ten new diagnostic codes; formatter, ownership, layout and daemon fixes", "items": [
        ("Formatter", "`drx fmt` now keeps the parentheses that change what a call means, as in `(f)(y, x)` or `v "
                      "|> (adder(n = 1))`. Dropping them changed what the program computed. It also keeps the "
                      "parentheses an inline `if`, `match` or lambda needs, where it used to refuse the file.",
                      "0b45af02 a0dc4b05"),
        ("Ownership", "`let inner = frame.inner` over a copy-class struct, tuple or enum now binds a read-only "
                      "borrow, so a write through `inner` is `AX0304`. Borrowing a moved value is `AX0312`, a "
                      "`borrow T` call result passed bare as owned is `AX0321` unless `T` is copy-class, and a "
                      "record update may now read its base's fields.",
                      "5a050e92 b39556ab"),
        ("Types", "The refinement checker now instantiates a predicate by its syntax tree, not its text, closing "
                  "several false proofs. A capability bound is now met only by a conformance from a module the "
                  "caller reaches through `use`, and an alias or default that expands into itself is `AX0427`.",
                  "eff9a527 757af49e 79f109fa"),
        ("Syntax", "A capability operation is now a signature only: a body or `when` arms on one is `AX0292`, as "
                   "capabilities have no default operations. A `def` parameter without a type is now `AX0264`, and "
                   "an unknown or misplaced annotation, such as `@pined` for `@pinned`, is `AX0295`.",
                   "2ac64d5d 63316b5e 4e1f5ac8"),
        ("Syntax", "After a block opened in an inline form (`if c: while k < 3:`), the next line now stays outside "
                   "the `if`. A line at a `when` arm's or a lambda body's continuation column is now `AX0274` or "
                   "`AX0293`, not split off; a `when` arm's body placed at or left of its arm is `AX0294`.",
                   "9352948a 94e813a9 1bb84130 61fddbc9"),
        ("Syntax", "`-> :` now also opens a block body on a `match` or `select` arm, and on a lambda that is the "
                   "whole value of a `let`, assignment or `return`. `g<N + 1>(1)` now parses as a generic call, not "
                   "two comparisons, and a second `where` clause adds its bounds instead of silently replacing the "
                   "first.",
                   "8dbb8836 1bb84130 0ce36fc1 3286bf27"),
        ("Interpreter", "`when A == B ->` arms now parse, and the interpreter and native code test equality and "
                        "const `when` arms instead of treating them as `otherwise`. Property tests now draw `Bool` "
                        "inputs from `Bool`'s own generator; they were getting `Duration` values from `std.time`.",
                        "559ccc1c 89da35b3"),
        ("Agent daemon", "The agent daemon now loads `path` dependencies, so its diagnostics and write verdicts "
                         "match `drx check`; reads reach a dependency's exported definitions, and writes into one "
                         "are refused as `dependency-read-only`. A `put-def` fragment indented with non-ASCII "
                         "whitespace is now refused instead of crashing the daemon.",
                         "be5e53d8 d011c3b6"),
    ]},
    {"date": "2026-10-19", "title": "Descriptive names across the spec and the standard library", "items": [
        ("Standard library", "The standard library's parameter labels are now descriptive: 323 were renamed, such "
                             "as `trim(text =)`, `fold(items =, initial =, combine =)` and `checked_div(dividend =, "
                             "divisor =)`, along with some fields, such as `System.arguments` and "
                             "`Duration.nanoseconds`. Calls that need labels use the new names.",
                             "997e3101"),
        ("Spec", "The spec's code examples, laws, signatures and prose now use descriptive snake_case names instead "
                 "of single letters and cryptic abbreviations. Law variables take role names such as `left`, "
                 "`middle` and `right`; geometric `x`/`y` and `re`/`im` stay.",
                 "997e3101"),
    ]},
    {"date": "2026-10-18", "title": "The language takes the name Draconyx; the command is drx", "items": [
        ("Toolchain", "The language takes the name Draconyx, and the command becomes `drx` (`drx check`, `drx fmt`, "
                      "`drx serve`, `drx explain AXnnnn`). Manifests are `draconyx.toml`, lockfiles "
                      "`draconyx.lock`, and environment variables `DRACONYX_*`. Source files keep `.ax` and "
                      "diagnostics keep their `AXnnnn` codes.",
                      "f8283144"),
    ]},
    {"date": "2026-10-09", "title": "The formatter now checks that it can read back what it writes", "items": [
        ("Formatter", "`drx fmt` re-parses everything it writes and returns it only if it reads back as the same "
                      "tree. If it does not, nothing is written and `drx fmt` exits 1, and `put-def` answers with "
                      "the new error kind `formatter-defect`. The spec now states this rule.",
                      "4ddc271c"),
        ("Formatter", "`drx fmt` keeps more of the parentheses and labels that carry meaning: `for x in (borrow "
                      "xs):` and `(p).x` keep their parentheses, and the labels in `h ! transfer Moved(y = y, x = "
                      "x)` stay, where dropping them swapped the fields. `0 .. .n` is no longer written as the "
                      "unparsable `0...n`.",
                      "4ddc271c"),
    ]},
    {"date": "2026-10-08", "title": "Formatter keeps literals intact; doc comments found by tokens", "items": [
        ("Formatter", "`drx fmt` no longer changes what a string says. An interpolation hole that starts with `{`, "
                      "such as a map literal, is written `{ {\"k\": 1} }` instead of fusing into the escaped brace "
                      "`{{`, and a multi-line string's continuation lines are no longer re-indented.",
                      "0e8edb8d df0b79c7"),
        ("Agent daemon", "A line inside a multi-line string that begins with `//` is no longer taken for a doc "
                         "comment. The compiler, `drx fmt` and the agent daemon find comments from the lexer's "
                         "tokens, so `get-def` serves the whole string and editing the next definition no longer "
                         "cuts into it.",
                         "06823610"),
        ("Diagnostics", "In recovery from a malformed generic list, a bare `<` opens a bracket only after a type "
                        "name or where an argument begins, so `x < 8` no longer swallows the parameters after it. A "
                        "malformed generic parameter default is now one diagnostic, and later definitions are kept.",
                        "6b6943bb"),
    ]},
    {"date": "2026-10-06", "title": "Actor handler hashes, conformance instances in impact reports, parser recovery", "items": [
        ("Toolchain", "An actor handler's content hash now covers its body and the definitions it calls. Before, "
                      "every handler hashed as empty input, so an edit to a handler's body changed no hash.",
                      "15dee8b9"),
        ("Agent daemon", "Impact reports now tell conformances apart by their capability arguments. If `Box` goes "
                         "from `Conv<Int>` to `Conv<Float>`, the report shows one conformance revoked and one "
                         "created; before, it reported nothing. Slices also list each instance under "
                         "`conforms_instances` and `asserts_instances`.",
                         "94bd106c"),
        ("Formatter", "`drx fmt` now prints a cost tier after the whole extent: `Box<4..=32 @ Node>`, and `N + 1 @ "
                      "Node` without parentheses. Before, it wrote the unparsable `Box<(4..=32) @ Node>`, and every "
                      "definition after it was lost on the next parse.",
                      "15d4d6cb"),
        ("Diagnostics", "A malformed generic argument, such as `Box<(4..=N)>`, is now one diagnostic. The parser "
                        "picks up again at the list's closing `>`, so the items and definitions after it are no "
                        "longer lost.",
                        "51560e4b"),
    ]},
    {"date": "2026-10-05", "title": "Ownership checker port to Draconyx complete; positional patterns list every field", "items": [
        ("Self-hosting", "The ownership checker port to Draconyx is complete: it matches the reference ownership "
                         "checker on every move, loan, liveness decision and diagnostic, on all 1,004 test "
                         "packages, interpreted and compiled with `drx build`. It is the fifth compiler stage "
                         "written in Draconyx.",
                         "e3cc5118 96a99e9f 2db8126b cc7fd90c 91839a3d"),
        ("Types", "A positional constructor pattern must list every field, using `_` for any field it ignores. Too "
                  "few sub-patterns, or a bare constructor name whose constructor has a payload, is now `AX1003`; "
                  "before, the missing fields were silently read as `_`. A labelled pattern may still leave fields "
                  "out.",
                  "7a3d916b"),
        ("Types", "A named type now keeps its `;` segments, so `Grid<1;2>` and `Grid<1, 2>` give a definition "
                  "different content hashes; before, the checker flattened them into one. No typing rule reads the "
                  "segments, so the checker still accepts `Grid<1, 2>` where `Grid<1;2>` is expected.",
                  "c6413dcb"),
        ("Interpreter", "A `when T: Conv<Int>` dispatch arm now asks its question with the capability's arguments. "
                        "Before, the first answer for a type and a capability was reused whatever the arguments, so "
                        "call order could pick the wrong arm, in the interpreter and in native code.",
                        "0c31f3b3"),
        ("Toolchain", "Changing the spacing of a refinement predicate or a const argument (`n>0` against `n > 0`, "
                      "`N+1` against `N + 1`) no longer changes a definition's content hash. The checker now spells "
                      "these from the parsed tree, not from the source text.",
                      "6f926b64"),
    ]},
    {"date": "2026-10-04", "title": "Content hashes cover meaning; new AX0278 for const expressions", "items": [
        ("Toolchain", "A definition's content hash now covers a `when` arm by its condition and body, so most "
                      "reformatting of the arm no longer moves it. It also covers what it used to drop: "
                      "`where`-bound capability arguments, explicit type arguments, types written as values, "
                      "brace-literal contents and `comptime` code.",
                      "633e3aea 33369933 69693337"),
        ("Agent daemon", "Writing back the canonical text that `get-def` served no longer shows up in `put-def`'s "
                         "impact report as `signature-changed`. The report now compares canonical spellings and the "
                         "typed signature, so only a real change counts.",
                         "633e3aea"),
        ("Formatter", "`drx fmt` keeps the parentheses in `(secret Int) -> Int`. It used to drop them, so the "
                      "result read as `secret (Int -> Int)`. A `when` arm body with no one-line form is now written "
                      "as a `-> :` block.",
                      "633e3aea"),
        ("Syntax", "In a capability, a dispatch arm names one definition (`when borrow -> name`). An `otherwise`, a "
                   "constraint or any other body there is now refused with `AX0267`; before, such an arm passed the "
                   "check.",
                   "47aa0e05"),
        ("Syntax", "A stray closing bracket after a dispatch arm no longer hangs `drx check` and `drx fmt`. An arm "
                   "body continued on a deeper line no longer ends the definition early, which made the next arm an "
                   "error.",
                   "47aa0e05"),
        ("Diagnostics", "Both sides of a `where` const proposition are now read as const expressions, so `where 2 "
                        "<= N` and `where (N + 1) >= 2` are checked instead of crashing the compiler. An operator a "
                        "const expression does not admit (`%`, bitwise operators, shifts, a call, a literal-zero "
                        "divisor) is the new `AX0278`.",
                        "fe67d31f"),
    ]},
    {"date": "2026-10-03", "title": "Named arguments enforced; the ownership checker port begins", "items": [
        ("Syntax", "Named arguments are now enforced: at a call of two or more arguments to a function, an "
                   "operation, an `extern` or a constructor with named fields, an unlabelled argument is `AX0256` "
                   "unless it is a name equal to the label, bare or module-qualified, as in `feed(animal, amount = "
                   "3)`.",
                   "50c3e09c 9ceaf806"),
        ("Formatter", "`drx fmt` drops a label its argument repeats: `animal = animal` becomes `animal`, and `cx = "
                      "borrow cx` becomes `borrow cx`. The content hash does not move. On the self-hosted packages "
                      "it removed 14,388 labels.",
                      "50c3e09c"),
        ("Types", "In a single-argument call, a name now selects the overload that declares it as a label; `g(b)` "
                  "over `g(b: Int)` and `g(c: Int)` used to be an ambiguity error. A label written at a call "
                  "through a function value is `AX0257`; such calls bind by position.",
                  "9ceaf806"),
        ("Self-hosting", "The ownership checker is now being ported to Draconyx. Its first three milestones, "
                         "covering its inputs, the type model and liveness, agree with the reference ownership "
                         "checker on all 928 test packages; the port is 1,725 lines of code so far.",
                         "9ceaf806 67bfee3e"),
        ("Syntax", "A `when` dispatch arm's body may now be any single statement, such as `-> return show(x)`, or a "
                   "colon-opened block. `drx fmt` now prints a block body as `head -> :` with the block beneath; it "
                   "used to drop the colon, leaving code that no longer parsed.",
                   "67bfee3e"),
    ]},
    {"date": "2026-09-30", "title": "Glob imports, or-patterns, look-only pipelines and filled bracket lists", "items": [
        ("Syntax", "`use m.*` imports a module's surface bare, ranked below locals, declarations and explicit "
                   "imports and above the prelude. Two globs bringing different items of one name are `AX0253` only "
                   "where the name is used; globbing a non-module is `AX0254`. There is no grouped `use m.{a, b}` "
                   "form.",
                   "e0556495"),
        ("Syntax", "Or-patterns `p1 | p2` work wherever a pattern does, defined by expansion, so evaluation order, "
                   "guards, exhaustiveness and redundancy follow. Alternatives must bind the same names (`AX0255`) "
                   "with the same types (`AX0605`). The checkers, the formatter, the interpreter and native code "
                   "support them.",
                   "e0556495"),
        ("Standard library", "Every `Iterator` is now `Iterable`, existentials included, so look-only pipelines "
                             "such as `sensors |> iter_ref |> fold(...)` check and run, and the list stays usable "
                             "afterwards. `position`, `contains` on a `List` and `join` are added.",
                             "e0556495"),
        ("Formatter", "`drx fmt` now fills a bracketed list that does not fit in 80 columns: items run left to "
                      "right and wrap at the alignment column, instead of one item per line. Formatting already "
                      "formatted code changes nothing.",
                      "e0556495"),
        ("Self-hosting", "The Draconyx lexer, parser, resolver and type checker adopted the filled layout and glob "
                         "imports: their code shrank from 51,598 to 37,166 lines, blank lines and comments not "
                         "counted, with every name resolving to the same item before and after.",
                         "e0556495"),
    ]},
    {"date": "2026-09-29", "title": "Type checker fixes: patterns, dispatch, services, variance and content hashes", "items": [
        ("Types", "Literal patterns are compared by value, so `0x10` after `16` is a redundant arm (`AX0602`). "
                  "Exhaustiveness checking has no depth cap: a match on a very wide tuple now reports exactly the "
                  "missing case instead of calling every arm redundant.",
                  "338963f1"),
        ("Types", "A refutable pattern where an irrefutable one is required, in a `let` without `else`, a `for` "
                  "binder, a parameter or a lambda head, is now error `AX0601`. The help suggests `let ... else` at "
                  "a `let` and a `match` elsewhere. It used to be accepted silently.",
                  "338963f1"),
        ("Types", "A `when` arm that can never be selected is now error `AX0604`: one after `otherwise`, or after "
                  "an arm that matches every type it matches and requires nothing it does not already guarantee, "
                  "together with the declared bound. The spec now defines when one arm implies another.",
                  "338963f1"),
        ("Services", "A function value's service requirements now travel with its type. Calling a closure returned "
                     "from a function, or taken from a list or an `Option`, charges its services, as does a call "
                     "through a capability bound, so a missing provider is reported as `AX0501`.",
                     "338963f1"),
        ("Agent daemon", "When two functions share a name and labels but differ in the type of their first "
                         "parameter, each now has its own address, such as `m.ping@Loud`, which the agent daemon "
                         "accepts, so one member's service requirements no longer overwrite the other's.",
                         "338963f1"),
        ("Types", "Variance is computed to a fixpoint with no pass cap, so it no longer depends on declaration "
                  "order, and a parameter nested 26 levels deep, past the old limit of 24, is now seen. A `borrow "
                  "T` field is invariant in `T`; `share` and `observe` fields are covariant.",
                  "338963f1"),
        ("Types", "Definite assignment no longer reports `AX1019` at a read that cannot be reached, such as code "
                  "after a `loop` with no `break`.",
                  "338963f1"),
        ("Toolchain", "The content hash now covers a `let ... else` block, default argument values, const "
                      "constraints and a parameter pattern's constructor. The spec names two hashes, a definition's "
                      "own and its closure over everything it calls, and both type checkers compute both.",
                      "338963f1"),
    ]},
    {"date": "2026-09-27", "title": "The type checker written in Draconyx; partial moves; edits with consequences", "items": [
        ("Self-hosting", "The type checker is now also written in Draconyx. It agrees with the reference type "
                         "checker on all 751 test packages, including all 5,228 definition hashes, and on the "
                         "Draconyx lexer, parser, resolver and its own source.",
                         "dd762e59 267a8415 34c0d926 347ed42a 93faa018"),
        ("Ownership", "Projecting a field out of a temporary is a read; where an owned copy of a non-copy field is "
                      "needed it is `AX0321`, repaired with `clone`. Moving a field out with `transfer x.f` is a "
                      "partial move, refused as the new `AX0313` when the type of `x` declares a destructor.",
                      "655724b1 f82ba5c6"),
        ("Ownership", "`observe` handles are now weak in the interpreter and native code: `upgrade` returns `None` "
                      "once the last `share` handle is gone. That makes the spec's way out of the reference-cycle "
                      "leak work, since an unreachable `share` cycle is not reclaimed in this edition.",
                      "655724b1 f82ba5c6 2e433c7a"),
        ("Diagnostics", "Suggested edits on the JSON channel now carry `also`, further spans applied all or "
                        "nothing, and `consequence`, what the edit makes true. `AX0312` uses both: when the callee "
                        "is in the workspace it offers one edit at the call and the parameter, plus a `clone` "
                        "repair.",
                        "23c23f10 6773b7a2 93faa018"),
        ("Agent daemon", "`drx outline` and the agent daemon's outline now print an `evidence` line: the `trust` "
                         "blocks a definition contains, the foreign libraries it calls directly with their modes, "
                         "or `unimplemented` for a `todo()` body. The line is omitted when empty.",
                         "23c23f10 6773b7a2"),
        ("Formatter", "`drx fmt` now also drops a redundant `transfer` before an operator result, as it already did "
                      "before call results and literals: `f(transfer (a + b))` becomes `f(a + b)`.",
                      "23c23f10 6773b7a2"),
        ("Standard library", "The spec's `dropout` now takes a `Key`, as `dropout(key, x, rate)`, so its mask is "
                             "drawn from an explicit key like every other random draw.",
                             "655724b1 f82ba5c6"),
    ]},
    {"date": "2026-09-23", "title": "Destructors run, let ... else arrives, drx explain covers every code", "items": [
        ("Spec", "After an outside review, the spec names the five layers of a definition: address, contract, "
                 "reach, evidence and body. It also specifies, though none is built yet, `drx audit tcb`, which "
                 "lists everything a build's guarantees rest on, and the agent daemon queries `what-rests-on` and "
                 "`same-computation`.",
                 "ce3f6360 ac57263f c61682b3"),
        ("Toolchain", "`drx explain AXnnnn` is new and answers for every code the toolchain can emit, 121 of them, "
                      "and a test keeps it complete. `drx run` and built binaries exit 0 for `Ok`, 1 for `Err`, 2 "
                      "for a trap and 3 for a failure to start, front-end errors included.",
                      "2e433c7a ac57263f 36721b9e c61682b3"),
        ("Native code", "A native binary now carries a serialised program image and no source, so it starts without "
                        "running the front end. Calls through function values and lambda bodies are compiled, and "
                        "compiled code enforces the interpreter's step limit.",
                        "36721b9e ac57263f c61682b3"),
        ("Ownership", "Destructors now run, in the interpreter and in native code: at the end of the owning frame "
                      "in reverse declaration order, on reassignment, and for a container's elements in index "
                      "order. A temporary whose field is projected out is dropped, destructor included, at the end "
                      "of its full expression.",
                      "ac57263f 2e433c7a c61682b3"),
        ("Syntax", "`let Some(text) = setting else:` binds a refutable pattern; the `else` block must diverge and "
                   "sees none of the pattern's names. The parser, the checkers, the formatter, the interpreter and "
                   "native code support it. A match arm that fails part-way now binds nothing.",
                   "2e433c7a ac57263f c61682b3"),
        ("Safety", "`secret` now has the same barrier as `tainted`: a `secret` value in an unmarked position, such "
                   "as an argument, field, return or collection element, is compile error `AX1023`. The repairs are "
                   "marking the position `secret` or `declassify` with a stated rationale.",
                   "36721b9e c61682b3"),
        ("Types", "A conformance not decided within the fixed depth of 12 steps is error `AX0425`, never an "
                  "acceptance; an `asserts` clause can no longer supply the conformance it presupposes (`AX0423`). "
                  "A nested named-tuple projection like `t.b.c`, which used to trap at run time, now works.",
                  "36721b9e ac57263f c61682b3"),
        ("Standard library", "New: `push_into` for appending to a map of lists, `int_of_text` for integers in radix "
                             "2 to 36, checked subtraction on `Byte`, and ordering on tuples of ordered values. An "
                             "inclusive range ending at the largest `Int` now traps on overflow instead of silently "
                             "skipping its last element.",
                             "36721b9e ac57263f c61682b3"),
    ]},
    {"date": "2026-09-20", "title": "Native executables with drx build; the resolver written in Draconyx", "items": [
        ("Native code", "`drx build` now produces a linked native executable. Across 82 test programs, including "
                        "the Draconyx lexer, parser and resolver, it matches the interpreter byte for byte on "
                        "output and exit code. Constructs it does not compile yet are named at build time, `AX1101` "
                        "to `AX1104`.",
                        "6063bf3c"),
        ("Self-hosting", "The resolver is now also written in Draconyx: 14,492 lines in nineteen modules, with no "
                         "`trust` blocks. It agrees with the reference resolver on all 608 test packages, and "
                         "resolves the Draconyx parser and its own source exactly as the reference does.",
                         "d026f10e"),
        ("Standard library", "New `OrdMap` and `OrdSet` keep their keys in order. `sort` is now guaranteed stable, "
                             "and the new `sort_by` and `sort_by_key` are stable too; checked laws state the "
                             "stability of both and their agreement with `sort`.",
                             "6063bf3c"),
        ("Standard library", "The prelude gains ASCII character predicates, such as `is_digit` and `is_alpha`, for "
                             "both `Char` and `Byte`. `FileSystem.list` now returns each entry's name and kind, and "
                             "`FileSystem` gains `exists` and `canonicalize`, which returns a path relative to its "
                             "authority's root and refuses one outside it.",
                             "6063bf3c"),
        ("Toolchain", "A package may not declare a top-level module named `std` (`AX0252`). A dependency can now "
                      "import only its own modules, `std` and the packages its own manifest declares, never its "
                      "dependencies' dependencies; any other root is `AX0231`.",
                      "6063bf3c"),
        ("Types", "A tensor type without axes, such as `Tensor<F32>`, now unifies with every axis-named tensor of "
                  "its dtype, so the standard library's tensor functions accept shaped tensors but do not yet catch "
                  "shape errors. Two shaped tensors unify only when axis names, order and sizes agree.",
                  "6063bf3c"),
        ("Laws", "The spec now states that laws, like witness examples, are hermetic: they are handed no `System`, "
                 "so a law cannot read a file, open a socket or consult a clock, and its verdict cannot depend on "
                 "the world.",
                 "6063bf3c"),
        ("Ownership", "The spec now says a parameter's ownership mode, the unmarked read-only borrow included, is "
                      "part of the published signature, and that shared mutable state such as an interner is "
                      "threaded as a `borrow` parameter rather than kept in a field.",
                      "6063bf3c"),
    ]},
    {"date": "2026-09-16", "title": "Taint barrier enforced, faster checking, module cycles allowed, path dependencies", "items": [
        ("Safety", "The type checker now enforces the taint barrier: a `tainted T` where an unmarked `T` is "
                   "expected (argument, field, return, annotated `let`, `provide`, collection element) is `AX1022`, "
                   "and the error names both repairs. `Network.read` now returns `tainted Bytes`.",
                   "90fc928b"),
        ("Laws", "A law's free variables must have types the checker can infer, or the law is `AX0712` at check "
                 "time instead of failing mid-test. Variables can be annotated: `law name(a: Int) checked:`.",
                 "90fc928b"),
        ("Toolchain", "Modules in one package may `use` each other in a cycle; a cycle across packages is `AX0211`. "
                      "A path dependency is a separate package with its own manifest and namespace, imported as "
                      "`use dep.module.item`.",
                      "90fc928b"),
        ("Ownership", "The spec now states that a temporary needs no verb in a consuming position: "
                      "`f(make_engine())`; a written `transfer` stays legal and `drx fmt` removes it. Inside "
                      "`<...>`, `borrow T`, `share T` and `observe T` are types that survive instantiation; "
                      "`transfer` there is `AX0260`.",
                      "90fc928b"),
        ("Ownership", "A `match` binding now borrows read-only unless its arm writes through it, so reading the "
                      "matched value's siblings inside the arm no longer raises a false conflict.",
                      "90fc928b"),
        ("Syntax", "A `let` without an initialiser must be exactly `let x: T`: leaving out the type, or "
                   "destructuring, is refused at the declaration, and reads are checked by definite assignment. The "
                   "spec now states there is no `Enum.Variant` form: clashing constructor families go in separate "
                   "modules.",
                   "90fc928b"),
        ("Syntax", "Seven short malformed inputs that sent the parser into an endless loop now end with a "
                   "diagnostic, and the spec requires the parser to always terminate. The nesting limit of 96 is "
                   "normative (`AX0270`), and `(x,)` is now `AX0273`.",
                   "90fc928b"),
        ("Toolchain", "`drx check` on the self-hosted parser package fell from more than nine minutes to under "
                      "three seconds. Whether a type is a view is now computed once per program instead of "
                      "re-derived at every call site; the language is unchanged.",
                      "90fc928b"),
    ]},
    {"date": "2026-09-07", "title": "Char literals, views, integer overflow, named tuples; the parser in Draconyx", "items": [
        ("Ownership", "A `for` operand is spelled like an argument: unmarked borrows each element, `transfer` "
                      "consumes. A `borrow` argument no longer blocks later arguments from reading the same value. "
                      "Newly refused: moving a value a `provide` still serves, and binding or returning a view of a "
                      "temporary (`AX0310`).",
                      "fccf672f 1df1922b"),
        ("Syntax", "`'x'` is a `Char` literal; `''` is `AX0110`, and `'\\''` is the apostrophe. New lexical errors: "
                   "a stray carriage return (`AX0111`), a letter glued to a number such as `1u8` (`AX0112`), a "
                   "bracket still open at end of file (`AX0113`), a block at a continuation column (`AX0114`).",
                   "fccf672f 1df1922b"),
        ("Types", "The spec now pins down `Int` arithmetic, which the interpreter already followed: `+`, `-` and "
                  "`*` panic on overflow, with `wrapping_*` and `checked_*` alternatives; `/` and `%` truncate "
                  "toward zero; `a == (a / b) * b + a % b` is a checked law.",
                  "1df1922b"),
        ("Types", "Named tuples work end to end: `(mean = m, sd = s)` literals, by-name patterns in any order, and "
                  "`.mean` access; mixing named and positional components is `AX0273`. Tuples of `Arbitrary` types "
                  "are `Arbitrary`, so a law can range over pairs.",
                  "1df1922b fccf672f"),
        ("Standard library", "The library gains read-only borrowed views over a new `Sequence` capability: "
                             "`View<S>`, `BytesView` and `Str`. Also new: `sum`, byte and character conversions, "
                             "`push_byte` and `Console.write`. A qualified `std` name the library does not declare "
                             "is now an error at check time.",
                             "fccf672f 1df1922b"),
        ("Interpreter", "`drx run` passes the arguments after `--` to `main` as `System.args` and reaches real "
                        "files through `FileSystem`, which `drx test` and `drx verify` refuse. Console input and "
                        "arguments are now typed `tainted String`, not yet enforced by the checker. A tail call "
                        "across a `provide` runs in constant stack.",
                        "fccf672f 1df1922b"),
        ("Formatter", "The canonical form now has a normative width of 80 columns. An `and`/`or` chain that does "
                      "not fit breaks before every operator, and over-long `if`, `while`, `match` and `for` heads "
                      "now wrap as well.",
                      "fccf672f"),
        ("Self-hosting", "The parser is now also written in Draconyx: 9,765 lines, using the Draconyx lexer as a "
                         "dependency. It builds the same tree as the reference parser, node for node, on all 1,018 "
                         "test inputs and on its own source.",
                         "1df1922b"),
    ]},
    {"date": "2026-09-06", "title": "Spec split into 31 sections; the first compiler; the lexer in Draconyx", "items": [
        ("Spec", "The specification is split into 31 sections and grows from 302 to 432 pages. New: GPU kernels, "
                 "with `std.kernel` and a FlashAttention example; `std.ai`, where model access is a permission "
                 "derived from `Network`; pass-rate laws; witness `example` clauses; and editions, which freeze "
                 "grammar, keywords and diagnostic codes together.",
                 "5b3c9fa6 045f2aa3"),
        ("Safety", "The spec now specifies `tainted`: model completions, console input and network reads are born "
                   "tainted at their library signatures, a tainted value may not fill a prompt's instruction slot, "
                   "and `endorse` with a written rationale is the only way out.",
                   "5b3c9fa6"),
        ("Ownership", "Function types spell ownership as a `def` does: `(T) -> U` borrows read-only, `(transfer T) "
                      "-> U` consumes and `(borrow T) -> U` borrows exclusively. The spec also says operators "
                      "consume heap-backed operands, as their capability operations do, so `clone a + b` keeps `a`.",
                      "5b3c9fa6"),
        ("Toolchain", "The first compiler lands, written in Rust: lexer, parser, resolver, type and ownership "
                      "checkers, interpreter, canonical formatter, and a standard library generated from the spec. "
                      "Diagnostics carry `AX` codes and spans, as text or JSON. Its commands include `check`, "
                      "`fmt`, `outline`, `get-def`, `test`, `verify` and `run`.",
                      "5b3c9fa6 045f2aa3"),
        ("Services", "The type checker works out which services each function reaches through its callees: one that "
                     "no enclosing `provide` supplies is `AX0501`, naming the call chain, and `drx outline` prints "
                     "each definition's uses and needs. A missing `match` case is `AX0601`; a redundant arm, "
                     "`AX0602`.",
                     "5b3c9fa6"),
        ("Agent daemon", "`drx serve` starts the agent daemon: JSON-RPC 2.0, one request per line, with 20 methods, "
                         "among them `outline`, `get-def`, `slice`, `search`, `put-def`, `fork`, `what-breaks-if`, "
                         "`delta-card` and `resume-card`. `drx rpc` makes a single call.",
                         "5b3c9fa6"),
        ("Testing", "`drx test` runs every obligation a package owes: checked laws as property tests from a fixed "
                    "seed, with failures shrunk and replayed first next time, conditional and statistical laws, "
                    "witness examples and `_test` modules. A `todo()` body gets `UNIMPLEMENTED`, not a failure.",
                    "5b3c9fa6"),
        ("Self-hosting", "Self-hosting begins: the lexer is rewritten in Draconyx, 2,148 lines with no `trust` "
                         "blocks, running on the interpreter. It produces the same tokens as the reference lexer in "
                         "Rust, byte for byte, on all 678 test inputs, its own source included.",
                         "045f2aa3"),
    ]},
    {"date": "2026-07-21", "title": "The Iteration Budget section; spec examples brought in line with the grammar", "items": [
        ("Spec", "The spec gains a section, The Iteration Budget, that charges each check to one of three loops: "
                 "edit (type, ownership and safety checks), test (laws) or ship (SMT proofs, optimisation). An "
                 "answer not yet recomputed is reported as pending, never served stale.",
                 "ef8cfc4c"),
        ("Spec", "The spec's illustrative fragments now obey its own grammar: match arms and tooling-directive "
                 "strings were respelled, and `syntax-parameterize` gained the production its comment promised, "
                 "making 102 contextual keywords.",
                 "39ead6e6 7ceedef3 64562635"),
        ("Ownership", "The spec's mirror rule now covers an assignment's right-hand side as well as a `let`'s: a "
                      "bare place there binds a read-only borrow, so handing an owned value on is spelled "
                      "`transfer`.",
                      "64562635"),
    ]},
    {"date": "2026-07-20", "title": "First commit: a 280-page specification; field defaults and keyword classes", "items": [
        ("Spec", "First commit: a 280-page specification, a draft chapter on the agent interface, and two example "
                 "packages: an online shop and the event-sourcing language extension it is written in.",
                 "9af22e96"),
        ("Ownership", "Ownership is spelled with the same verb at the call and in the signature: `transfer`, "
                      "`borrow`, `share` or `observe`. An unmarked parameter is a read-only borrow; returns, fields "
                      "and locals are owned.",
                      "9af22e96"),
        ("Syntax", "Modules are the only namespace: there are no methods, and the dot never calls anything. There "
                   "is no `pub`: functions are visible across their package, `export` lines declare what other "
                   "packages may call, and functions overload by name plus label set.",
                   "9af22e96"),
        ("Types", "The spec now gives struct fields defaults, evaluated afresh at each construction that omits "
                  "them, so `seen: List<Int> = empty()` gives every value its own list. A default may not read a "
                  "sibling field; adding a defaulted field is a minor version bump.",
                  "76885b0d"),
        ("Safety", "The spec now lets a module's `_test` companion construct its `strict` types, in test builds "
                   "only. Deserialising, `Arbitrary` and other generated construction of a `strict` struct must be "
                   "written in its module, through its validating constructor. A permission holding another "
                   "permission is a compile error.",
                   "76885b0d"),
        ("Types", "Purity is inferred, not declared: a refinement predicate may call only functions the compiler "
                  "infers pure, by the same judgement `comptime` bodies use, and `trust pure` vouches for the "
                  "deterministic intrinsics at the bottom of the library.",
                  "76885b0d"),
        ("Syntax", "Every keyword is now classified: 32 reserved words that can never be identifiers, and 101 "
                   "contextual keywords that are keywords only where the grammar quotes them. A new appendix lists "
                   "each keyword with a one-line account of what it does.",
                   "60ec9bff 2a3e9111"),
        ("Laws", "Laws are implicitly quantified over their free variables, with no quantifier syntax, and a law "
                 "may now stand alone at module level as well as inside a capability or `extend` block.",
                 "29a4f464"),
    ]},
]

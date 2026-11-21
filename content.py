"""Site content for draconyx.ai: the single source for index.html, index.md, llms.txt, the opinions page, the
changelog page and the words around the blog's posts (the posts themselves are in posts/).

Reasons 1-8 were fact-checked against the spec and the compiler on 2026-10-18 (adversarial
verifier per reason, code samples run through the compiler); reason 9 (context) and the name section were
checked by the site review the same day. On 2026-11-02 every reason, feature, number and spec citation was
re-checked against main of the language repository (fb4f8937), and the code samples were re-run through a
compiler built from it. On 2026-11-16 all of it was re-checked against main 05e74e38d1 (15 Nov). Since then the
code samples are written in the syntax the language's owner ruled, even where that compiler does not accept it
yet; a caption says "Checked with the compiler" only where a run on main accepted the sample as shown. On
2026-11-20 every Draconyx sample moved to `//` comments and `@doc` docs above what they document, each function's
doc listing every parameter; main's compiler accepts neither yet, so no Draconyx sample carries that caption. Status
pills follow the work: Ships when it is built or being tested, Partly built when started, In the spec when not.
Keep it that way: change a claim only together with its citation.
"""

AS_OF = "15 November 2026"
# No page prints the contact address, where harvesters would collect it: the links go to /contact, which Caddy
# redirects to a mailto: (README, "Contact"). CONTACT_LINK is the phrase linked to it, in INVOLVED and PRIVACY.
CONTACT_URL = "https://draconyx.ai/contact"
CONTACT_LINK = "email us"
# Set to the listmonk list UUID once the public "Draconyx updates" list exists; None keeps the form disabled.
LISTMONK_LIST_UUID = "240235c8-27a5-472b-b775-904925a1ceb6"
LISTMONK_FORM_URL = "https://lists.draconyx.ai/subscription/form"
# The form's bot check (README, "Signup form"): the ALTCHA widget fetches a proof-of-work challenge that listmonk
# issues, from this path on the site itself (Caddy passes it to listmonk), and puts the solution in the form.
ALTCHA_CHALLENGE_URL = "/altcha-challenge"
SPEC_PDF = None  # "/draconyx-spec.pdf" once the renamed spec is published

HERO = {
    "eyebrow": "The programming language for AI authors",
    "headline": "Built for the machines that write your code.",
    # The page's <h1>: the headline with the name in front, so the main heading says what the site is. The headline
    # alone stays in the link previews, the share image and the Markdown copy.
    "h1": "Draconyx: the programming language built for the machines that write your code.",
    "subhead": (
        "Python, Rust and Go were designed for a human at a keyboard. Draconyx was designed for the "
        "model in the loop: errors that come back as data, edits addressed by name and checked before they land, "
        "laws that are checked, not trusted, and every service a function uses printed in its outline."
    ),
}

PROBLEM = [
    "Models now write code by the million lines, and they don't work like people. In the spec's words, a "
    "language model does not read documentation and then write correct code: it generates, observes and "
    "repairs, hundreds of times, unattended.",
    "Python, Rust and Go hand that agent error text or half-structured JSON, make it patch files "
    "by string match, route it through tooling built around an editor cursor, and run its code where any import "
    "can open a socket. Every fix for that lives outside the language: a flag, a server, a sandbox. In Draconyx, "
    "the agent's interface is in the spec.",
    "Draconyx flips it. What the AI author needs is the language: \u201cnot leniency but a fast, precise, "
    "machine-readable verdict.\u201d The compiler never calls a model, and its agent daemon is a "
    "deterministic oracle: same tree, same answer, every time.",
]
PROBLEM_CITES = ["01-vision:71", "01-vision:79", "26-agent-interface:92-141"]

# Each reason: title, body paragraphs, unlike, sample (kind, text, caption), cites, status tag.
REASONS = [
    {
        "id": "diagnostics",
        "state": "ships",
        "title": "Errors are data. Not prose.",
        "body": [
            "Every checker emits one Diagnostic value: a stable AXnnnn code, byte-precise spans, an "
            "explanation, and suggested edits. Each edit carries an applicability (`always` or `maybe`), can carry "
            "`also` spans that apply all-or-nothing across files, and, where the checker knows it, a `consequence`: "
            "the fact about the program that the edit makes true.",
            "When a name, a label or a field doesn't resolve, the spec's “hallucination contract” requires ranked candidates "
            "to come back as `maybe` edits. A model repairs from data instead of parsing prose. "
            "`drx explain` answers for every code the toolchain can emit, and a test enforces it.",
        ],
        "ships": "Ships today: the JSON channel, the ownership checker's two-file edits with consequences, ranked candidates "
                 "(by fit at the use site, then edit distance, then import cost) for unknown names, labels and fields, "
                 "explain for all 262 catalogued codes.",
        "unlike": "rustc's JSON has applicability but no per-edit consequence, and many diagnostics have no "
                  "code. CPython's “Did you mean” is prose. Go's compiler errors carry neither codes nor edits; fixes "
                  "come from gopls.",
        "sample": ("json", """$ drx check pkg --json
{"code": "AX0234", "severity": "error",
 "message": "unresolved name `add_amount`",
 "primary_span": {"file": "src/money.ax", "start": [9,5], "end": [9,15],
                  "bytes": [192,202]},
 "secondary_spans": [],
 "explanation": "a name resolves lexically: enclosing bindings, ...",
 "suggested_edits": [{"span": {..., "bytes": [192,202]},
   "replacement": "add_amounts", "applicability": "maybe",
   "description": "replace `add_amount` with `add_amounts`",
   "consequence": "`add_amounts` names the def `pkg.money.add_amounts`"}],
 "help": ["did you mean `add_amounts`?"]}""",
                   "Real compiler output, trimmed."),
        "cites": ["25-tooling:8-45", "25-tooling:84-123", "25-tooling:188-210", "26-agent-interface:620-645"],
    },
    {
        "id": "edit-by-name",
        "state": "ships",
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
        "ships": "Ships today in `drx serve` and `drx rpc`. The daemon re-reads the workspace before every write, "
                 "so a write whose `base` predates an edit made outside it is refused, and it stages every changed "
                 "file before replacing any. A write adds the plain `use` line a new name needs in the same "
                 "transaction, and nested members (variants, operations, laws) are spliced canonically by name.",
        "unlike": "Python, Rust and Go define no such write interface. Agents patch text by string "
                  "match, diff hunks or range-keyed LSP edits. Codemod tools (LibCST, rust-analyzer "
                  "SSR) are add-ons with no tree-hash precondition, no type check before the bytes land and no "
                  "impact report.",
        "sample": ("shell", """$ drx rpc . put-def '{"address": "inventory.reprice",
    "base": "deadbeef", "text": "@doc \\"\\"\\"...\\"\\"\\"\\nreprice(...) -> Int: ..."}'

# the workspace moved since `base`: refused, with the current text
{"code": -32000, "message": "the workspace has moved since `base`",
 "data": {"kind": "conflict", "detail": {"base": "deadbeef",
   "current_tree": "def6ed83...", "addresses": ["inventory.reprice"],
   "current": [{"address": "shop.inventory.reprice",
     "text": "@doc \\"\\"\\"\\nRaises `price` by `pct` percent.\\n\\n  * price - the price to raise\\n  * pct - the percentage to raise it by\\n\\"\\"\\"\\nreprice(price: Int, pct: Int) -> Int:\\n    price + price * pct / 100\\n"}]}}}

# a write that fails the check: same shape as success, nothing written
{"tree": "def6ed83...", "applied": false, "new_errors": 1,
 "diagnostics": [{"code": "AX1001",
   "message": "type mismatch: expected `Int`, found `String`"}],
 "impact": {"broken_consumers": [{"address": "shop.inventory.reprice",
   "codes": ["AX1001"]}]}}""", "Daemon replies, abridged (hashes trimmed, fields elided; the definition's text shown in the current doc syntax)."),
        "cites": ["26-agent-interface:95-99", "26-agent-interface:188-196", "26-agent-interface:669-776", "32-agent-conformance:1106-1131", "25-tooling:881"],
    },
    {
        "id": "authority",
        "state": "ships",
        "title": "No global open(). Every service on the record.",
        "body": [
            "The rule is “no ambient permission”: there is no global `open` and no standard function that "
            "reaches the world on its own authority. Every permission descends from the `System` powerbox handed "
            "to `main`, and code holds one only when it is handed one.",
            "The compiler works out which services each definition reaches, through callees and function "
            "values. A service reached with no provider is compile error AX0501, naming the whole call chain, and "
            "`drx outline` prints each definition's uses and needs. A host can hand an AI-written plan a narrowed "
            "permission, such as a filesystem that `scope_to` confines to one directory, and read from the outline "
            "exactly which services the plan reaches.",
        ],
        "ships": "Ships today: AX0501 with call chains, including a service reached through a function value passed "
                 "to a standard function such as `map`; uses/needs in the outline; and AX0241 for a standard handle "
                 "such as `File(descriptor)` built outside its module.",
        "unlike": "In Python, Go and Rust any imported module can open files or sockets on ambient "
                  "process authority. Confinement comes from outside the type system (containers, seccomp, "
                  "the third-party cap-std crate for Rust). None checks per function, at "
                  "compile time, what a function can reach.",
        "sample": ("shell", """error[AX0501]: Missing provider: service 'Network'
  required by  main
  reached from run_generated_plan
  reached from upload""", "Real compiler output, trimmed."),
        "cites": ["12-services-di-permissions:278-322", "12-services-di-permissions:122-145", "12-services-di-permissions:184-195", "12-services-di-permissions:401-414", "09-modules:441-500", "26-agent-interface:316-340"],
    },
    {
        "id": "tainted",
        "state": "ships",
        "title": "Prompt injection meets the type checker.",
        "body": [
            "`tainted` is a type qualifier. Model completions, console input, network reads and process "
            "arguments are born tainted at their standard-library signatures. A tainted value where a plain "
            "type is expected is compile error AX1022, and every parameter that steers what the program does "
            "is such a position: a prompt's instruction, SQL identifiers, permission-minting arguments.",
            "The only way out is `endorse` with a mandatory rationale, so every place untrusted text becomes "
            "trusted is one line you can grep for.",
        ],
        "ships": "Ships today: AX1022 at every argument, field, return, binding and collection element; taint "
                 "through field projection, type arguments such as `List<tainted String>`, and string interpolation; "
                 "the prompt-instruction barrier; and a tainted path given to `scope_to`.",
        "unlike": "Python, Go and Rust treat model output as a plain string. A newtype can imitate "
                  "a taint marker by convention, but the standard library never marks its sources and nothing "
                  "makes unwrapping state a reason. Real defences are runtime libraries or separate analysers "
                  "such as CodeQL and Semgrep.",
        "sample": ("draconyx", """@doc \"\"\"
Builds a prompt that wrongly makes the email its instruction.

  * email - the email, as received
\"\"\"
hijacked(email: tainted String) -> Prompt:
    prompt(instruction = email, data = [])  // AX1022: `instruction` is an unmarked String.

@doc \"\"\"
Builds a prompt that asks for a summary, with the email kept as data.

  * email - the email to summarize
\"\"\"
summarize(take email: tainted String) -> Prompt:
    prompt(instruction = "Summarize the message.", data = [take email])""",
                   "The tainted email as the instruction is compile error AX1022; kept as data, it is allowed."),
        "cites": ["12-services-di-permissions:599-658"],
    },
    {
        "id": "laws",
        "state": "ships",
        "title": "Laws are checked. Not trusted.",
        "body": [
            "Concepts carry algebraic laws as syntax, and a law with no mode is checked. `drx test` "
            "synthesizes a property test for it, draws inputs from a fixed seed, shrinks any failure to a "
            "minimal counter-example and records it in a regression file that later runs replay first. "
            "A violation fails the run, and a release build refuses to build until every checked law passes. "
            "Skipping a law takes an explicit `trust`, and the test run reports each trusted law as unverified.",
            "Dispatch picks implementations by the laws a type keeps, so a false law would be a silent "
            "miscompilation. Laws decide membership instead: a type that breaks one is no member of the concept, "
            "and the report names every site that rested on it. An obligation the toolchain could not evaluate is reported as a “coverage shortfall” "
            "naming its cause, never as a pass, and fails the run unless `--allow-unsupported` is given; a "
            "`todo()` body gets its own `UNIMPLEMENTED` verdict instead of a fake failure.",
        ],
        "ships": "Ships today: `drx check` checks laws to decide membership, `drx test` and `drx verify` run every "
                 "obligation, a release build with a failing law builds nothing, and the violation report names each "
                 "site resting on the law and offers exactly two repairs.",
        "unlike": "Python, Rust and Go state laws like Ord/Hash consistency only in documentation; "
                  "the compiler never sees them. Property testing is a third-party library (Hypothesis, "
                  "proptest) or, in Go, stdlib testing/quick and fuzzing, and someone must restate each law as a "
                  "test by hand.",
        "sample": ("draconyx", """@doc \"\"\"Values with an `add` that can be regrouped and a `zero` that changes nothing.\"\"\"
concept Monoid<T>:
    add(left: T, right: T) -> T
    zero() -> T
    law associative(left: T, middle: T, right: T) checked:
        add(left = add(left = left, right = middle), right = right) == add(left = left, right = add(left = middle, right = right))
    law identity(value: T) checked:
        add(left = value, right = zero()) == value

@doc \"\"\"
Finds the middle value of `values` once they are sorted.

  * values - the values, in any order
\"\"\"
median(values: List<Float>) -> Float:
    todo()  // verdict UNIMPLEMENTED, not a failure.

example median(values = [1.0, 3.0, 2.0]) == 2.0""",
                   "A concept with two checked laws, and an example on a function whose body is `todo()`."),
        "cites": ["13-law-verification:4-96", "13-law-verification:339-363", "13-law-verification:524-539", "10-abstractions:83-102", "10-abstractions:230-252"],
    },
    {
        "id": "calls",
        "state": "ships",
        "title": "Every named call tells the truth.",
        "body": [
            "Named arguments are mandatory whenever a declared function with two or more arguments is called by its "
            "name; an unlabelled one is AX0256 unless it is a name matching its label, and the error lists the "
            "callee's labels. Ownership is spelled the same at both ends of a "
            "call: unmarked is read-only, `borrow` is exclusive mutation, `take` consumes. A wrong verb is AX0306, "
            "a consumption left unspelled is AX0321, and using a value after it moved is AX0312.",
            "Called by its name, a declared function can't have its arguments swapped by position, a mislabelled "
            "argument shows on the call line, and a mutation or consumption the argument list doesn't spell won't "
            "compile, so an agent reads what happens to each argument from the call alone. The exception is a "
            "pipeline: a stage may borrow the value piped into it and mutate it without `borrow` being written, "
            "though it consumes a named value only when `take` is.",
        ],
        "ships": "Ships today: all four diagnostics.",
        "unlike": "Rust and Go have no named arguments, so `resize(height, width)` compiles and looks right. "
                  "Python's keywords are optional unless the author opts in. Rust marks `&mut` but not a move, and method calls auto-borrow "
                  "their receiver unmarked. Go passes slices, maps and pointers unmarked while the callee "
                  "mutates through them.",
        "sample": ("draconyx", """open(url: String, timeout: Duration) -> Connection
close(take conn: Connection) -> None
send(borrow conn: Connection, request: Request) -> None

@doc \"\"\"
Opens a connection to `address`, sends `ping` once and closes it.

  * address - the address to connect to
  * ping - the request to send
\"\"\"
ping_once(address: String, ping: Request) -> None:
    conn = ^open(url = address, timeout = seconds(5))    // a failure goes up to the caller.
    ^send(borrow conn, request = ping)                    // mutation is spelled here.
    close(take conn)                                      // consumption is spelled here.
    close(take conn)                                      // AX0312: use of moved value `conn`.""",
                   "What happens to each argument, and which calls can fail, read off the call lines."),
        "cites": ["05-syntax-conventions:3-4", "04-core-language:290-311", "04-core-language:1992-2004", "04-core-language:2030-2046", "04-core-language:2127-2162", "07-memory-model:376-413"],
    },
    {
        "id": "failure",
        "state": "ships",
        "title": "No exceptions. No missing arms. No mercy.",
        "body": [
            "There are no exceptions and no try/catch. The signature says what a function gives; the body says "
            "how it fails, with `fail`, and the compiler infers what it fails with. Every call that can fail is "
            "marked: handled on the spot by arms in a `match` that name its failures, or passed up with a prefix `^`. A panic is "
            "for bugs only, nothing catches it on the spot, and every operation that can stop the program has a "
            "total twin that gives no value instead.",
            "Each kind of value is its own type, and a function that handles several kinds is written once for "
            "each. Values of different kinds stand side by side as `any T`, and putting a kind into `any T` when "
            "a function called on those values has no version for it is error AX0420, reported right there and "
            "naming the function and the type. A redundant `match` arm is error AX0602, not a warning. An agent "
            "sees every call that can fail where it is made, and gets an exact to-do list for any kind it missed.",
        ],
        "ships": "Ships today: AX0420 for a kind with no function, and AX0602 for a redundant arm.",
        "unlike": "In Python and C++ exceptions are invisible in signatures: you meet them in production. "
                  "Go hands you `err` and hopes you check it. Rust comes closest, but `catch_unwind` can catch a panic "
                  "on the spot, and an unreachable arm is only a warn-by-default lint. In Draconyx a redundant arm is "
                  "a hard error.",
        "sample": ("draconyx", """@doc \"\"\"A payment the bank has not answered yet.\"\"\"
type Pending

@doc \"\"\"A payment the bank has set aside.\"\"\"
type Authorized:
    amount: Money

@doc \"\"\"A payment given back to the customer.\"\"\"
type Refunded:
    reason: String
    amount: Money

@doc \"\"\"
Writes a pending payment's state on the receipt.

  * payment - the pending payment
\"\"\"
label(payment: Pending) -> String:
    "pending"

@doc \"\"\"
Writes an authorized payment's state on the receipt.

  * payment - the authorized payment
\"\"\"
label(payment: Authorized) -> String:
    "authorized {payment.amount}"

@doc \"\"\"
Writes the state of every payment of the day on the receipt.

  * payments - the day's payments
\"\"\"
receipt(payments: List<any T>) -> None:
    for payment in payments:
        print(label(payment))

@doc \"\"\"Writes the receipt of a day with a pending payment and a refund.\"\"\"
main() -> None:
    receipt([Pending(), Refunded(reason = "damaged", amount = Money(cents = 1200))])
    // error AX0420: `Refunded` is put into `any T` here, but no `label` takes a `Refunded`.""",
                   "A forgotten kind is a compile error that names it."),
        "cites": ["04-core-language:612-650", "11-type-system:133-138", "11-type-system:591-657", "11-type-system:1216-1297"],
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
   "toolchain": "1f80fbc8e1c003a0...", "tree": "1902a039f0cc11b1...",
   "methods": ["audit-trust", "call-path", "callees", "delete-def", "delta-card", ...],
   "authority": ["read: the workspace source tree",
     "read: the synthesized standard library",
     "write: workspace source under the package root",
     "write: derived state under the package root's .draconyx/ (law verdicts, compiled summaries)",
     "no network", "no home directory", "no process spawning"]}}""",
                   "Real daemon handshake, abridged."),
        "cites": ["26-agent-interface:30-79", "26-agent-interface:138-186", "25-tooling:786-791", "32-agent-conformance:468-489"],
    },
    {
        "id": "context",
        "state": "ships",
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
        "ships": "Ships today: outline, slice, search, `delta-card` and `resume-card` as daemon methods. Every card "
                 "is measured over its own text with the pinned reference tokenizer, `o200k_base`: the delta card "
                 "comes to 1,057 of its 2,000 tokens.",
        "unlike": "Assembling context is the agent framework's job (repository maps, embeddings, file reads); "
                  "the language defines no briefing format and no token budget.",
        "sample": None,
        "cites": ["26-agent-interface:254-274", "26-agent-interface:317-363", "26-agent-interface:516-525", "26-agent-interface:146-150", "26-agent-interface:931-982", "26-agent-interface:1086-1098", "26-agent-interface:379-396"],
    },
]

# Big numbers for the stats band (all from STATUS, as of AS_OF).
STATS = [
    ("733", "pages of specification"),
    ("90k", "lines of compiler written in Draconyx"),
    ("262", "diagnostic codes, each explained"),
    ("5", "compiler stages also written in the language"),
    ("439", "design rulings ratified"),
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
        ('Concepts: named, but never declared', "Write the functions and the type has the concept, as long as it keeps the concept's laws. No impl blocks, and no two modules can give one type two meanings.", 'ships'),
        ('Algebraic laws as code, property-tested by default', 'In C++ and Rust, associativity is a line in the docs. In Draconyx it is a `law` line in a concept, and a type that breaks it fails `drx test` with a shrunk counter-example.', 'ships'),
        ('Dispatch on algebra', 'Write the parallel reduction once. The compiler picks it only for types that keep the laws that make it correct.', 'ships'),
        ('Generics that infer the hard parts', 'Variance and const-generic shapes are worked out by the compiler, not annotated by the model.', 'ships'),
    ]),
    ('Memory and ownership', [
        ('Ownership spelled at both ends', 'Every handover at a call is written where the value is given and again where it is taken, so a model never has to guess who owns what.', 'ships'),
        ('Borrow checking with zero lifetime syntax', "Rust-grade memory safety without a single `'a`: you never write a lifetime, and the compiler works out every one.", 'ships'),
        ('Views inferred, not annotated', 'Put a borrow in a type with fields and the type becomes a safe view on its own: no keyword, no lifetime parameter.', 'ships'),
        ('No garbage collector, deterministic drops', 'No tracing GC and no pauses: each value is freed the moment its last owner lets go.', 'ships'),
    ]),
    ('Concurrency and distribution', [
        ('Data-race freedom by construction', 'No annotations to write: sendability is inferred from the ownership authorities you already write, and it decides what may cross a task boundary.', 'ships'),
        ('Structured concurrency', 'Several tasks run together through an ordinary standard-library function that takes the functions to run. The first failure stops the rest.', 'ships'),
        ('Move-only channels and a fair, replayable `select`', 'Every message exists in exactly one place at a time, and `select` timeouts run on a Clock you can fast-forward in tests.', 'ships'),
        ('Actors and let-it-crash supervision', 'Erlang-style actors under supervision trees that restart what crashed, with no exceptions anywhere.', 'ships'),
        ('Remote values that cannot hide the network', 'In Draconyx a network call never looks like a local call: `remote` is in the type, and reading a remote value as if it were local is a compile error.', 'ships'),
        ('Bundled distributed runtime', 'Cluster membership and failure detection come with every binary, and CRDTs are ordinary types: no ZooKeeper, no Consul, no sidecar.', 'ships'),
        ('Raft consensus as an ordinary type', '`Replicated<T, n>` keeps a value on a quorum of `n` nodes with linearizable reads and writes, inside the program: no external coordinator.', 'specified'),
        ('Live code swap in development, with checked state migration', 'In development, a running program loads a new version of a module beside the old one. The swap point is proven safe, state is handed over as a linear move, and migrations are functions the compiler checks. Release builds restart instead; the unikernel never swaps.', 'partial'),
        ('Native binaries', '`drx build` produces a native executable through the Rust bootstrap compiler\'s own code generator. The spec names one back end for the language, LLVM: `dev` and `test` builds run it without the optimizer, `release` and `proof` with it.', 'ships'),
        ('An LLVM back end written in Draconyx', 'A code generator written in the language itself that lowers checked programs to LLVM, so that the compiler can build itself, and every program, with no Rust inside.', 'partial'),
        ('Unikernel and WebAssembly targets', 'The same source targets a unikernel that needs no OS underneath, or a WebAssembly module.', 'specified'),
    ]),
    ('Safety and effects', [
        ('Services and dependency injection', 'A function uses a service without anyone passing it in. You get no constructor plumbing, no effect rows, and a compile error when nothing above a function supplies a service it uses.', 'ships'),
        ('Object-capability permissions (no ambient authority)', "No global `open` and no importable `Network`: the only way code gets authority is to be handed it. Starting from main's `System` powerbox, it can only be narrowed, never widened.", 'ships'),
        ('`tainted`: a typed defense against prompt injection', "Model output, console input and the command line are born `tainted`. Passing one to an unmarked parameter, or to a prompt's instruction slot, is compile error AX1022.", 'ships'),
        ('`trust` blocks: unsafe code that names its reason', 'Draconyx has no `unsafe`. It has `trust "why this holds":`, where every unchecked call site carries a mandatory written rationale an auditor can grep.', 'ships'),
        ('With blocks: one keyword for receiver, destructuring and scoped release', "One `with` covers Python's context managers, Rust's RAII and multi-value destructuring, even at the end of a pipeline.", 'ships'),
    ]),
    ('AI and numerics', [
        ('Shapes and named axes in the type', "A tensor's dtype, axis names and sizes belong to its type, so a tensor passed where a signature declares another shape fails at compile time, before any array is allocated.", 'ships'),
        ('grad and vmap as typed function transforms, with schedules certified by laws', 'Autodiff and auto-batching are plain functions over functions, and schedule rewrites are gated by laws instead of being trusted.', 'ships'),
        ('`jit`: captured and fused array code', '`jit` is a function transform in the same family as `grad` and `vmap`: it captures a computation as a lazy array graph and fuses it, and it composes with both.', 'specified'),
        ('Hygienic, typed dialects (macros, elab, comptime)', 'Dialects extend the syntax with Racket-grade hygiene and type-directed elaboration, without textual macros.', 'ships'),
    ]),
]

# Head-to-head: only rows where Draconyx ships today. Cells verified per language (2026-11-16).
VERSUS_LANGS = ['Draconyx', 'Python', 'Java', 'Kotlin', 'C#', 'C++', 'Rust', 'Go', 'Swift', 'Zig', 'Elixir', 'Haskell', 'Mojo']
VERSUS = [
    ('Every error has a code and an explain entry, with JSON repair edits from the compiler itself', ['yes', 'no', 'part', 'part', 'part', 'part', 'part', 'no', 'part', 'no', 'no', 'part', 'no']),
    ("Edits addressed by definition name, type-checked before they're written", ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
    ('Compiler-computed map of the services each function reaches, through the whole call chain', ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
    ('Model output typed untrusted at its standard-library source', ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
    ("Algebraic laws property-tested by default by the compiler's own test command", ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
    ('Named arguments required at every multi-argument call of a declared function by its name', ['yes', 'part', 'no', 'no', 'no', 'no', 'no', 'no', 'part', 'no', 'no', 'no', 'part']),
    ('Mutation and moves spelled in the argument list of every call', ['yes', 'no', 'no', 'no', 'part', 'part', 'part', 'no', 'part', 'part', 'no', 'no', 'part']),
    ('Missing and redundant match arms both rejected, on every match', ['yes', 'no', 'part', 'part', 'part', 'part', 'part', 'no', 'part', 'yes', 'no', 'part', 'no']),
    ('Deterministic agent protocol: same source tree, byte-identical answers', ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
    ('Ownership and borrows checked at compile time, with no tracing garbage collector and no lifetime annotations', ['yes', 'no', 'no', 'no', 'no', 'no', 'part', 'no', 'part', 'no', 'no', 'no', 'part']),
    ('Generic code dispatches on the algebraic laws a type satisfies, with arm totality checked', ['yes', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no', 'no']),
]
# The fine print for every "part"/"yes" a competitor gets, so nobody has to take our word for it.
VERSUS_NOTES = {
    'Python': [
        'Named arguments required at every multi-argument call of a declared function by its name: The author can opt in with keyword-only parameters after a bare `*` (PEP 3102), and calling them positionally is then a TypeError. But that is opt-in, and the error comes at run time, not compile time.',
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
        'Mutation and moves spelled in the argument list of every call: `ref`/`out` (and optionally `in`) must be written at the call site. Mutation through reference-type arguments and receivers is unmarked, and there is no move semantics.',
        'Missing and redundant match arms both rejected: A subsumed/unreachable arm is an error (CS8510 in switch expressions, CS8120 in switch statements). A non-exhaustive switch expression is only warning CS8509, even over the union types C# 15 added, and switch statements get no exhaustiveness check.',
    ],
    'C++': [
        'Every error has a code and an explain entry: There is no single reference compiler. MSVC gives errors stable codes (C2065, C2440...) with an online docs entry for each, but it has no built-in explain command. Clang and GCC emit machine-readable fix-its (clang -fdiagnostics-parseable-fixits; GCC -fdiagnostics-format=json/sarif), but GCC and Clang errors have no stable numeric codes.',
        'Mutation and moves spelled in the argument list of every call: To move from a named lvalue you must write std::move/std::forward at the call site. Moves of temporaries and return values are implicit, and std::move is only a cast, so a moved-from object stays usable. Mutation through a non-const reference parameter or a method receiver is not marked.',
        'Missing and redundant match arms both rejected: A duplicate case label in a switch is always a compile ERROR. A missing enumerator in an enum switch is a warning (-Wswitch, on in -Wall) and becomes an error only by opt-in (-Werror=switch).',
    ],
    'Rust': [
        'Every error has a code and an explain entry: Many rustc errors carry stable E-codes with `rustc --explain`, and `--error-format=json` emits suggestions marked MachineApplicable, which `cargo fix` / `cargo clippy --fix` apply. Not every diagnostic has a code: many errors and all lints lack E-codes.',
        'Mutation and moves spelled in the argument list of every call: `&mut buffer` is written at the call site for free-function args. Moves are not marked, and method calls auto-borrow `&mut self` without a marker.',
        'Missing and redundant match arms both rejected: A non-exhaustive match is a hard error (E0004) on every match. Unreachable or redundant arms only trigger the warn-by-default `unreachable_patterns` lint (an error only with deny/-D warnings).',
        "Ownership and borrows checked at compile time: Use-after-move and aliased &mut are rejected statically, with no tracing GC. But Rust has lifetime annotation syntax ('a), so it meets two of the three conditions.",
    ],
    'Swift': [
        'Every error has a code and an explain entry: Swift 6.1/6.2 diagnostic groups (e.g. [#StrictMemorySafety]) have names and documentation pages, but most errors have no code. Fix-its are built in and can be exported in machine-readable form (serialized diagnostics, -emit-fixits-path).',
        'Named arguments required at every multi-argument call of a declared function by its name: Argument labels are required by default at every call, but the author can opt out per parameter with _.',
        'Mutation and moves spelled in the argument list of every call: & is required at the call site for inout. consume (SE-0366) is optional. Mutating method calls on receivers are not marked.',
        "Missing and redundant match arms both rejected: A non-exhaustive switch is a compile error. A duplicate or unreachable case is only a warning ('case is already handled by previous patterns').",
        'Ownership and borrows checked at compile time: Swift uses ARC, not a tracing GC. It has no stable lifetime syntax (@lifetime for ~Escapable is still experimental). ~Copyable types reject use-after-consume statically.',
    ],
    'Zig': [
        "Mutation and moves spelled in the argument list of every call: Zig parameters are immutable, so a caller has to write &x at the call site to let a callee mutate a local, much like Rust's &mut. Method receivers auto-take the address, an already-held pointer passes unmarked, and moves don't exist.",
        'Missing and redundant match arms both rejected: On an enum or tagged-union switch, a missing prong is a compile error, so is a duplicate prong, and so is an else prong once every case is handled. (Integer switches need an else.)',
    ],
    'Haskell': [
        "Every error has a code and an explain entry: Since 9.6, GHC tags most diagnostics with [GHC-nnnnn] codes, and -fdiagnostics-as-json emits them, but GHC ships no explain command. The Haskell Foundation's separate error index documents only about 130 GHC codes, and the JSON hints are prose strings, not machine-applicable repair edits.",
        'Missing and redundant match arms both rejected: -Woverlapping-patterns (redundant arms) is on by default and -Wincomplete-patterns (missing arms) comes with -W or -Wall, but both are warnings; rejecting a match takes -Werror or -Werror=incomplete-patterns.',
    ],
    'Mojo': [
        "Named arguments required at every multi-argument call of a declared function by its name: Mojo supports Python-style keyword-only parameters (after `*` in the signature), so an author can opt in to required labels, as in Python. The default is optional, so Mojo scores the same as Python.",
        'Mutation and moves spelled in the argument list of every call: Ownership transfer is written `buffer^` at the call site, but passing to a `mut` parameter is unmarked.',
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
    ("Specification", "32 sections, a 733-page PDF with 668 code blocks that the corpus tool pulls into the compiler's tests."),
    ("Toolchain", "Lexer, parser, resolver, type checker, ownership checker, interpreter with law runner, canonical formatter, agent daemon and native code generation."),
    ("Agent daemon", "36 JSON-RPC methods, among them outline, get-def, slice, search, who-calls, what-breaks-if, put-def, put-defs, fork, verify, `delta-card` and `resume-card`."),
    ("Diagnostics", "262 codes, each with an explain entry; a test enforces the coverage."),
    ("Self-hosting", "The lexer, parser, resolver, type checker and ownership checker are written in Draconyx itself, about 90,000 lines. As of 12 November 2026 each one gave the same output as its reference implementation on the whole shared test corpus. The binaries `drx build` makes come from the Rust bootstrap compiler's own code generator."),
    ("Native code", "`drx build` compiles a package to a native binary that prints and exits exactly as the interpreter runs it, on all 159 back-end unit programs."),
    ("Design record", "439 design rulings ratified into the spec; five example packages, among them an online shop, event sourcing and FlashAttention, a gallery of 20 common patterns written beside Rust, C++, Zig, Java and Elixir, and a 4,925-line standard library generated from the spec."),
    ("Release", "In development, first commit 20 July 2026. The first public release is the first compiler written entirely in Draconyx."),
]


SIGNUP_TITLE = "Stay tuned"
SIGNUP_LEAD = (
    "The dragon is hatching. Be first to know when Draconyx launches, and hear about every new feature "
    "the moment it lands. Updates only, straight from the source. One click to leave."
)
SIGNUP_FINE = "We send a confirmation link first. Nothing arrives until you click it."
# Under the ALTCHA widget: its box ticks by itself, and a visitor who expects a picture puzzle cannot tell why.
SIGNUP_CHECK = (
    "The box ticks itself when you send the form: your browser solves a small puzzle to prove it isn't a bot, "
    "with nothing for you to do."
)
SIGNUP_NOSCRIPT = "The form needs JavaScript: a short check in your browser keeps bots off the list."
# The honeypot's label. People never see the field (it sits off-screen, hidden from screen readers); bots fill it in.
HONEYPOT_LABEL = "Leave this field empty"

INVOLVED = (
    "Want in early? For design discussion, collaboration, or to train or evaluate models on Draconyx, email us."
)

# Footer note. Keep it true of the server (infra runbook, "Website statistics"; listmonk privacy settings):
# Caddy access log rolled daily and deleted after about 14 days, monthly/all-time totals with anonymised IPs,
# listmonk record_optin_ip off, view/click tracking off, double opt-in; and of the form (README, "Signup form"):
# the honeypot (listmonk's nonce field), the ALTCHA widget served from /assets/altcha/ and its challenge from
# ALTCHA_CHALLENGE_URL on this site, listmonk's CAPTCHA setting on.
PRIVACY = (
    "This site sets no cookies, runs no tracking scripts and loads nothing from other sites. Its web server logs each "
    "request: your IP address, the time, the page, and what your browser sends with it, such as its name and the page "
    "that linked here. The logs are kept about 14 days for security and visitor statistics, then deleted; after that, "
    "the statistics keep only totals, without full IP addresses. The signup form sends your email address to the "
    "Draconyx list at lists.draconyx.ai, on the same server. To keep bots out, the form has a field that people never "
    "see, and the list refuses a sign-up that fills it in; and a script served by this site, ALTCHA, has your browser "
    "solve a small computing puzzle that the list sets. The script fetches the puzzle from this site and puts the "
    "answer in the form; it sets no cookies, stores nothing in your browser and sends nothing anywhere else. You get "
    "a confirmation email first and nothing else until you confirm, the list does not record your IP address or which "
    "emails you open or links you click, and every update has an unsubscribe link. Questions: email us."
)

# The blog (README, "Blog"): the words around the posts. Each post's own words are in its file in posts/.
BLOG_URL = "/blog/"
BLOG_TITLE = "Draconyx blog"
BLOG_HEADLINE = "Notes on Draconyx"
BLOG_LEDE = "Articles about the Draconyx language: its design, its compiler and the choices behind them, newest first."
BLOG_LLMS = "articles about the language, its design and its compiler, newest first"
BLOG_EMPTY = "No posts yet."
BLOG_BACK = "All posts"
BLOG_FEED_LINK = "Atom feed"
# The home page's blog section, between Status and Stay tuned: the latest published posts and a link to the blog.
BLOG_HOME_KICKER = "From the blog"
BLOG_HOME_LEDE = "Why the language works the way it does, one article at a time."
BLOG_HOME_ALL = "Read the blog"

# The not-found page (404.html): Caddy serves it, with status 404, at any address on draconyx.ai that has no page
# (README, "Not found"). The heading, one line and the way home; the signup form stays on the real pages.
NOT_FOUND_TITLE = "Page not found: Draconyx"
NOT_FOUND_HEADLINE = "Page not found"
NOT_FOUND_LINE = "The address you asked for does not exist on draconyx.ai."
NOT_FOUND_HOME = "Back to draconyx.ai"

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
    "29 October and 2 November 2026, on the spec as it stood then. The excerpts are verbatim: \u201c\u2026\u201d marks a cut, and [Draconyx] stands "
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
    {"date": "2026-11-15", "title": "One LLVM back end; drx publish, tune and replay; cluster substrate and Merged values", "items": [
        ("Native code", "The spec now names one code generator, LLVM: `dev` and `test` builds run it without the optimizer, `release` and `proof` with it. The tier contract binds the release optimizer, so a release build prints, byte for byte, what a `dev` build of the same program prints and exits with the same status. `Float` arithmetic is IEEE 754 binary64 at every tier with no fast-math, and the only law-driven rewrites are a catalogue of three over folds (split fold, strided accumulation, parallel reduction), each consuming only exact laws at or above the target's minimum mode.",
         "78100e8e6f b6ea2a21e8 05e74e38d1"),
        ("Toolchain", "`drx publish` is new. A path dependency is `AX0202`, and a missing version, or one below the minimum that the changes to the public surface since the last published bundle force, is `AX0203`. The package must also match its lock, check, and pass verification at `release`. `--dry-run <dir>` writes the bundle (package card, compiled summaries, surface and trust records, source) into a local registry directory, and a package card over its budget is published whole with the warning `AX0204`.",
         "c43dbc0333 05e74e38d1"),
        ("Toolchain", "`drx tune` enumerates an `@autotune` block's search space in source order and decides every law gate before measuring: a candidate whose gate fails is reported with its code, such as `AX0701`, and never runs. The fastest measured candidate is written as a `_pinned` schedule, with a `[[schedule]]` row in an existing `draconyx.lock`, while `drx bench` runs the same search and writes nothing. `drx run --record <dir>` records a run's service traffic and a hash of every training step, and `drx replay` re-runs the program from that recording alone, up to a given step, and reports the first step whose hash differs.",
         "480cba9888 a37dfdd841"),
        ("Syntax", "A module that activates a dialect with `use extension` now parses that dialect's forms where they are written. Each dialect is checked when it loads, and so are the dialects one module activates against each other, under eight new codes from `AX0901` to `AX0908`, such as two dialects reserving one keyword (`AX0907`). `drx gen schema` writes a PostgreSQL database's tables as a checked-in module of `Query` `table` declarations. A column outside its type map is `AX0826`, and `--check` reports drift as `AX0827`.",
         "874319ac1b a17b82d388 a89858fef4 05e74e38d1"),
        ("Agent daemon", "Several clients can now reach one workspace daemon at once, each on its own connection, and `initialize` gives each a client identity. A fork's one writer is the client that created it. A write, `drop-fork` or `merge-fork` from any other client is the new error kind `fork-writer-held`, and asking for an identity another live connection holds is `client-identity-held`.",
         "dee41152cb 05e74e38d1"),
        ("Standard library", "Every binary now carries a cluster substrate: SWIM membership with gossip, failure detection decided by majority, joining through one seed address, and 256 shards rebalanced on every join and leave. The `[deploy]` key `cluster` switches it on, `cluster_seed` and `cluster_listen` give its addresses, and the environment can override each. `std.dist` gains `Merged<T>`, a replicated `Mergeable` value whose writes and reads are local on either side of a partition and whose replicas converge through `T`'s own `merge` once the partition heals.",
         "65f5ad3483 8b8a2c3129 05e74e38d1"),
        ("Safety", "Each `[native]` library's `[permissions]` row is now checked by the library's mode. An `in_process` library whose row is missing or is a list is `AX0830`, with an edit that writes `\"unbounded\"`, and `\"unbounded\"` on any other row is `AX0831`. A sandboxed or isolated library with no row is budgeted to nothing.",
         "95fdce7632 05e74e38d1"),
        ("Types", "An explicit `from` whose argument already has the target type is now the identity conversion and needs no conversion function. A `from` into a type with no conversion from the argument's type is now one `AX0420` naming the missing conformance, such as `From<Int>`, instead of `AX1001` beside `AX1007`. `Pytree` is now derived structurally: a struct, tuple, `List` or `Array` through which a tensor is reachable is one, so the standard library's tree walks and checkpoint functions carry their `Pytree` bounds.",
         "3f571790a6 515008468a"),
    ]},
    {"date": "2026-11-14", "title": "Cloning a type parameter's value needs a Clone bound", "items": [
        ("Types", "`clone x` on a value of a type parameter now needs `where T: Clone`. Without the bound it is `AX0420` at the operand (\"type parameter `T` has no `Clone` bound\"). Before, it checked clean and an instantiation could copy a type with no `Clone`.",
         "3c40ae6654"),
    ]},
    {"date": "2026-11-13", "title": "Generators with yield; naming rules enforced; a pinned solver discharges laws", "items": [
        ("Syntax", "A function declared `-> Generator<T>` now gives its values one at a time with `yield`, and `for` walks the generator a call returns. The call runs none of the body: each step runs it to the next `yield`. `yield` is a reserved word; a `yield` outside a generator is `AX0452`, and a generator body that gives back any value other than another generator is `AX0453`.",
         "8b27780556 4b466065b7 8e68f1088e 4da3ce9068 a3c91e95c4"),
        ("Syntax", "The compiler now checks naming rules as errors. Types and constructors are UpperCamel, and every value name, `const`s included, is lower_snake (`AX1201`). No type may take the name of a prelude type (`AX1216`), and a function's leading word must keep its promise: an `is_` function returns `Bool`, and an `into_` function takes its first parameter with `take` (`AX1205`). The standard constants are now `int_min` and `int_max`.",
         "65cab49641 c8dea6338b"),
        ("Types", "`some C` is removed: written in a type it is `AX0296`, and a function returns its named type instead, so std's iterators are named types such as `Chars`. `any C` now appears only inside data and as a result whose type is decided at run time. A parameter of type `any C` is `AX0434`, and an `any C` result that always returns one type gets the warning `AX0435`.",
         "e67465e676 5f62f6da94"),
        ("Laws", "At the `release` and `proof` targets, a solver pinned in the toolchain now discharges each `proven` law that its own proof does not close, and a law it cannot prove fails the build (`AX0711`). At those targets `drx check` now also asks a solver to prove each refinement the checker left open, reporting `AX1057` for one it cannot prove, and dev and test builds check such refinements at run time. A law's `proof:` block is now checked: a goal left open is `AX0722`, and a proof that is not total, such as one that appeals to its own law, is `AX0745` to `AX0748`.",
         "796b0853a9 ab7f5ce4f3 0593f9c4d2 da2132bc1b 1a922c9256 347e5948ec b8ec8d5b9d 1c8cbcb40b"),
        ("Safety", "The manifest's `[permissions]` table is now enforced. A dependency that reaches a permission its row does not grant is `AX0507`, and grants narrow along the dependency graph, because a package passes on only what it holds. The new `drx add` writes a dependency's row and asks which permissions to grant, and `drx run` now gives `main` a sandboxed `System` by default, whose `Network` records and refuses every request; `--live` gives it the full powerbox.",
         "9f221f0c4e 4308769dc4 6543ee3d01 63b97d7c9d a02dbdd69c"),
        ("Toolchain", "The new `drx lock` writes `draconyx.lock`, which pins the toolchain and every path dependency by hash; an input that no longer matches it is `AX0822`, and a `release` or `proof` build then builds nothing. The compiler now checks the manifest's `edition` (`AX0212` for an unknown one), and `drx migrate --edition` moves a package between editions. A package can order its modules in `[[layer]]` tables in `draconyx.toml`, where a reference up a layer is `AX0817`, and a module under an `internal/` folder can be reached only from inside its parent's subtree (`AX0281`).",
         "601c775ba8 e395aade1c 876ce64507 a02dbdd69c d06914af48"),
        ("Agent daemon", "The agent daemon now serves `rename-def`, which rewrites every reference to a definition in one transaction. It also serves `why-conformance` and `why-not`, which use recorded witnesses to explain why a type does or does not conform to an abstraction. `callees`, `call-path` and `provenance` answer questions that otherwise mean reading one definition after another, `search` and `outline` now cover the standard library and dependencies, and a `put-def` now adds, in the same write, the plain `use` line its definition needs when exactly one import fits.",
         "2c4965bc46 00aa0c1d6e c8b1df645a c4d32d5874 aac5396e8f 3be2d03cd5 aa592f1689"),
        ("Types", "The standard tensor operations, such as `matmul`, the reductions and `transpose`, now check shapes at each call: a `matmul` whose inner axes disagree is `AX1001`, naming the axis and both extents, and each result carries its computed shape on to the next operation. A `?` axis now stands for an extent known only at run time, and the checker types `as_static` as opening it to a fixed size.",
         "4c2394274d ec44aac8e6"),
    ]},
    {"date": "2026-11-11", "title": "Consts computed at build time; match arms narrow; remote enforced; drx fix", "items": [
        ("Types", "A `const` initializer is now evaluated once, at build time, and may call only pure functions: one that reaches a service, a permission, an `extern` or a `trust global` is `AX0442`. One that traps is `AX0443`, one that exceeds the evaluation quota `AX0444`, one the build cannot evaluate `AX0445`, and consts that read each other `AX0446`. The spec now defines these rules in a Constants paragraph.",
         "55c52cf0e3 abb5798f3d 72c5ddaea0 639cade1d3"),
        ("Types", "A `match` arm on a variant with named fields may now name just the variant (`Refunded ->`). Inside it, the matched value is narrowed to that variant, so its fields are read with `.` (`payment.amount`). Reading another variant's field, or reading after a write to the value, is `AX1002`. A `match` over a call whose arms read payload fields is the new `AX0450`, with an edit that names the value first.",
         "f1c6de4cc7"),
        ("Safety", "`remote` is now enforced: a field read on a remote value is `AX0447`, a `remote T` used where a plain `T` is expected is `AX0448`, and `share` or `watch` of a remote value is `AX0308`. The value a `sandboxed` or `isolated` foreign call returns is now `tainted`, like network input, so it reaches an unmarked position only through `endorse` (`AX1022`).",
         "5e7a534d75 1070efdade"),
        ("Toolchain", "`drx fix` now applies every suggested edit marked `always` as one transaction, writing all files or none, and then checks again. A `maybe` edit is applied only when it is passed back with `--edits`. More diagnostics now carry edits, and each `maybe` edit states its consequence: `AX0601` adds the missing arms, `AX1003` the missing fields, `AX0321` offers `share`, `take` or `clone`, and `AX1005` and `AX1008` write the annotation or label.",
         "36d9d5df42 597d14d38b cde84b5a89"),
        ("Laws", "`drx build`, `drx test` and `drx verify` now take `--target` with `dev`, `test`, `release`, `proof` or a profile from the manifest's `[targets]` table; an unknown target is `AX0727`. `dev` runs no law, `release` fails on a failing law, witness or test, and `proof` also refuses each `trust` or `checked` law and each `proven` law not discharged. The new `drx suggest-laws` proposes laws for a module's operations and keeps only those that hold on every sample it runs.",
         "2f6d192640 14ef278690"),
        ("Agent daemon", "The agent daemon now serves `who-conforms`, `what-conforms`, `explain`, `explain-dispatch`, `suggest-laws` and `audit-trust`. `drx audit trust` prints the last of these: every `trust` block, conformance and global, with its rationale, module and hash. The spec now has an appendix that fixes the interface's method names, payload schemas, error kinds and framing.",
         "359210ee8c 4d4fa94a70 bd1e303d66 57fbd6d187 46c44d85a6"),
        ("Native code", "An `extern \"C\"` function in `in_process` mode now runs in `drx run` and in built binaries. The library is opened or linked and called directly, with `Int`, `Float`, `Bool`, `Byte` and `Ptr` values crossing the boundary. Any other parameter type, or more than six integer or eight `Float` parameters, is the new `AX0811`, which `drx run` and `drx build` report before any code runs.",
         "39c9a0adf1"),
        ("Standard library", "`graphemes`, `words`, `sentences`, `normalize`, `to_upper`, `to_lower` and `trim` now follow Unicode 17.0.0, the same in the interpreter and in native code. Segmentation follows UAX #29, and `normalize` handles NFC, NFD, NFKC and NFKD. `std.text` gains `is_whitespace`, `is_xid_start`, `is_xid_continue` and `general_category`.",
         "ecde22152b e97de4826c"),
    ]},
    {"date": "2026-11-09", "title": "Abstraction defaults now fill bare bounds", "items": [
        ("Types", "An abstraction's default type arguments now apply wherever the abstraction is named: in a `where` bound, a `require` clause and a `when` arm, as in a type. Given `abstraction Shl<Rhs = Int>`, a bare `where T: Shl` is now `where T: Shl<Int>`, so `value << 1` checks, and a type that shifts by a `String` meets neither. The spec now says so.",
         "8056dbd98e"),
    ]},
    {"date": "2026-11-08", "title": "New comment, function and binding forms; failure inferred; lock order checked", "items": [
        ("Syntax", "`#` now starts a comment, and a `\"\"\"` block is a declaration's documentation: directly under a function's header, first in a type's body, or directly above a `const`. A block anywhere else is the new `AX0439`, and an unclosed one is `AX0104`. The spec now defines both forms.",
         "a1fce4aec0"),
        ("Syntax", "A function can now be declared without `def`, as `find(id: Int) -> User:`; declared this way it writes its result type, and a function that gives nothing writes `-> None` (leaving it out is `AX0264`). `@export` and `@strict` now mark a declaration, one per line above it; in a module that writes `@export`, an item without it is hidden from other packages, and exporting a function that shows a hidden type is `AX0240`.",
         "8a9d07b6cb 01e4eda343"),
        ("Syntax", "Inside a function, the first `=` on a name not in scope now declares it, without `let`: `count = 0`, `rate: Float = 0.05`. Declaring such a name again in its scope, or shadowing it with another binder, is the new `AX1029`, and a name declared this way whose value no path reads, such as the typo `totl = total + 1`, is the new `AX0319`.",
         "095ca9411d"),
        ("Syntax", "Compound assignment (`+=`, `-=`, `*=` and the others) and the statements `x++` and `x--` now exist; `y = x++` is `AX0268`, and `drx fmt` now writes `x = x + y` as `x += y`. `**` is now a power (`-x ** 2` is `-(x ** 2)`), `~x` a bitwise NOT, and `not in` the negated `in`.",
         "b319d6bab2"),
        ("Types", "A function can now fail by writing `fail value` in its body, with nothing about failure in its signature: the checker infers which functions can fail, through function values too. A call that can fail is handled where it is written, by a `match` with `ok` and `fail` arms, or its failure is passed up to the caller; a call that does neither is the new `AX1040`. `drx run` and built binaries both run these forms.",
         "23d18bd6cc 79d99b0df2 eb10f75e74 a217e1158b 8eaae3c359"),
        ("Concurrency", "A lock is not re-entrant, and the checker now refuses taking a lock again while the same task holds it, directly or through a chain of calls (the new `AX1055`). Taking two locks in opposite orders anywhere in a program, which can leave two tasks waiting on each other forever, is the new `AX1056`, and the spec now has a section on lock order. At run time a lock is now held until its guard ends, in `drx run` and in built binaries.",
         "909edf34f9 ecda0ec027"),
        ("Safety", "Process-global mutable state is now declared with `trust global`, which replaces `trust static` (`AX0296`, with the repair), and only in a module the root manifest lists in `proof-allowlist`; anywhere else it is the new `AX0285`. Assigning to a global now runs in `drx run` and in built binaries. A dependency whose `[dependencies]` row says `trust = false` may now hold no trust code at all (`AX0807`).",
         "f4f764f621 b1952f0fe2"),
        ("Standard library", "`Console.print` and `Console.write` now cannot fail: output that never reaches its stream, through a broken pipe or a full disk, is lost output, the program runs to its end, and the run exits 1 with a lost-output message. `Map` and `Set` now have `is_empty` and `clear`; a `for` loop over a `Map`, `OrdMap` or `OrdSet` now works, borrowing or with `take`, and a plain `for` over a `Set` now borrows instead of asking for a copy.",
         "ac786ae944 606c34e307"),
    ]},
    {"date": "2026-11-07", "title": "Taint follows computation; raw pointers stay in trust; law shapes checked", "items": [
        ("Safety", "A value computed from a `tainted` or `secret` one now keeps its marker through arithmetic, comparison and logic operators, pattern binders, destructuring and field reads, and a `tainted` one through string interpolation, so each of these routes is `AX1022` or `AX1023` where the value meets an unmarked position. Branching on such a value stays legal. `endorse` and `declassify` now refuse a view as their value (`AX0438`), and new `to_bytes` and `to_string` overloads keep the marker on the owned copy.",
         "d2ace5dd81 9e98365d4d"),
        ("Safety", "A raw `Ptr<T>` can now be created only inside a `trust` block (`AX0721` elsewhere), and neither a `Ptr` nor a struct holding one is `Sendable` or `Foreign` unless a trust conformance vouches for it. A trust conformance of `Sendable` on a generic type now holds only where its type arguments are `Sendable`.",
         "38169150b3"),
        ("Standard library", "A live `FileSystem` now has a root, the package root under `drx run` and the launch directory for a built binary, and nothing leaves it: host-absolute paths, paths with a `..` component and symbolic links that lead out of the root are refused. `drx run --fs-root <dir>` anchors it elsewhere, and the new `FileSystem.kind` says what a path names, following links.",
         "d35ea5168d 2761388dfd"),
        ("Laws", "A law's shape is now checked at `drx check`: a verification mode on a `pass_rate` law is `AX0716`, a rate outside (0, 1] `AX0717`, a bare predicate body without `pass_rate` `AX0718`, a rate or tolerance that is not a `Float` literal `AX0719`, and a qualifier that disagrees with the body's operator `AX0720`. Inside a law body a free variable no longer supplies the argument label it spells, so `minus(left, right) == minus(right, left)` is `AX0256` instead of a law that compares a call with itself.",
         "5def3eea4f c9a29c65aa"),
        ("Types", "An integer literal outside its type's range, such as an `Int` outside the signed 64-bit range or a `Byte` above 255, is now the compile error `AX0436`; before, it ran as 0 or as an `Int`. A `\\u{...}` escape naming a surrogate or a value above `10FFFF` is now `AX0106` in a character literal too, and a map literal with `Float` keys is refused (`AX0421`).",
         "3304450521"),
        ("Types", "A refinement `v in 0..4096` over integer-literal bounds now means `0 <= v and v < 4096`, so the two spellings are one type with one content hash, and a guard written one way proves the other. Two refinements are now the same type only when the names in their predicates also resolve to the same things, not merely when their text matches.",
         "1239e342d9 d627a31268"),
        ("Interpreter", "A run of consecutive statement-level `when` arms now runs as one cascade, in `drx run` and in built binaries: the first arm whose test holds runs, and none need hold. Such a statement now discards its arm's value, and a `break` or `continue` with no loop around it in the same function is the new `AX0430`.",
         "25c5d0eaf9"),
        ("Toolchain", "Content hashes now cover five parts of a definition they missed: tuple labels, the verb of a `for` loop or a lambda parameter, a lambda parameter's default, `trust def`, and a written type the compiler keeps less of, such as `@heap Grid<Int, Int>`. A closure hash now also moves when a `const`, a field default, a chosen witness or a standard-library item it reads changes.",
         "a1f07d53fe b666b65b0f"),
    ]},
    {"date": "2026-11-06", "title": "Abstractions met by inference; generic functions without type lists; laws decide membership", "items": [
        ("Types", "A type now satisfies an abstraction when functions with its operations exist for it in any module the program uses; `extend` blocks and the `include`, `!include` and `asserts` clauses are removed (`AX0296`, with a fix). A function may have the body `derived` for `compare`, `hash`, `generate` and `shrink`. Two modules that each supply the same abstraction's operations for one type are `AX0422`, settled by a `[conformances]` row in `draconyx.toml`.",
         "b930b3568c"),
        ("Types", "A function now declares no `<...>` list: a single capital letter in its signature is a type variable, and a single lowercase letter in a size position a size variable. A call writes no type arguments, and a variable nothing fixes by the end of the statement holding the call is `AX1025`. Axes are passed as labeled arguments, as in `softmax(tensor = logits, over = classes)`.",
         "e9b4daad17"),
        ("Laws", "A type is now a member of an abstraction only when it has the operations and breaks none of the laws, which the build checks and caches. A bound at a type that breaks a law is `AX0432` with the counterexample, a bound at a type with no generator for a law is `AX0433`, and a function in the package that makes its type break a law is the warning `AX0714`. Law qualifiers such as `Add associative` are removed (`AX0296`); std declares `AssociativeAdd` and `CommutativeAdd` instead.",
         "9ddf3df8c7 b930b3568c"),
        ("Types", "Two overloads of one name whose parameter types are the same and that differ only in their labels, such as `area(rect: Rect)` beside `area(shape: Rect)`, are now `AX1027`. A bound now also supplies the operations of the abstractions its abstraction requires, so under `where T: HasPerimeter` a function can call `area`.",
         "81bec1e471 b9b8e2f6e2"),
        ("Ownership", "Once a `match` arm is taken, the scrutinee's borrow now ends at the last use of the arm's binders, so an arm can write the map it looked in. Assigning a whole new value to a `borrow` parameter, as in `counter = counter + 1`, now reaches the caller, in `drx run` and in built binaries.",
         "5cf63da831 4075b3b36c"),
        ("Standard library", "An empty `{}` now builds a `Set` where a `Set` is expected, `len` takes a `Map` or a `Set`, and a `Str` shows as its text. `replace` and `int_of_text` now also take a `String`, and `FileSystem.read_to_string` reads a whole file as text. `Array` now has a generator and a shrinker, so std's `Sequence` law is checked for it at a fixed size.",
         "2659ca296d 5984f90694"),
        ("Agent daemon", "`get-def`, `put-def` and `delete-def` now treat a definition as ending at its own last line, so a write no longer removes the comments or the doc block of the definition below it, and a definition inserted after another lands above that doc block.",
         "a7d7282ab3"),
        ("Toolchain", "A Tree-sitter grammar and a Zed extension now color Draconyx source in the Zed editor.",
         "36aa653813"),
    ]},
    {"date": "2026-11-05", "title": "drx test refuses ownership errors; daemon names the keys it ignored", "items": [
        ("Testing", "`drx test` and `drx verify` now refuse a package with ownership errors, as `drx run` and `drx build` do, printing the diagnostics as `drx check` prints them. A refused package now exits 3, so it can be told apart from a failed obligation, and `--force` runs the obligations anyway.",
         "8fefeeaa9d"),
        ("Syntax", "A line that begins with `and(` or `or(`, with no space, now starts a new statement calling a function of that name instead of continuing the previous line as a boolean operator. `and (` and `or (` still continue the line.",
         "e0f35708a4"),
        ("Agent daemon", "Every daemon answer now ends with `ignored`, the request keys it did not honour, such as a misspelt key or a value of the wrong type, and `initialize` now lists every error kind. The new `new-def` adds a definition to a module.",
         "e4582e4792"),
    ]},
    {"date": "2026-11-04", "title": "Agent daemon write lock freed on a crash; takeovers reported", "items": [
        ("Agent daemon", "The workspace write lock is now held by an operating-system lock where the file system supports one, so a crashed daemon's lock is free at once and a running daemon keeps its lock however long it idles. A daemon that has lost the lock now fails its next write with `write-lock-lost`, and a write that takes a lock over says so in `reclaimed_lock`.",
         "78dfa60846"),
    ]},
    {"date": "2026-11-03", "title": "Keywords renamed to abstraction, require, take and watch; overload families told apart", "items": [
        ("Syntax", "The keywords are now `abstraction` (was `capability`), `require` (was `requires`), and `take` and `watch` for the owning and non-owning verbs (were `transfer` and `observe`). An old word where no name can stand is `AX0296`, with a fix that writes the new one; elsewhere it is an ordinary name. std's `take` on a list is now `remove_at`.",
         "2cf0db7488"),
        ("Types", "Two definitions of one name and label set are now `AX0233` unless they answer one operation of an abstraction or service for different types or arguments, as two `from(value: HttpError)` into two error types do. Each member of such a family now has its own address, so a call runs the member its types select and an `Int` binding can no longer hold a `Float`.",
         "8afa42a584"),
        ("Laws", "A failing law over `Float` now reports small, readable counterexamples such as `0.0, 0.0, 1.0`: the shrinker tries the simplest candidates first, by a fixed order that puts short decimals before long ones and finite values before infinities and NaN.",
         "da7841b9e5"),
    ]},
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

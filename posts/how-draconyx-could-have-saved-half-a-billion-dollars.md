---
title: "How Draconyx could have saved half a billion dollars"
date: 2026-11-21
summary: "In 1996 the first Ariane 5 rocket was lost, half a billion dollars by media reports, because a number assumed to fit in 16 bits did not, and the check that would have caught it had been left out to save time. Design by contract writes such an assumption down, but checks it while the program runs, where it can be switched off. In Draconyx it is a rule on a type, proven when the program is built, so flight software written in Draconyx has no rule checked in flight and nothing to switch off."
tags: design, types, contracts
draft: false
---

Every program rests on assumptions about its values: a count is never negative, an index is inside its list, a
number fits in the space kept for it. When an assumption is written down and checked, a broken one is a message. When
it lives only in someone's head, or in a document nobody reads with the code, a broken one is whatever the machine
does next. A rule that every value of a type keeps is called an invariant, and how a language checks it decides
whether a wrong assumption is found by the compiler, by a test, or in flight.

## Ariane 5, Flight 501

Ariane is Europe's family of rockets that carry satellites into orbit, built for [ESA](https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Ariane_5), the European Space Agency.
Ariane 4 was the rocket Europe was flying at the time. Ariane 5 was its successor: in ESA's words, "larger and more
powerful" and "developed essentially as an all-new launch system". ESA [delegated](https://esa.int/Newsroom/Press_Releases/Flight_501_failure-_first_information) the management of
the programme to CNES, the French space agency, and project teams of CNES and industry developed it. Its first
flight, Flight 501, left Kourou in French Guiana on 4 June 1996, uncrewed, carrying ESA's four
[Cluster](https://esa.int/About_Us/ESA_history/Cluster_s_decade_of_discovery) satellites, a science mission built to study how the solar wind meets Earth's magnetosphere.

About 37 seconds after its main engine ignited, some 30 seconds after lift-off, at an altitude of about 3700 m, the
rocket veered off its path, broke up under the aerodynamic loads and destroyed itself, with the four satellites.
Its debris fell over about 12 km² east of the launch pad, an area that is, in the [Inquiry Board](https://csapp.cs.cmu.edu/2e/docs/ariane5rep.html)'s words, "nearly all
mangrove swamp or savanna". Media reports put the loss at half a billion dollars, uninsured, as
[Jézéquel and Meyer](https://archive.eiffel.com/doc/manuals/technology/contract/ariane/) noted the following January.
Other estimates put it at about 370 million dollars: [Wikipedia's account of the flight](https://en.wikipedia.org/wiki/Ariane_flight_V88) gives "more than
US$370 million", citing Mark Dowson in ACM SIGSOFT Software Engineering Notes, March 1997.

The Inquiry Board, chaired by Jacques-Louis Lions, reported on 19 July 1996. The cause was in the inertial reference
system, the SRI, which measures the rocket's attitude and movement for the on-board computer. Its software was, in
the report's words, "practically the same as that of an SRI which is presently used on Ariane 4". One of its functions, an
alignment computation, served no purpose once the rocket had lifted off, but it was kept running for about 40
seconds after lift-off, as on Ariane 4.

That function computed a value called BH, the horizontal bias, as a 64-bit floating-point number, and converted it
to a 16-bit signed integer. A 16-bit signed integer holds -32768 to 32767. Ariane 5's early trajectory gave
"considerably higher horizontal velocity values" than Ariane 4's, the bias grew past what 16 bits can hold, and the
conversion raised an Operand Error.

The conversion could have been protected. The report says that "the data conversion instructions (in Ada code) were
not protected from causing an Operand Error". Of seven variables at risk, four had been protected and three left
unprotected, BH among them, because the SRI computer had a maximum workload target of 80%. The three had been judged
safe because they were "either physically limited or that there was a large margin of safety". For Ariane 4 the
reasoning held. For BH on Ariane 5 it did not, and Ariane 5's trajectory data had not been included in the SRI's
requirements.

What followed was the design working as specified. On an exception, the SRI was to record the failure and shut its
processor down. There were two SRIs, identical in hardware and software, so the backup failed first, in the previous
72 ms data cycle, and the active one about 0.05 seconds later, the same way. The active SRI then sent a diagnostic
bit pattern, which the on-board computer read as flight data. It swivelled the nozzles of the boosters and the main
engine to their full deflection, the angle of attack passed 20 degrees, the boosters began to separate, and the
self-destruct system did its job.

The board's recommendations included "Do not allow any sensor, such as the inertial reference system, to stop sending
best effort data", and asked to "identify all implicit assumptions made by the code and its justification documents
on the values of quantities provided by the equipment." That last one is the heart of it: the assumption that BH fits
in 16 bits was true for Ariane 4, written down, and invisible to the code.

## Design by contract

Bertrand Meyer's Eiffel has a name for writing such an assumption into the code: a contract. A routine states a
precondition, what must hold when it is called. A class states an invariant, what every one of its objects keeps. In
"Design by Contract: the lessons of Ariane" (IEEE Computer, January 1997), Jean-Marc Jézéquel and Meyer called the
loss a reuse error and showed what the reused routine should have said:

```eiffel
convert (horizontal_bias: INTEGER): INTEGER is
    require
        horizontal_bias <= Maximum_bias
    do
        ...
    ensure
        ...
    end
```

The requirement, they wrote, "was in fact stated in an obscure part of a document. But in the code itself it was
nowhere to be found!" Putting it in the code is the right lesson. Whether a contract checked while running would
have saved the flight is less sure, and their own answer is careful: "the answer is probably yes", above all because a
review would have checked every call against the precondition, while a test with the checks on "might have" caught
it.

The objections are well known, and they are about when the contract is checked. A run-time assertion costs processor
time, and the same budget, the 80% workload target that left three conversions unprotected, would have switched it
off in flight: Jézéquel and Meyer grant that with the checks kept on in flight, "given the performance constraints on
such a mission, however, this would probably not have been the case." Switched on, it would have raised the same kind
of error the conversion raised. And it fires only in a test that feeds it Ariane 5 data, which was never run. Eiffel's
own [tutorial](https://www.eiffel.org/doc/eiffel/ET-_Design_by_Contract_%28tm%29%2C_Assertions_and_Exceptions) advises that "when releasing the final version of a system, it is usually appropriate to turn off
assertion monitoring, or bring it down to the `require` level." A contract states the assumption. It does not make
anything check it, in the tests before launch or in the program that flies.

## The same assumption, proven when the program is built

In Draconyx the assumption is a rule on a type, written after `when`:

```draconyx
""" Tells whether `number` fits in 16 signed bits: from -32768 to 32767.

    * number: the number checked
"""
signed16_is_valid(number: Int) -> Bool:
    number >= -32768 and number <= 32767

""" A whole number that fits in 16 signed bits. """
type Signed16 extend Int when signed16_is_valid
```

`Signed16` is a refinement type: `Int` extended with a named rule. A `Signed16` is still an `Int`, and the rule holds
for every value of the type: it is the type's invariant, and it does the precondition's job too, since a function
that gives a `Signed16` can only give one that fits. What makes it more than a contract is when it is checked. A
value enters a `Signed16` only where the code proves the rule, and the proof is checked when the program is built, at
every target: `dev`, `test` and `release` alike. There is no monitoring level and no flag that turns it off.

Here is the Ariane 4 conversion, written the way it flew:

```draconyx
""" Converts the horizontal bias to the 16 bits the flight data carries.

    * bias: the horizontal bias the alignment computed
"""
horizontal_bias_16(bias: Float) -> Signed16:
    to_int(value = bias)        // does not build: nothing proves the value fits in 16 bits
```

It does not compile. `to_int` gives an `Int`, and nothing on the way proves that this `Int` is between -32768 and
32767. The argument that justified the missing protection, that the bias is physically limited, lived in a document;
the compiler cannot read it, so it asks for the proof in the code. The version that builds says what happens when the
bias does not fit:

```draconyx
""" The horizontal bias does not fit in 16 signed bits. """
type BiasOutOfRange extend Error

""" Gives `number` as a Signed16. Fails with BiasOutOfRange when it does not fit.

    * number: the number to fit
"""
fit_16_bits(number: Int) -> Signed16:
    if not signed16_is_valid(number):
        fail BiasOutOfRange(message = "The horizontal bias does not fit in 16 bits.")

    fitted: Signed16 = number
    fitted

""" Converts the horizontal bias to the 16 bits the flight data carries. Fails with BiasOutOfRange when it does not fit.

    * bias: the horizontal bias the alignment computed
"""
horizontal_bias_16(bias: Float) -> Signed16:
    match whole = checked_to_int?(value = bias):
        ok   -> ^fit_16_bits(whole)
        None -> fail BiasOutOfRange(message = "The horizontal bias is not a number in range.")
```

`checked_to_int?` gives `None` for a value that is not a number or lies far outside `Int`'s range, and `fit_16_bits`
checks the rule itself, which is the proof the compiler accepts. Now the failure is part of the function's contract,
and every caller must handle `BiasOutOfRange` or pass it on: the build refuses a call that does neither. On Ariane 5
that caller would have had to decide, in code a reviewer could read, what an alignment function that no longer
mattered should do with a bias too large to send. Sending the nearest value 16 bits can hold, the best effort data
the board asked for, is one more arm in a `match`.

It is worth being exact about what the compiler knows. It cannot know Ariane 5's trajectory, and it cannot tell
whether 32767 is the right value to send. What it knows is that nothing in the code proves the bias fits, and it
will not build the conversion until the code says what happens when it does not. Ariane 4's analysis was right for
Ariane 4, and the compiler would have refused the conversion on Ariane 4 all the same, because an argument in a
document is not a proof in the code. The out-of-range case would have been written then, and reused with the rest of
the software.

The cost is honest too. Where the value is known when the program is built, or arrives already typed `Signed16`, the
proof costs nothing while the program runs. Where it comes from a computation, as BH did, the proof is the check in
`fit_16_bits`: two comparisons, the kind of protection Ariane's engineers left off. Draconyx does not make
that check free. It makes it impossible to leave out on the strength of an argument the code cannot see, and it
leaves no switch that removes it from the program that flies.

## Laws: the reason becomes a claim the tools check

What Eiffel writes as a precondition or a class invariant is, in Draconyx, a refinement type like `Signed16`. A law is
a third thing: an equation between calls, which the tools check before the program runs, on inputs drawn from its
types every time the tests run, or for every input when the solver proves it.

The refinement type refuses the unprotected conversion. Laws go after the reason the conversion was thought safe, the
sentence in the justification document that the bias always fits. They add four things.

- **The assumption becomes a claim the tools check.** "For every bias this rocket can reach, the word is the bias
  itself" is a law, and its inputs are generated from its declared type on every test run. Nobody has to remember to
  feed a trajectory into a simulator, which is the test the inquiry found was never run.
- **The limit cannot stay unwritten.** Without a limit the claim is false, and the tests find that at once: the
  generator draws numbers up to 9e18, NaN and the infinities on purpose. To make the law pass, the author must write
  the rocket's limit in the source, as a type, under a name, beside the conversion.
- **Reuse meets that name.** For Ariane 5 the limit is one constant. Change it, and the tests fail on the ground with
  the number that does not fit, and a release build writes nothing.
- **The protection itself is proven.** The solver of the release build proves, for every one of the 2^64 integers,
  that the protected conversion keeps a count that fits.

Here is the conversion with the rocket's limit as a type, and the two laws. The numbers are for illustration: the
real constants of the flight software are not public.

```draconyx
""" How much horizontal bias one step of the 16-bit word stands for. """
const bias_per_step: Float = 0.5

""" The largest horizontal bias on this rocket's trajectory while the alignment runs. """
const max_horizontal_bias: Float = 12000.0      // from the trajectory data of Ariane 4

""" Tells whether this rocket can reach `bias` while the alignment runs.

    * bias: the horizontal bias checked
"""
flight_bias_is_valid(bias: Float) -> Bool:
    -max_horizontal_bias <= bias and bias <= max_horizontal_bias

""" A horizontal bias inside this rocket's trajectory data. """
type FlightBias extend Float when flight_bias_is_valid

""" Counts the steps of the 16-bit word that `bias` takes.

    * bias: a horizontal bias inside the trajectory data
"""
steps_of(bias: FlightBias) -> Int:
    to_int(bias / bias_per_step)

""" Turns a count of steps into the 16-bit word. Holds the word at the nearest limit when the count does not fit.

    * steps: the horizontal bias, counted in steps of the word
"""
word_of(steps: Int) -> Signed16:
    if not signed16_is_valid(steps):
        if steps > 0:
            return 32767

        return -32768

    word: Signed16 = steps              // proven: the rule's own check is just above
    word
example word_of(steps_of(max_horizontal_bias)) == steps_of(max_horizontal_bias)

// Law 1. On this rocket the protection never has to act: the word is the count itself.
law flight_bias_keeps_its_count(bias: FlightBias) checked:
    word_of(steps_of(bias)) == steps_of(bias)

// Law 2. The protection changes no count that fits, and the solver proves it for every Int.
law a_count_that_fits_is_kept(steps: Int) proven:
    signed16_is_valid(steps) ==> (word_of(steps) == steps)
```

`word_of` holds the word at its limit instead of stopping, which is the board's own recommendation: a sensor must not
stop sending its best data. Law 1 is the sentence that lived in the justification document. Law 2 is about the
protection. The `example` line under `word_of` runs one exact call, at the edge of the range.

With the limit of Ariane 4, `drx test` passes the example and Law 1, on 256 generated biases that are the same on
every machine, and `drx build --target release` proves Law 2. With the limit of Ariane 5, one line changes,
`max_horizontal_bias` becomes 60000.0 in the illustration, and `drx test` fails at the example, on the ground:

```
Witness violation: word_of, example at line 37
  word_of(steps_of(max_horizontal_bias)) = 32767
  expected                               = 120000
```

The word stops at 32767 where the bias needs 120000 steps, and the report names the constant to look at. A generated
bias that breaks Law 1 gives a report of the same shape: `Law violation`, the law's name, the bias, made as small as
the run can, and the two sides. If Law 2 were false, say with a wrong limit in `word_of`, the release build would stop
with `Proven law refuted` and the count that breaks it.

### Where laws do not help

- **A law checks the code against the limit that is written, not the limit against the rocket.** If nobody enters the
  limit of Ariane 5, the law still passes. Draconyx can make the limit a named constant; it cannot make someone type
  the right number. That was the real failure: nobody gave the unit the new trajectory.
- **The bias is floating point, so its law is tested, not proven.** The solver covers integers and booleans, not
  floating point. A test can miss: the values the toolchain builds inside a range stay close to the simplest one, so
  it may never reach the far end of a wide range. That is why the example pins the edge with one exact call, which
  cannot miss.
- **The type forces the out-of-range branch to exist; it does not write it.** If that branch fails and the failure
  reaches `main`, the unit stops, as it did in 1996. What keeps the rocket flying is a branch that holds the word at
  its limit.
- **No law knows that the alignment function had no purpose after lift-off.** It ran for about 40 seconds of flight
  because Ariane 4 required it.
- **No law touches the shutdown policy or the identical backup.** A proven law holds in both units, and so does a
  wrong assumption.
- **The diagnostic pattern read as flight data is a matter of types, not laws.** Two kinds of message need two types.

## Even with C inside

Code the compiler cannot check, such as a call into a C library or a read through a raw pointer, goes in a `trust:`
block. The programmer vouches for it, as with Rust's `unsafe`, but it unlocks only seven such
operations, every other check still runs inside it, and `drx audit trust` lists every trusted block in a program.

Flight software written in Draconyx needs no `trust:` at all: every value of a refinement type is proven when the
program is built, no rule is checked in flight, and nothing can be switched off. And when a program does use a C
library, Draconyx still guards it: a value that comes back from C is checked before the program can use it, unless
the program vouches for it, in writing, in a `trust:` block.

**The manifest says how far C reaches.** Each C library is declared in the manifest with a mode. A `sandboxed`
library, the default, runs in memory of its own. An `isolated` one runs in a process of its own, and each call is a
message to that process, copied in and copied back. A raw pointer never crosses into or out of a sandboxed or isolated
library: only an `in_process` one, which shares the program's memory, may pass one, inside `trust:`.

**What C returns is checked before it is trusted.** A call to a sandboxed or isolated library returns its value
`tainted`, and a tainted value reaches no plain position until the program checks it with `validate`, which runs the
type's rule. A bias from C becomes a `FlightBias` only through that rule.

**An address from C is read inside `trust:`, and the rule is checked at the read.** The program reads the value at an
address with `@`, written right before the pointer:

```draconyx
""" Gives where the alignment routine, written in C, stored the horizontal bias it computed last. """
extern "C" alignment_last_bias() -> Ptr<FlightBias>
    from library "alignment"

""" Gives the horizontal bias the alignment routine computed last. The library keeps the bias in place while the program runs, and nothing else writes it. """
last_bias() -> FlightBias:
    trust:
        @alignment_last_bias()      // the rule of FlightBias is checked as the bias is read
```

Outside `trust:`, the `@` does not build. A bias that breaks the rule stops the program at that line, as an `Int`
overflow does, instead of flying on with wrong data: the doc vouched for that memory, and a broken trust is a bug. A
bias that may really be out of range is declared `Ptr<Float>` instead and passed to `bias_word`, which never stops.
Each `in_process` call and each read through a pointer is a `trust:` block that `drx audit trust` lists, and an
assignment inside one still needs its proof.

Other languages leave this boundary open. In Rust, a `NonZeroU32` made from raw bytes that hold 0 is
[undefined behaviour](https://doc.rust-lang.org/reference/behavior-considered-undefined.html), and nothing checks it. In Ada, an invalid value from an unchecked conversion or an
imported function is erroneous to use, unless the program first tests it with the `Valid` [attribute](http://www.adaic.org/resources/add_content/standards/12rm/html/RM-13-9-2.html).

## How other languages handle it

| Language | Where a type's invariant is checked | Can the check be switched off? |
|---|---|---|
| **Draconyx** | **Proven when the program is built, at every assignment; checked while running only for a value read through a pointer in `trust:`.** | **No: every target gives the same answer.** |
| Eiffel | While running, when a creation ends and around every call to an exported routine from outside. | Yes: the default checks preconditions only, and final versions usually turn monitoring off. |
| Ada | While running: range checks, and predicates and `Type_Invariant` as the assertion policy says. | Yes: `pragma Suppress`, or `Assertion_Policy (Ignore)`. |
| SPARK | Proved before the program runs, by GNATprove. | The proof is a separate step, on a subset of Ada. |
| Rust | In the constructor the type's author writes, such as `NonZeroU32::new`. | `unsafe` code can skip the constructor, and the result is undefined behaviour. |
| Java, C++ | Only where the programmer writes a check, or an `assert`. | Yes: Java's `assert` runs only with `-ea`, and C++'s is removed under `NDEBUG`. |

Ada lets a program leave its checks out in general, with `pragma Suppress`, and the
[standard](http://www.adaic.org/resources/add_content/standards/12rm/html/RM-11-5.html) is plain about the cost: "If a given check has been suppressed, and the corresponding error situation occurs, the
execution of the program is erroneous." SPARK, the Ada subset built for proof, is the closest to Draconyx: its
prover shows before the program runs that no range check can fail.

## Why this is better

**The assumption lives in the code.** Ariane's 16-bit assumption was true for Ariane 4 and written in a document.
In Draconyx it is a type, and every value that enters the type carries its proof where a reader, a reviewer or a
model repairing the code can see it.

**A missing proof is a build error, not a flight.** Eiffel and Ada find a broken assumption in a run that reaches
it, if the checks are on. Draconyx refuses the line that cannot be proven before anything runs.

**The reason becomes a test.** The argument that BH always fits is a law, checked on every test run with inputs
from its types, so a reused limit that no longer holds fails on the ground, with the number.

**There is nothing to switch off.** One program gives one answer in every build. Code written in Draconyx runs no
rule checks in flight, and C inside the program is fenced by its mode, by tainted results and by the rule checked
where its memory is read.

Design by contract is one of the best ideas in programming, and Ariane 5 is the story that made its case. Draconyx
keeps the idea and moves the check to where nobody can turn it off: before launch.

## Sources

- J. L. Lions (chairman) and the Inquiry Board, "[Ariane 5 Flight 501 Failure: Report by the Inquiry Board](https://csapp.cs.cmu.edu/2e/docs/ariane5rep.html)",
  ESA and CNES, Paris, 19 July 1996. ESA's own page for it is
  [Ariane 501, Report by Board of Inquiry](https://sci.esa.int/web/cluster/-/38889-ariane-501-report-by-board-of-inquiry).
- Jean-Marc Jézéquel and Bertrand Meyer, "[Design by Contract: The Lessons of Ariane](https://archive.eiffel.com/doc/manuals/technology/contract/ariane/)", IEEE Computer,
  January 1997, in Eiffel Software's web copy.
- Wikipedia, "[Ariane flight V88](https://en.wikipedia.org/wiki/Ariane_flight_V88)", which cites Mark Dowson, "The Ariane 5 Software Failure", ACM SIGSOFT
  Software Engineering Notes, March 1997, for the figure of more than US$370 million.
- ESA, "[Flight 501 failure: first information](https://esa.int/Newsroom/Press_Releases/Flight_501_failure-_first_information)", press release, June 1996.
- ESA, "[Cluster's decade of discovery](https://esa.int/About_Us/ESA_history/Cluster_s_decade_of_discovery)", ESA history pages.
- ESA, "[Ariane 5](https://www.esa.int/Enabling_Support/Space_Transportation/Launch_vehicles/Ariane_5)", ESA space transportation pages.
- Eiffel Software, "[ET: Design by Contract (tm), Assertions and Exceptions](https://www.eiffel.org/doc/eiffel/ET-_Design_by_Contract_%28tm%29%2C_Assertions_and_Exceptions)", Eiffel tutorial, eiffel.org.
- ISO/IEC 8652:2012, the Ada Reference Manual: "[11.5 Suppressing Checks](http://www.adaic.org/resources/add_content/standards/12rm/html/RM-11-5.html)",
  "[13.9.2 The Valid Attribute](http://www.adaic.org/resources/add_content/standards/12rm/html/RM-13-9-2.html)",
  "[7.3.2 Type Invariants](http://www.adaic.org/resources/add_content/standards/12rm/html/RM-7-3-2.html)" and
  "[11.4.2 Pragmas Assert and Assertion_Policy](http://www.adaic.org/resources/add_content/standards/12rm/html/RM-11-4-2.html)",
  published by the Ada Information Clearinghouse.
- The Rust Project, "[Behavior considered undefined](https://doc.rust-lang.org/reference/behavior-considered-undefined.html)", The Rust Reference, doc.rust-lang.org.

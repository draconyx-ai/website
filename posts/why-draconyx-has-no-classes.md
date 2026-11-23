---
title: "Why Draconyx has no classes"
date: 2026-11-22
summary: "Should a sale save itself, or should a repository or a database save it? A class-based language makes every function answer a second question on top of which module it goes in: which object owns it. C++, Java and even Rust, through its impl blocks, ask it. Draconyx keeps structure in types and behaviour in free functions whose calls name every argument, so no argument is the owner and the question does not come up."
tags: design, types
draft: true
---

A shop sells a book, and the sale must be written down. Which line saves it?

```
sale.save()
repository.save(sale)
database.save(sale)
```

All three are reasonable, and each has its school. The first makes the sale responsible for itself, the second hands
the job to an object whose only work is storing sales, and the third lets the storage do it. None of them is wrong,
and a team can spend an afternoon choosing. This post is about why that afternoon exists, and why Draconyx is designed
so that it does not.

## Where does a method belong?

The question has a name: assigning responsibilities to objects. Craig Larman's book *Applying UML and Patterns* gave
it a set of guidelines, GRASP, the General Responsibility Assignment Software Patterns. There are nine of them, among
them Information Expert, give the work to the class that holds the information it needs, and Pure Fabrication,
invent a class that stands for no thing in the domain when no real class is a good home.

Applied to the sale, the two give different answers. Information Expert points at the sale: it holds the title and
the price. Pure Fabrication points at a repository: storing is not what a sale is about. Both are GRASP, and the
guidelines say how to weigh them, not which one wins.

Enterprise software has the same split under two well-known names. In Martin Fowler's *Patterns of Enterprise
Application Architecture*, an Active Record is "an object that wraps a row in a database table or view, encapsulates
the database access, and adds domain logic on that data". A Repository "mediates between the domain and data mapping
layers using a collection-like interface for accessing domain objects". Ruby on Rails chose the first: "Active Record
in Rails is an implementation of that pattern." Other codebases keep a repository beside plain domain objects. Both
work.

When the choice goes wrong, it has a name too. Fowler and Kent Beck's *Refactoring* lists Feature Envy among its code
smells: "A classic case of Feature Envy occurs when a function in one module spends more time communicating with
functions or data inside another module than it does within its own module." The usual cure is to move the
function, which in a class-based language means moving it to another class, and changing every call.

That is the deeper problem. Wherever code lives, someone decides which module or package it goes in. A class-based
language adds a second decision on top: which object owns the behaviour. GRASP, SOLID and Domain-Driven Design are
good advice for making it, but they are heuristics. They make the second decision better; they do not remove it.

## C++: a member, or not

C++ offers both homes:

```cpp
class Sale {
public:
    void save(Ledger& ledger) const;  // a member: the sale owns saving
};

void save(const Sale& sale, Ledger& ledger);  // a free function: nobody owns it
```

C++ deserves credit here: its own experts lean towards the free function. In "How Non-Member Functions Improve
Encapsulation", in 2000, Scott Meyers argued that when a function can be "implemented as either a member or as a
non-friend non-member", the non-member is the better choice: "That decision increases class encapsulation." Every
member is one more function that sees the class's private data. The C++ Core Guidelines say the same in rule
C.4: "Make a function a member only if it needs direct access to the representation of a class".

But the language still asks the question for every function, and the answer shows at every call: `sale.save(ledger)`
and `save(sale, ledger)` are written differently, so moving a function from one home to the other rewrites its
callers.

## Java: everything in a class

Java answers by leaving no choice: a source file holds classes and interfaces, and a function exists only inside one.
A function that belongs to no object still needs a class to live in:

```java
final class Sales {
    private Sales() {}

    static void save(Sale sale, Ledger ledger) {
        ledger.add(sale.title() + ": " + sale.price());
    }
}
```

The standard library is full of such classes. The documentation of `java.util.Collections` opens: "This class consists
exclusively of static methods that operate on or return collections." `java.util.Arrays` is another. And the two
homes can end up holding the same operation: `List` has its own `sort` method, and of `Collections.sort` the
documentation says, "This implementation defers to the List.sort(Comparator) method using the specified list and a
null comparator." A reader who wants to sort a list must know both places.

Java's rule is simple and every method is easy to find once you know its class. The cost is the classes that stand for
nothing, and the question of which class, which is still there.

## Rust: no classes, the same question

Rust has no classes, and it gets a lot right. A `struct` holds data, behaviour is written apart from it in `impl`
blocks, and traits work much like Haskell's type classes. Free functions are allowed too. But a method is still
written inside an `impl` block for one type, and so the question returns:

```rust
struct Sale {
    title: String,
    price: u32,
}

struct Ledger {
    lines: Vec<String>,
}

// The sale owns saving...
impl Sale {
    fn save(&self, ledger: &mut Ledger) {
        ledger.lines.push(format!("{}: {}", self.title, self.price));
    }
}

// ...or the ledger does.
impl Ledger {
    fn save(&mut self, sale: &Sale) {
        self.lines.push(format!("{}: {}", sale.title, sale.price));
    }
}
```

`sale.save(&mut ledger)` or `ledger.save(&sale)`: one of the two types has to be the home. The Rust Reference adds a
rule about where that home may be written. An inherent `impl`, the plain kind above, must be in the crate that defines
the type: "An implementing type must be defined within the same crate as the original type definition." A trait
`impl` has the orphan rule: "a trait implementation is only allowed if either the trait or at least one of the types
in the implementation is defined in the current crate." So this is refused, with error E0117, because neither
`Display` nor `Vec` is defined here:

```rust
use std::fmt;

impl fmt::Display for Vec<Sale> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{} sales", self.len())
    }
}
```

The orphan rule exists for a good reason: two crates must not give the same type two different `Display`s. But it
shows that in Rust behaviour still belongs to a type, and a crate, in the way a method belongs to a class.

## Others, briefly

Other languages have taken parts of this apart. Kotlin's extension functions let anyone write `fun Sale.save(...)`,
which is called like a member, but "extensions don't modify the classes or interfaces they extend": the call looks as
if the sale owned it, and the question of the receiver is only moved. Go has methods with a receiver, and its specification says: "A receiver
base type cannot be a pointer or interface type and it must be declared in the same package as the method." Its
interfaces, though, need no declaration: a type satisfies one by having its methods. Haskell keeps data declarations
free of functions, and joins them with class and instance declarations written separately. Common Lisp's CLOS and
Julia go furthest: a method belongs to a generic function, not to a class, and Julia calls choosing it from "all of a
function's arguments" multiple dispatch. Philip Wadler's 1998 note "The Expression Problem", "a new name for an old
problem", is about the same tension, seen from the other side: adding new cases and new functions without rewriting
what exists.

## Draconyx: types hold structure, functions hold behaviour

Draconyx takes the separation all the way. A `type` has fields and nothing else. There are no classes, no methods and
no `impl` blocks, and the dot reads a field or names a module, never calls a function. Every function is a free
function in a module, and a call names its arguments:

```draconyx
module sales

""" A sale the shop has made. """
type Sale:
    title: String
    price: Int

""" The day's sales, one line each. """
type Ledger:
    lines: List<String>

""" The sales of every day, one row each. """
type Archive:
    rows: List<String>

""" A place that keeps sales. """
concept Store:
    save(sale: Sale, borrow store: T) -> None

""" Writes `sale` as the last line of the ledger.

    * sale: the sale to write
    * store: the ledger written
"""
save(sale: Sale, borrow store: Ledger) -> None:
    push(list = borrow store.lines, item = "{sale.title}: {sale.price}")

""" Writes `sale` as a new row of the archive.

    * sale: the sale to write
    * store: the archive written
"""
save(sale: Sale, borrow store: Archive) -> None:
    push(list = borrow store.rows, item = "{sale.title},{sale.price}")

""" Saves every sale of the day in `store`.

    * sales: the day's sales
    * store: where the sales are kept
"""
close_day(sales: List<Sale>, borrow store: any T) -> None:
    for sale in sales:
        save(sale, borrow store)

main() -> None:
    sales = [Sale(title = "Dune", price = 12), Sale(title = "Emma", price = 9)]
    ledger = Ledger(lines = [])
    archive = Archive(rows = [])

    close_day(sales, borrow ledger)
    close_day(sales, borrow archive)
```

Five things make the owner question disappear.

**A type is structure only.** `Sale`, `Ledger` and `Archive` say what they hold. Nothing in them says what can be done
with them, so there is no inside of a type for a function to be put in.

**A function is free.** `save` is written in the module `sales`, next to the types it reads, and could as well be
written in another module. The only placement question is the one every language has: which module.

**A type joins a concept by having its functions.** `Ledger` and `Archive` are both `Store`s because a `save` is
written for each. Neither type says so: there is no `implements`, no `impl Store for Ledger` and no instance
declaration, so behaviour can be added to a type without touching it. Go's interfaces work this way for methods;
Draconyx does it for free functions.

**A call names its arguments.** `save(sale, borrow store)` gives a sale and a store, side by side. Neither is the
receiver and neither comes first in a way that means anything, so there is nothing to argue about between
`sale.save(store)` and `store.save(sale)`: in Draconyx neither can be written.

**Functions of one name live side by side.** A function's signature is its name, its parameter names and types, their
ownership and its return type, so the two `save`s are two functions, and each call picks by what it gives: here by the
type of the store. CLOS and Julia choose a method from all the arguments too; in Draconyx the call also names every
argument. Ownership is spelled at the call as well: an argument is
read-only unless the call says `borrow`, to change it, or `take`, to consume it, so `close_day(sales, borrow ledger)`
shows on its own line that the ledger changes and the sales do not.

## What this does not solve

It removes one decision, not design. `save` still goes in some module, and choosing between `sales` and `storage` is
a real choice, made the same way as in any language with modules. Which layer may talk to the database, what a module
exports and where a system's boundaries run still need thought, and no language feature does that thinking.

Feature Envy does not go away either. Fowler and Beck's definition speaks of modules, not classes, and a function that
reads more of another module than of its own is still in the wrong place. In Draconyx, moving it means moving it to
another module: the `use` lines that bring it in change, and every call stays as it was.

## Why Draconyx does it better

**One decision instead of two.** Where a function goes is a question about modules, and only about modules. There is
no second question about which object owns it, so no afternoon is spent on `sale.save()` against
`repository.save(sale)`.

**Moving a function does not change its calls.** A call is `save(sale, borrow store)` wherever `save` lives, so a
function that turns out to be in the wrong module moves with a change to the `use` lines that bring it in, and none
to its calls. Turning a C++ member into a
free function, or a Rust method from one `impl` to another, changes every call.

**Adding behaviour to a type is ordinary code.** A function for a type another module defines is a function like any
other, written where it is needed, with no wrapper class, no extension syntax and no `impl` block to place.

**A call says everything.** The call names each argument and spells what happens to it, so a reader knows from one
line what goes in, what changes and what is consumed, without looking up which argument is the receiver.

**A model has one place to look.** A model writing Draconyx does not guess which class owns a method, whether it is a
member or a free function, or which extension is in scope. It looks for a function by its name and the types it
takes, and the toolchain's outline lists each function with its signature. The less a language leaves to convention,
the less a model has to guess, and a guess is where generated code goes wrong.

Draconyx did not invent these parts: free functions are older than objects, CLOS and Julia separated methods from
classes, Haskell kept its data declarations free of functions, and Go let a type satisfy an interface without saying
so. What Draconyx adds is having all of them at once, with named arguments and ownership spelled at every call, so a
type holds its structure, a function holds its behaviour, and nothing has to decide who owns what.

## Sources

- Craig Larman, *[Applying UML and Patterns: An Introduction to Object-Oriented Analysis and Design and Iterative Development](https://informit.com/title/0131489062)*,
  3rd edition, Pearson, 2004.
- Wikipedia, "[GRASP (object-oriented design)](https://en.wikipedia.org/wiki/GRASP_(object-oriented_design))", for the nine patterns and their
  source in Larman's book.
- Martin Fowler, *[Patterns of Enterprise Application Architecture](https://martinfowler.com/books/eaa.html)*, 2002, and its catalog
  entries "[Active Record](https://martinfowler.com/eaaCatalog/activeRecord.html)" and "[Repository](https://martinfowler.com/eaaCatalog/repository.html)".
- Ruby on Rails Guides, "[Active Record Basics](https://guides.rubyonrails.org/active_record_basics.html)".
- Martin Fowler with Kent Beck, *[Refactoring: Improving the Design of Existing Code](https://martinfowler.com/books/refactoring.html)*, 2nd edition, 2018; the
  chapter on code smells, with "[Feature Envy](https://www.informit.com/articles/article.aspx?p=2952392&seqNum=9)", is excerpted on InformIT.
- Scott Meyers, "[How Non-Member Functions Improve Encapsulation](https://jacobfilipp.com/DrDobbs/articles/CUJ/2000/0002/meyers/meyers.htm)", C/C++ Users Journal,
  February 2000, in an archived copy of the Dr. Dobb's reprint.
- "[C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#rc-member)", rule C.4, on isocpp.github.io.
- Oracle, *The Java Language Specification*, Java SE 21, "[7.6 Top Level Class and Interface Declarations](https://docs.oracle.com/javase/specs/jls/se21/html/jls-7.html#jls-7.6)".
- Oracle, Java SE 21 API, "[Collections](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Collections.html)",
  "[Arrays](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Arrays.html)" and
  "[List](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html)".
- The Rust Project, "[Implementations](https://doc.rust-lang.org/reference/items/implementations.html)", The Rust Reference, with its
  "[orphan rules](https://doc.rust-lang.org/reference/items/implementations.html#orphan-rules)", and "[E0117](https://doc.rust-lang.org/error_codes/E0117.html)" in the
  Rust error code index.
- "[Extensions](https://kotlinlang.org/docs/extensions.html)", Kotlin documentation, kotlinlang.org.
- The Go Authors, *The Go Programming Language Specification*, "[Method declarations](https://go.dev/ref/spec#Method_declarations)" and
  "[Interface types](https://go.dev/ref/spec#Interface_types)".
- *[Haskell 2010 Language Report](https://www.haskell.org/onlinereport/haskell2010/haskellch4.html)*, chapter 4, "Declarations and
  Bindings", sections 4.3.1 and 4.3.2 on class and instance declarations.
- The Julia Project, "[Methods](https://docs.julialang.org/en/v1/manual/methods/)", Julia manual.
- LispWorks, Common Lisp HyperSpec, "[Macro DEFGENERIC](http://www.lispworks.com/documentation/HyperSpec/Body/m_defgen.htm)".
- Philip Wadler, "[The Expression Problem](https://homepages.inf.ed.ac.uk/wadler/papers/expression/expression.txt)", 12 November 1998.

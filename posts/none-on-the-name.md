---
title: "Nothing to hide: how Draconyx handles a missing value"
date: 2026-11-16
summary: "Java marks a missing value with null or an Optional, C++ with a null pointer or a std::optional, Rust with an Option in the type. Draconyx puts it on the name, where every call shows it and every caller has to deal with it."
tags: design, types
---

Every program meets a value that might not be there: a name with no age on record, a user with no nickname, a
search that finds nothing. How a language lets you say "there may be no value" decides two things. Can a reader see
it? And can a writer forget it?

Take one small function in four languages: look up a person's age, which may be unknown, and use it.

## Java: any reference may be null

```java
Integer findAge(String name) {
    return name.equals("ada") ? 36 : null;
}

int next = findAge("bob") + 1;   // compiles; throws NullPointerException
```

Nothing in `Integer findAge(String name)` says the answer can be missing. Any reference in Java can be `null`, so the
compiler cannot tell this method from one that always answers, and the mistake waits for run time. Tony Hoare, who
introduced the null reference in 1965, later called it his "billion-dollar mistake".

Java 8 added `Optional<T>`, which says it in the signature:

```java
Optional<Integer> findAge(String name) {
    return name.equals("ada") ? Optional.of(36) : Optional.empty();
}

int age = findAge("bob").orElse(0); // 0
int risky = findAge("bob").get();  // compiles; throws NoSuchElementException
```

It is a real improvement, but an optional one. It is a library class that a method may use or not, much of the
platform, `Map.get` among it, still returns `null`, `get()` throws when it is empty, and an `Optional` is itself a
reference, so the compiler accepts `Optional<Integer> age = null`, which the `Optional` documentation forbids only in
prose.

## C++: a null pointer, or an optional you can still misread

C++ has two answers. The old one is a pointer that may be null:

```cpp
const int* find_age(const std::string& name);  // nullptr when unknown

if (const int* age = find_age("ada")) use(*age); // checked, then read
int next = *find_age("bob") + 1;  // compiles; undefined behaviour
```

The newer one, since C++17, is `std::optional<T>`:

```cpp
std::optional<int> find_age(const std::string& name) {
    if (name == "ada") return 36;
    return std::nullopt;
}

int age = find_age("bob").value_or(0);    // 0
int checked = find_age("bob").value();    // throws std::bad_optional_access
if (auto age = find_age("ada")) use(*age);   // checked, then read
int risky = *find_age("bob");             // compiles; undefined behaviour
```

The optional says "maybe" in the signature, which is better than a pointer. But reading the value directly has two
spellings with different rules. `.value()` checks and throws. `*` does not check at all: on an empty optional the
behaviour is undefined, and Clang accepts it without a warning, even with `-Wall -Wextra`. C++26 lets a standard
library be built hardened, which turns this into a stop, but only when hardening is switched on. The check and the
read are separate steps, nothing ties the `*` to the `if`, and the shorter spelling is the unsafe one.

## Rust: in the type, checked, with a way out

Rust gets the important part right. Safe Rust has no null references: a value that may be missing has the type
`Option<T>`, and the compiler will not let you use it as a `T`.

```rust
fn find_age(name: &str) -> Option<u32> {
    if name == "ada" { Some(36) } else { None }
}

let age = find_age("bob").unwrap_or(0);  // 0
match find_age("ada") {
    Some(years) => println!("{years} years"),
    None => println!("age unknown"),
}
if let Some(years) = find_age("ada") { println!("{years}") }

fn next_age(name: &str) -> Option<u32> {
    let years = find_age(name)?;    // no age: return None from here
    Some(years + 1)
}

let next = find_age("bob") + 1;
// error[E0369]: cannot add `{integer}` to `Option<u32>`
let risky = find_age("bob").unwrap();    // compiles; panics at run time
```

Inside a function that itself returns an `Option`, `?` passes a missing value up to the caller: a short, visible mark
on the call, though one that hands the problem on rather than settling it.

Two things remain. The "maybe" lives in the type, not in the name: `find_age("ada")` looks like any other call, and
you learn that the answer can be missing from the signature or from the code that handles it. Because an `Option` is
an ordinary value, that handling can be on the same line, with `?`, `unwrap_or` or `match`, or it can come much later,
after the value has been stored or passed on. The type keeps it honest, but a reader of the call cannot tell which.
And there is a way out: `unwrap()` or `expect()` turns "maybe" into "surely", and a wrong guess stops the program with
a panic.

## Draconyx: on the name

In Draconyx the mark is a `?` on the function's name:

```draconyx
""" Looks up the age of `name`, which may be unknown.

    * name: the name of the person
"""
find_age?(name: String) -> Int:
    if name == "ada":
        return 36

    return None
```

The result type is `Int`, the type of the value the function gives when it has one. When it has none, it returns
`None`. There is no wrapper to build and none to take apart.

The `?` is part of the name, so it is written at every call, and the caller handles the missing case right there.
With a fallback, `??`, whose right-hand side runs only when there is no value:

```draconyx
age = find_age?(name = "ada") ?? 0
```

Or with a `match` that covers both cases. The head names the result, and inside the `ok` arm `age` holds the value:

```draconyx
""" Describes in words how old `name` is.

    * name: the name of the person
"""
describe(name: String) -> String:
    match age = find_age?(name):
        ok   -> "{age} years"
        None -> "age unknown"
```

The checker refuses:

- A call written without its `?`: `find_age(name = "ada")`.
- A result used as a plain `Int`, with neither `??` nor `match`: `next = find_age?(name = "ada") + 1` in a function
  that gives a plain `Int`.
- A `match` with no `None` arm.
- `None` stored in a local, passed to a function parameter or compared.

A field that may be absent takes the same mark, on its name:

```draconyx
""" A user of the shop. """
type User:
    name: String
    nickname?: String
    age?: Int
```

Left out of a construction, a `?` field starts as `None`, so it needs no default.

It is read like a call, with the `?` at every read: `user.nickname? ?? "none"`, or
`match nick = user.nickname?:`. A bare `user.nickname` is refused. A value goes in without the mark:
`User(name = "ada", nickname = "Ada")`, and `ada.nickname = None` empties the field. A `?` call or read may also go, as
it is, into a `?` field: `User(name = "bob", age = find_age?(name = "bob"))` holds `None` when there is no value.
Into a plain field it is refused.

And the word is the same wherever the language means "no value". A function that gives nothing says so in its
result type:

```draconyx
""" Stops the task if `amount` is negative.

    * amount: the amount to check
"""
check_amount(amount: Int) -> None:
    assert(amount >= 0)
```

## Why this is better

**You can see it at every call.** In Java the call `findAge("bob")` does not tell you an answer may be missing, and
in C++ and Rust neither does `find_age("bob")`: you learn it from the signature, or from the code that handles the
result.
In Draconyx the call itself says `find_age?`. Whoever reads the line, a person in review or a model repairing it,
sees the "maybe" where it matters, without opening another file.

**It is handled where it is seen.** A local always holds a value, and so does a parameter. A call's missing value
cannot be stored in a local or passed as an argument to a function, to fail somewhere far from its cause. It is settled on
the line that produced it, with `??` or `match`, or kept in a `?` field, whose every read carries the mark again.
Wherever a value may be missing, the line in front of you says so.

**There is no word for "assume it is there".** Java's `get()` and Rust's `unwrap()` turn "maybe" into "surely" with
one word and fail at run time when the guess is wrong. C++'s `*` does not even fail: on an empty optional the
behaviour is undefined. Draconyx has no such word. A program that really should stop says so with the same fallback
as every other call, `find_age?(name = "ada") ?? panic("no age for ada")`, much as Rust's `expect("...")` does; here
there is no shorter spelling beside it, so the crash always sits in plain sight. The program does not compile until every call has said what happens when there is no value.

**There is nothing to unwrap.** `find_age?` gives an `Int`, not a box that holds an `Int`. There is no `Some(36)` to
build, no `.value()` to read and no nested "maybe of a maybe" to untangle.

**One word for one idea.** `None` is the only word for "no value". As a result type it says a function never gives
one, and as a value it says a `?` function or field has none this time. The `?` on the name tells you which.

Rust, like ML and Haskell before it, shows that a compiler can make a missing value impossible to ignore. Draconyx keeps that guarantee and moves the
mark from the type to the name, where every reader sees it and no caller can skip it. That is all the syntax does,
and it hides nothing.

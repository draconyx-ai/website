---
title: "None, on the name: how Draconyx handles a missing value"
date: 2026-11-16
summary: "A design that is decided but not built yet: a function that may give no value says so in its name, and every call decides on the spot what happens when there is none."
tags: design, types
draft: true
---

> [!WARNING]
> **Not built yet.** This post describes a design that is decided but not yet in the compiler. Today's `drx`
> rejects every sample below except the last. A few details are still open, and the post says which.

Every program meets a value that might not be there: a name with no age on record, a user with no nickname, a
search that finds nothing. Draconyx has no null. A value that may be missing is marked where it is declared, on its
name, and every place that uses it has to say what happens when it is not there.

## A function that may give no value

The mark is a `?` on the function's name, never on a type:

> [!WARNING]
> Not in the compiler yet: today's `drx` rejects this sample.

```draconyx
find_age?(name: String) -> Int:
    """The age of `name`, if it is known."""
    if name == "ada":
        return 36
    return None
```

The result type is the type of the value the function gives when it gives one: here, an `Int`. When it has a
value, it returns it as any function does. When it has none, it returns `None`. A function marked `?` must declare a
result type.

## Every call says what happens

The `?` is part of the name, so it is written at every call, `find_age?(name = "ada")`, and a call that leaves it
out is an error. The caller then handles the missing case on the spot, in one of two ways.

With a fallback, `??`. The right-hand side runs only when there is no value:

> [!WARNING]
> Not in the compiler yet: today's `drx` rejects this sample.

```draconyx
age = find_age?(name = "ada") ?? 0
```

Or with a `match` that covers both cases. The head names the result, and the arms are `ok` and `None`. Inside the
`ok` arm, `age` holds the value:

> [!WARNING]
> Not in the compiler yet: today's `drx` rejects this sample.

```draconyx
describe(name: String) -> String:
    """How old `name` is, in words."""
    match age = find_age?(name = name):
        ok   -> "{age} years"
        None -> "age unknown"
```

A result used as a plain `Int`, with neither `??` nor `match`, is refused at compile time,
and so is a `match` with no `None` arm. A missing value cannot be forgotten, because the program does not compile
until every call has said what to do about it.

> [!WARNING]
> Not in the compiler yet: today's `drx` rejects this sample.

```draconyx
next_year = find_age?(name = "ada") + 1   // will be refused: no ?? and no match
```

## A field that may be absent

A struct field takes the same mark, on its name, with `None` as its default:

> [!WARNING]
> Not in the compiler yet: today's `drx` rejects this sample.

```draconyx
struct User:
    """A user of the shop."""
    name: String
    nickname?: String = None
```

How a program reads and writes such a field, and whether the default must be written, are still being decided.

## One word for "no value"

A local always holds a value, and so does a parameter. `None` is the absent value of a `?` function or field, and it
is also the result type of a function that gives nothing:

> [!WARNING]
> Already built: today's `drx` accepts this sample. The rest of this post is not in the compiler yet.

```draconyx
check_amount(amount: Int) -> None:
    """Stops the task if `amount` is negative."""
    assert(amount >= 0)
```

Every function writes its result type, so `-> None` is not optional. One word means "no value" wherever the
language needs to say it.

## What the checker will refuse

- A `?` call whose result is used with neither `??` nor `match`.
- A call written without the `?` its function has, and a `?` on a call to a function that has none.
- A `match` on a `?` call with no `None` arm.
- `None` anywhere but as the absent value or as a type: stored in a local, passed as an argument, compared.
- A `?` on a type, such as `Int?`, or on a local.

## Still open

- Reading, writing and building a `?` field, and whether its default must be written.
- A missing value passed up through a chain of `?` functions without being handled.
- Which standard-library functions take the `?` form.
- How a missing value meets generators and channel receives.

When the design reaches the compiler, the [changelog](/changelog/) will say so.

---
title: Hello, blog
date: 2026-11-15
summary: Draconyx now has a blog, for the longer story behind the language.
tags: news
draft: true
---

Draconyx is a programming language designed for its AI author. So far this site has told its story in a few pages:
the [home page](/), the [changelog](/changelog/) and [what six AI models said about the spec](/what-models-think/).
This blog is for the parts that need more room than a card on the home page.

## What to expect

- Articles that take one mechanism and look at it closely: what the spec says, what ships today, and what is only
  specified.
- The thinking behind the changes that the [changelog](/changelog/) lists by date.
- Code, wherever it helps.

## Where it starts

The language starts from how a model actually writes code: it generates, observes and repairs, hundreds of times,
unattended. In the spec's words, what that author needs is

> not leniency but a fast, precise, machine-readable verdict.

Here is one such verdict, from the home page. The match below forgets a case, and the checker says which one:

```draconyx
enum PaymentState:
    Pending
    Authorized(Money)
    Captured(Money)
    Refunded(reason: String, amount: Money)

def label(payment_state: PaymentState) -> String:
    match payment_state:
        Pending       -> "pending"
        Authorized(_) -> "authorized"
        Captured(_)   -> "captured"
// error[AX0601]: non-exhaustive match: missing `Refunded(_, _)`
```

To follow along, subscribe to the [Atom feed](/blog/feed.xml).

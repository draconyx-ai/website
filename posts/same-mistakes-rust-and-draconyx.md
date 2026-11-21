---
title: "The same mistakes, in Rust and in Draconyx"
date: 2026-11-20
summary: "Six everyday mistakes, each made once in Rust and once in Draconyx, with what each compiler says about them."
tags: diagnostics, tooling
---

<style>
.vs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:22px 26px;
width:max(100%,min(1088px,calc(100vw - 32px)));margin:30px 0 34px 50%;transform:translateX(-50%)}
.vs figure{margin:0;min-width:0}
.vs .lang{margin:0 0 10px;font-size:14px;font-weight:750;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.vs .cap{margin:14px 0 8px;font-size:14px;font-weight:600;color:var(--muted)}
.post .vs pre{margin:0;font-size:13px}
.post pre.term{background:#1e1e1e;color:#d4d4d4;font-size:12.5px;line-height:1.45;padding:16px 18px}
.post pre.json{max-height:560px;overflow:auto}
.post pre.term .bar{display:block;border-left:3px solid;padding-left:calc(2ch - 3px)}
</style>

Every programmer makes the same few mistakes every day: a name typed wrong, a value of the wrong type, a case
left out. What matters is what the compiler says next, and how quickly it gets you, or the model writing the code,
back on track.

Here are six such mistakes, each written once in Rust and once in Draconyx. First (on the left, on a wide
screen) is Rust's compiler, rustc 1.98.0, exactly as it prints in a terminal, run with the command shown. Then
(on the right) is drx, the Draconyx toolchain.

drx reports each problem as one block. A bar in the problem's colour runs down its left side, and a badge says
what kind it is: an error, a warning, a note or a suggestion. Then come the line, with the spot marked; what is
wrong, in a sentence that uses your own names; why; and what to do. The reference code comes last, in grey,
for whoever wants more. One line at the end counts the problems and says whether the package was built.

## 1. A misspelled name

A parameter called `quantity`, used as `quantitty`.

<div class="vs">
<figure>
<p class="lang">Rust</p>
<pre tabindex="0" role="region" aria-label="Rust: shop.rs"><code><span class="t-sd">/// Works out what `quantity` items at `price` cost.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">total</span><span class="t-p">(</span><span class="t-n">price</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">quantity</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-p">)</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-n">price</span><span class="t-w"> </span><span class="t-o">*</span><span class="t-w"> </span><span class="t-n">quantitty</span>
<span class="t-p">}</span></code></pre>
<p class="cap">rustc says:</p>
<pre class="term" tabindex="0" role="region" aria-label="rustc&#x27;s output"><code><span style="color:#8a8a8a">$</span> rustc --edition 2024 --crate-type lib shop.rs
<span></span>
<span style="color:#f14c4c;font-weight:700">error[E0425]</span><span style="font-weight:700">: cannot find value `quantitty` in this scope</span>
 <span style="color:#3b8eea;font-weight:700">--&gt; </span>shop.rs:3:13
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700">3</span> <span style="color:#3b8eea;font-weight:700">|</span>     price * quantitty
  <span style="color:#3b8eea;font-weight:700">|</span>             <span style="color:#f14c4c;font-weight:700">^^^^^^^^^</span>
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#29b8db;font-weight:700">help</span>: a local variable with a similar name exists
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700">3</span> <span style="color:#f14c4c">- </span>    price * <span style="color:#f14c4c">quantitty</span>
<span style="color:#3b8eea;font-weight:700">3</span> <span style="color:#23d18b">+ </span>    price * <span style="color:#23d18b">quantity</span>
  <span style="color:#3b8eea;font-weight:700">|</span>
<span></span>
<span style="color:#f14c4c;font-weight:700">error</span><span style="font-weight:700">: aborting due to 1 previous error</span>
<span></span>
<span style="font-weight:700">For more information about this error, try `rustc --explain E0425`.</span></code></pre>
</figure>
<figure>
<p class="lang">Draconyx</p>
<pre tabindex="0" role="region" aria-label="Draconyx: src/shop.ax"><code><span class="k">module</span> shop
<span></span>
<span class="k">@doc</span> <span class="s">"""Works out what `quantity` items at `price` cost.</span>
  * price - the price of one item
  * quantity - how many items are bought
<span class="s">""</span>"
total(price: Int, quantity: Int) -&gt; Int:
    price * quantitty</code></pre>
<p class="cap">drx says:</p>
<pre class="term" tabindex="0" role="region" aria-label="drx&#x27;s output"><code><span style="color:#8a8a8a">$</span> drx check shop
<span></span>
<span></span><span class="bar" style="border-left-color:#cd3131"><span style="color:#ffffff;background:#cd3131;font-weight:700"> ERROR </span>  <span style="color:#ffffff;font-weight:700">src/shop.ax, line 8</span>
<span></span>
    <span style="color:#afd7ff">price</span> * <span style="color:#afd7ff">quantitty</span>
            <span style="color:#cd3131">^^^^^^^^^</span>
<span></span>
<span style="color:#afd7ff">quantitty</span> is not a name this function knows.
<span></span>
<span style="color:#afd7ff">total</span> has the parameters <span style="color:#afd7ff">price</span> and <span style="color:#afd7ff">quantity</span>, and nothing
else in reach is called <span style="color:#afd7ff">quantitty</span>.
<span></span>
Did you mean <span style="color:#afd7ff">quantity</span>, or <span style="color:#afd7ff">quantize</span> from <span style="color:#afd7ff">std</span>.<span style="color:#afd7ff">tensor</span>?
<span></span>
<span style="color:#8a8a8a">(AX0234. For more, run: drx explain AX0234)</span></span><span></span>
<span></span>
<span style="color:#cd3131;font-weight:700">1 error</span> in 1 file. The package was not built.</code></pre>
</figure>
</div>

Both compilers find the name and suggest `quantity`; drx also names a function of that spelling in the
standard library.

## 2. A value of the wrong type

A price written as text where a number is expected.

<div class="vs">
<figure>
<p class="lang">Rust</p>
<pre tabindex="0" role="region" aria-label="Rust: shop.rs"><code><span class="t-sd">/// Works out what `quantity` items at `price` cost.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">total</span><span class="t-p">(</span><span class="t-n">price</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">quantity</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-p">)</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-n">price</span><span class="t-w"> </span><span class="t-o">*</span><span class="t-w"> </span><span class="t-n">quantity</span>
<span class="t-p">}</span>
<span></span>
<span class="t-sd">/// Works out the cost of three items at 12.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">checkout</span><span class="t-p">()</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-n">total</span><span class="t-p">(</span><span class="t-s">"12"</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">3</span><span class="t-p">)</span>
<span class="t-p">}</span></code></pre>
<p class="cap">rustc says:</p>
<pre class="term" tabindex="0" role="region" aria-label="rustc&#x27;s output"><code><span style="color:#8a8a8a">$</span> rustc --edition 2024 --crate-type lib shop.rs
<span></span>
<span style="color:#f14c4c;font-weight:700">error[E0308]</span><span style="font-weight:700">: mismatched types</span>
 <span style="color:#3b8eea;font-weight:700">--&gt; </span>shop.rs:8:11
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700">8</span> <span style="color:#3b8eea;font-weight:700">|</span>     total("12", 3)
  <span style="color:#3b8eea;font-weight:700">|</span>     <span style="color:#3b8eea;font-weight:700">-----</span> <span style="color:#f14c4c;font-weight:700">^^^^</span> <span style="color:#f14c4c;font-weight:700">expected `u32`, found `&amp;str`</span>
  <span style="color:#3b8eea;font-weight:700">|</span>     <span style="color:#3b8eea;font-weight:700">|</span>
  <span style="color:#3b8eea;font-weight:700">|</span>     <span style="color:#3b8eea;font-weight:700">arguments to this function are incorrect</span>
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#23d18b;font-weight:700">note</span>: function defined here
 <span style="color:#3b8eea;font-weight:700">--&gt; </span>shop.rs:2:8
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700">2</span> <span style="color:#3b8eea;font-weight:700">|</span> pub fn total(price: u32, quantity: u32) -&gt; u32 {
  <span style="color:#3b8eea;font-weight:700">|</span>        <span style="color:#23d18b;font-weight:700">^^^^^</span> <span style="color:#3b8eea;font-weight:700">----------</span>
<span></span>
<span style="color:#f14c4c;font-weight:700">error</span><span style="font-weight:700">: aborting due to 1 previous error</span>
<span></span>
<span style="font-weight:700">For more information about this error, try `rustc --explain E0308`.</span></code></pre>
</figure>
<figure>
<p class="lang">Draconyx</p>
<pre tabindex="0" role="region" aria-label="Draconyx: src/shop.ax"><code><span class="k">module</span> shop
<span></span>
<span class="k">@doc</span> <span class="s">"""Works out what `quantity` items at `price` cost.</span>
  * price - the price of one item
  * quantity - how many items are bought
<span class="s">""</span>"
total(price: Int, quantity: Int) -&gt; Int:
    price * quantity
<span></span>
<span class="k">@doc</span> <span class="s">"""Works out the cost of three items at 12."""</span>
checkout() -&gt; Int:
    total(price = <span class="s">"12"</span>, quantity = 3)</code></pre>
<p class="cap">drx says:</p>
<pre class="term" tabindex="0" role="region" aria-label="drx&#x27;s output"><code><span style="color:#8a8a8a">$</span> drx check shop
<span></span>
<span></span><span class="bar" style="border-left-color:#cd3131"><span style="color:#ffffff;background:#cd3131;font-weight:700"> ERROR </span>  <span style="color:#ffffff;font-weight:700">src/shop.ax, line 12</span>
<span></span>
    <span style="color:#5fafff">total</span>(<span style="color:#afd7ff">price</span> = <span style="color:#87d787">"12"</span>, <span style="color:#afd7ff">quantity</span> = <span style="color:#ff875f">3</span>)
                  <span style="color:#cd3131">^^^^</span>
<span></span>
<span style="color:#afd7ff">price</span> takes an <span style="color:#5fd7d7">Int</span>, and <span style="color:#87d787">"12"</span> is a <span style="color:#5fd7d7">String</span>.
<span></span>
Text is never turned into a number on its own, because text
may hold anything.
<span></span>
To fix it, write the number:
<span></span>
    <span style="color:#5fafff">total</span>(<span style="color:#afd7ff">price</span> = <span style="color:#ff875f">12</span>, <span style="color:#afd7ff">quantity</span> = <span style="color:#ff875f">3</span>)
<span></span>
<span style="color:#8a8a8a">(AX1001. For more, run: drx explain AX1001)</span></span><span></span>
<span></span>
<span style="color:#cd3131;font-weight:700">1 error</span> in 1 file. The package was not built.</code></pre>
</figure>
</div>

Both stop at the text. rustc marks the parameter in the definition, `price: u32`; drx names it in a sentence
and shows the call to write.

## 3. A kind left out

A receipt for a cart that holds a book, a gift card and a bookmark, with a line written only for books and gift
cards.

<div class="vs">
<figure>
<p class="lang">Rust</p>
<pre tabindex="0" role="region" aria-label="Rust: shop.rs"><code><span class="t-sd">/// Something the shop sells.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">enum</span><span class="t-w"> </span><span class="t-nc">Item</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-n">Book</span><span class="t-w"> </span><span class="t-p">{</span><span class="t-w"> </span><span class="t-n">name</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-nb">String</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">price</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-w"> </span><span class="t-p">},</span>
<span class="t-w">    </span><span class="t-n">GiftCard</span><span class="t-w"> </span><span class="t-p">{</span><span class="t-w"> </span><span class="t-n">name</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-nb">String</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">price</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">recipient</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-nb">String</span><span class="t-w"> </span><span class="t-p">},</span>
<span class="t-w">    </span><span class="t-n">Bookmark</span><span class="t-w"> </span><span class="t-p">{</span><span class="t-w"> </span><span class="t-n">name</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-nb">String</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">price</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-w"> </span><span class="t-p">},</span>
<span class="t-p">}</span>
<span></span>
<span class="t-sd">/// Writes an item's line on the receipt.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">line</span><span class="t-p">(</span><span class="t-n">item</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kp">&amp;</span><span class="t-nc">Item</span><span class="t-p">)</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-nb">String</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-k">match</span><span class="t-w"> </span><span class="t-n">item</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">        </span><span class="t-n">Item</span><span class="t-p">::</span><span class="t-n">Book</span><span class="t-w"> </span><span class="t-p">{</span><span class="t-w"> </span><span class="t-n">name</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">price</span><span class="t-w"> </span><span class="t-p">}</span><span class="t-w"> </span><span class="t-o">=&gt;</span><span class="t-w"> </span><span class="t-fm">format!</span><span class="t-p">(</span><span class="t-s">"{name}: {price}"</span><span class="t-p">),</span>
<span class="t-w">        </span><span class="t-n">Item</span><span class="t-p">::</span><span class="t-n">GiftCard</span><span class="t-w"> </span><span class="t-p">{</span><span class="t-w"> </span><span class="t-n">name</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">price</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">recipient</span><span class="t-w"> </span><span class="t-p">}</span><span class="t-w"> </span><span class="t-o">=&gt;</span><span class="t-w"> </span><span class="t-fm">format!</span><span class="t-p">(</span><span class="t-s">"{name} for {recipient}: {price}"</span><span class="t-p">),</span>
<span class="t-w">    </span><span class="t-p">}</span>
<span class="t-p">}</span>
<span></span>
<span class="t-sd">/// Writes the receipt's lines for every item in `cart`.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">receipt</span><span class="t-p">(</span><span class="t-n">cart</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kp">&amp;</span><span class="t-p">[</span><span class="t-n">Item</span><span class="t-p">])</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-nb">Vec</span><span class="t-o">&lt;</span><span class="t-nb">String</span><span class="t-o">&gt;</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-kd">let</span><span class="t-w"> </span><span class="t-k">mut</span><span class="t-w"> </span><span class="t-n">lines</span><span class="t-w"> </span><span class="t-o">=</span><span class="t-w"> </span><span class="t-nb">Vec</span><span class="t-p">::</span><span class="t-n">new</span><span class="t-p">();</span>
<span class="t-w">    </span><span class="t-k">for</span><span class="t-w"> </span><span class="t-n">item</span><span class="t-w"> </span><span class="t-k">in</span><span class="t-w"> </span><span class="t-n">cart</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">        </span><span class="t-n">lines</span><span class="t-p">.</span><span class="t-n">push</span><span class="t-p">(</span><span class="t-n">line</span><span class="t-p">(</span><span class="t-n">item</span><span class="t-p">));</span>
<span class="t-w">    </span><span class="t-p">}</span>
<span class="t-w">    </span><span class="t-n">lines</span>
<span class="t-p">}</span>
<span></span>
<span class="t-sd">/// Writes the receipt for a cart of a book, a gift card and a bookmark.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">checkout</span><span class="t-p">()</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-nb">Vec</span><span class="t-o">&lt;</span><span class="t-nb">String</span><span class="t-o">&gt;</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-n">receipt</span><span class="t-p">(</span><span class="t-o">&amp;</span><span class="t-p">[</span>
<span class="t-w">        </span><span class="t-n">Item</span><span class="t-p">::</span><span class="t-n">Book</span><span class="t-w"> </span><span class="t-p">{</span><span class="t-w"> </span><span class="t-n">name</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s">"Dune"</span><span class="t-p">.</span><span class="t-n">into</span><span class="t-p">(),</span><span class="t-w"> </span><span class="t-n">price</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">12</span><span class="t-w"> </span><span class="t-p">},</span>
<span class="t-w">        </span><span class="t-n">Item</span><span class="t-p">::</span><span class="t-n">GiftCard</span><span class="t-w"> </span><span class="t-p">{</span><span class="t-w"> </span><span class="t-n">name</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s">"Gift card"</span><span class="t-p">.</span><span class="t-n">into</span><span class="t-p">(),</span><span class="t-w"> </span><span class="t-n">price</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">25</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">recipient</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s">"Ada"</span><span class="t-p">.</span><span class="t-n">into</span><span class="t-p">()</span><span class="t-w"> </span><span class="t-p">},</span>
<span class="t-w">        </span><span class="t-n">Item</span><span class="t-p">::</span><span class="t-n">Bookmark</span><span class="t-w"> </span><span class="t-p">{</span><span class="t-w"> </span><span class="t-n">name</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s">"Bookmark"</span><span class="t-p">.</span><span class="t-n">into</span><span class="t-p">(),</span><span class="t-w"> </span><span class="t-n">price</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">2</span><span class="t-w"> </span><span class="t-p">},</span>
<span class="t-w">    </span><span class="t-p">])</span>
<span class="t-p">}</span></code></pre>
<p class="cap">rustc says:</p>
<pre class="term" tabindex="0" role="region" aria-label="rustc&#x27;s output"><code><span style="color:#8a8a8a">$</span> rustc --edition 2024 --crate-type lib shop.rs
<span></span>
<span style="color:#f14c4c;font-weight:700">error[E0004]</span><span style="font-weight:700">: non-exhaustive patterns: `&amp;Item::Bookmark { .. }` not covered</span>
  <span style="color:#3b8eea;font-weight:700">--&gt; </span>shop.rs:10:11
   <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700">10</span> <span style="color:#3b8eea;font-weight:700">|</span>     match item {
   <span style="color:#3b8eea;font-weight:700">|</span>           <span style="color:#f14c4c;font-weight:700">^^^^</span> <span style="color:#f14c4c;font-weight:700">pattern `&amp;Item::Bookmark { .. }` not covered</span>
   <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#23d18b;font-weight:700">note</span>: `Item` defined here
  <span style="color:#3b8eea;font-weight:700">--&gt; </span>shop.rs:2:10
   <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700"> 2</span> <span style="color:#3b8eea;font-weight:700">|</span> pub enum Item {
   <span style="color:#3b8eea;font-weight:700">|</span>          <span style="color:#23d18b;font-weight:700">^^^^</span>
<span style="color:#3b8eea;font-weight:700">...</span>
<span style="color:#3b8eea;font-weight:700"> 5</span> <span style="color:#3b8eea;font-weight:700">|</span>     Bookmark { name: String, price: u32 },
   <span style="color:#3b8eea;font-weight:700">|</span>     <span style="color:#3b8eea;font-weight:700">--------</span> <span style="color:#3b8eea;font-weight:700">not covered</span>
   <span style="color:#3b8eea;font-weight:700">= </span><span style="font-weight:700">note</span>: the matched value is of type `&amp;Item`
<span style="color:#29b8db;font-weight:700">help</span>: ensure that all possible cases are being handled by adding a match arm with a wildcard pattern or an explicit pattern as shown
   <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700">12</span> <span style="color:#23d18b">~ </span>        Item::GiftCard { name, price, recipient } =&gt; format!("{name} for {recipient}: {price}")<span style="color:#23d18b">,</span>
<span style="color:#3b8eea;font-weight:700">13</span> <span style="color:#23d18b">~         &amp;Item::Bookmark { .. } =&gt; todo!()</span>,
   <span style="color:#3b8eea;font-weight:700">|</span>
<span></span>
<span style="color:#f14c4c;font-weight:700">error</span><span style="font-weight:700">: aborting due to 1 previous error</span>
<span></span>
<span style="font-weight:700">For more information about this error, try `rustc --explain E0004`.</span></code></pre>
</figure>
<figure>
<p class="lang">Draconyx</p>
<pre tabindex="0" role="region" aria-label="Draconyx: src/shop.ax"><code><span class="k">module</span> shop
<span></span>
<span class="k">@doc</span> <span class="s">"""A book the shop sells."""</span>
<span class="k">type</span> Book:
    name: String
    price: Int
<span></span>
<span class="k">@doc</span> <span class="s">"""A gift card bought for someone."""</span>
<span class="k">type</span> GiftCard:
    name: String
    price: Int
    recipient: String
<span></span>
<span class="k">@doc</span> <span class="s">"""A bookmark the shop sells."""</span>
<span class="k">type</span> Bookmark:
    name: String
    price: Int
<span></span>
<span class="k">@doc</span> <span class="s">"""Writes a book's line on the receipt.</span>
  * book - the book to write
<span class="s">""</span>"
line(book: Book) -&gt; String:
    <span class="s">"{book.name}: {book.price}"</span>
<span></span>
<span class="k">@doc</span> <span class="s">"""Writes a gift card's line on the receipt.</span>
  * card - the gift card to write
<span class="s">""</span>"
line(card: GiftCard) -&gt; String:
    <span class="s">"{card.name} for {card.recipient}: {card.price}"</span>
<span></span>
<span class="k">@doc</span> <span class="s">"""Writes the receipt's lines for every item in `cart`.</span>
  * cart - the items bought, of <span class="k">any</span> kind
<span class="s">""</span>"
receipt(cart: List&lt;<span class="k">any</span> T&gt;) -&gt; List&lt;String&gt;:
    lines: List&lt;String&gt; = []
<span></span>
    <span class="k">for</span> item <span class="k">in</span> cart:
        push(list = <span class="k">borrow</span> lines, item = line(item))
<span></span>
    lines
<span></span>
<span class="k">@doc</span> <span class="s">"""Writes the receipt for a cart of a book, a gift card and a bookmark."""</span>
checkout() -&gt; List&lt;String&gt;:
    receipt([Book(name = <span class="s">"Dune"</span>, price = 12), GiftCard(name = <span class="s">"Gift card"</span>, price = 25, recipient = <span class="s">"Ada"</span>),
             Bookmark(name = <span class="s">"Bookmark"</span>, price = 2)])</code></pre>
<p class="cap">drx says:</p>
<pre class="term" tabindex="0" role="region" aria-label="drx&#x27;s output"><code><span style="color:#8a8a8a">$</span> drx check shop
<span></span>
<span></span><span class="bar" style="border-left-color:#cd3131"><span style="color:#ffffff;background:#cd3131;font-weight:700"> ERROR </span>  <span style="color:#ffffff;font-weight:700">src/shop.ax, line 45</span>
<span></span>
    <span style="color:#5fd7d7">Bookmark</span>(<span style="color:#afd7ff">name</span> = <span style="color:#87d787">"Bookmark"</span>, <span style="color:#afd7ff">price</span> = <span style="color:#ff875f">2</span>)])
    <span style="color:#cd3131">^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^</span>
<span></span>
This <span style="color:#5fd7d7">Bookmark</span> goes into a cart of <span style="color:#afd7ff">any</span> <span style="color:#5fd7d7">T</span>, and no <span style="color:#afd7ff">line</span> is
written for <span style="color:#5fd7d7">Bookmark</span>.
<span></span>
<span style="color:#afd7ff">receipt</span> calls <span style="color:#afd7ff">line</span> on every item of the cart, on line 38,
so each kind that goes in needs a <span style="color:#afd7ff">line</span> of its own.
<span></span>
To fix it, write a <span style="color:#afd7ff">line</span> for <span style="color:#5fd7d7">Bookmark</span>:
<span></span>
    <span style="color:#d787d7">@doc</span> <span style="color:#87d787">"""Writes a bookmark's line on the receipt.</span>
    <span style="color:#87d787">  * bookmark - the bookmark to write</span>
    <span style="color:#87d787">"""</span>
    <span style="color:#5fafff">line</span>(<span style="color:#afd7ff">bookmark</span>: <span style="color:#5fd7d7">Bookmark</span>) -&gt; <span style="color:#5fd7d7">String</span>:
        <span style="color:#87d787">"{bookmark.name}: {bookmark.price}"</span>
<span></span>
<span style="color:#8a8a8a">(AX0420. For more, run: drx explain AX0420)</span></span><span></span>
<span></span>
<span style="color:#cd3131;font-weight:700">1 error</span> in 1 file. The package was not built.</code></pre>
</figure>
</div>

Both refuse the program before it runs, and both name the bookmark. In Rust the kinds are one `enum` and the
cases are the arms of one `match`; rustc points at the `match`, names `Item::Bookmark`, and offers an arm with
`todo!()` to fill in. In Draconyx each kind is a type of its own with its own `line`, joined where they meet by
`any T`; drx points at the bookmark where it goes into the cart, names the `line` it has none of, and shows the
`line` to write.

## 4. A value used after it was given away

A greeting sent twice, when sending takes it.

<div class="vs">
<figure>
<p class="lang">Rust</p>
<pre tabindex="0" role="region" aria-label="Rust: mail.rs"><code><span class="t-sd">/// Sends `message` and counts the bytes that went out.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">send</span><span class="t-p">(</span><span class="t-n">message</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-nb">String</span><span class="t-p">)</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-kt">usize</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-n">message</span><span class="t-p">.</span><span class="t-n">len</span><span class="t-p">()</span>
<span class="t-p">}</span>
<span></span>
<span class="t-sd">/// Sends the same greeting twice.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">notify</span><span class="t-p">()</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-kt">usize</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-kd">let</span><span class="t-w"> </span><span class="t-n">greeting</span><span class="t-w"> </span><span class="t-o">=</span><span class="t-w"> </span><span class="t-nb">String</span><span class="t-p">::</span><span class="t-n">from</span><span class="t-p">(</span><span class="t-s">"Hello"</span><span class="t-p">);</span>
<span class="t-w">    </span><span class="t-kd">let</span><span class="t-w"> </span><span class="t-n">first</span><span class="t-w"> </span><span class="t-o">=</span><span class="t-w"> </span><span class="t-n">send</span><span class="t-p">(</span><span class="t-n">greeting</span><span class="t-p">);</span>
<span class="t-w">    </span><span class="t-kd">let</span><span class="t-w"> </span><span class="t-n">second</span><span class="t-w"> </span><span class="t-o">=</span><span class="t-w"> </span><span class="t-n">send</span><span class="t-p">(</span><span class="t-n">greeting</span><span class="t-p">);</span>
<span class="t-w">    </span><span class="t-n">first</span><span class="t-w"> </span><span class="t-o">+</span><span class="t-w"> </span><span class="t-n">second</span>
<span class="t-p">}</span></code></pre>
<p class="cap">rustc says:</p>
<pre class="term" tabindex="0" role="region" aria-label="rustc&#x27;s output"><code><span style="color:#8a8a8a">$</span> rustc --edition 2024 --crate-type lib mail.rs
<span></span>
<span style="color:#f14c4c;font-weight:700">error[E0382]</span><span style="font-weight:700">: use of moved value: `greeting`</span>
  <span style="color:#3b8eea;font-weight:700">--&gt; </span>mail.rs:10:23
   <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700"> 8</span> <span style="color:#3b8eea;font-weight:700">|</span>     let greeting = String::from("Hello");
   <span style="color:#3b8eea;font-weight:700">|</span>         <span style="color:#3b8eea;font-weight:700">--------</span> <span style="color:#3b8eea;font-weight:700">move occurs because `greeting` has type `String`, which does not implement the `Copy` trait</span>
<span style="color:#3b8eea;font-weight:700"> 9</span> <span style="color:#3b8eea;font-weight:700">|</span>     let first = send(greeting);
   <span style="color:#3b8eea;font-weight:700">|</span>                      <span style="color:#3b8eea;font-weight:700">--------</span> <span style="color:#3b8eea;font-weight:700">value moved here</span>
<span style="color:#3b8eea;font-weight:700">10</span> <span style="color:#3b8eea;font-weight:700">|</span>     let second = send(greeting);
   <span style="color:#3b8eea;font-weight:700">|</span>                       <span style="color:#f14c4c;font-weight:700">^^^^^^^^</span> <span style="color:#f14c4c;font-weight:700">value used here after move</span>
   <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#23d18b;font-weight:700">note</span>: consider changing this parameter type in function `send` to borrow instead if owning the value isn't necessary
  <span style="color:#3b8eea;font-weight:700">--&gt; </span>mail.rs:2:22
   <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700"> 2</span> <span style="color:#3b8eea;font-weight:700">|</span> pub fn send(message: String) -&gt; usize {
   <span style="color:#3b8eea;font-weight:700">|</span>        <span style="color:#3b8eea;font-weight:700">----</span>          <span style="color:#23d18b;font-weight:700">^^^^^^</span> <span style="color:#23d18b;font-weight:700">this parameter takes ownership of the value</span>
   <span style="color:#3b8eea;font-weight:700">|</span>        <span style="color:#3b8eea;font-weight:700">|</span>
   <span style="color:#3b8eea;font-weight:700">|</span>        <span style="color:#3b8eea;font-weight:700">in this function</span>
<span style="color:#29b8db;font-weight:700">help</span>: consider cloning the value if the performance cost is acceptable
   <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700"> 9</span> <span style="color:#3b8eea;font-weight:700">| </span>    let first = send(greeting<span style="color:#23d18b">.clone()</span>);
   <span style="color:#3b8eea;font-weight:700">|</span>                              <span style="color:#23d18b">++++++++</span>
<span></span>
<span style="color:#f14c4c;font-weight:700">error</span><span style="font-weight:700">: aborting due to 1 previous error</span>
<span></span>
<span style="font-weight:700">For more information about this error, try `rustc --explain E0382`.</span></code></pre>
</figure>
<figure>
<p class="lang">Draconyx</p>
<pre tabindex="0" role="region" aria-label="Draconyx: src/mail.ax"><code><span class="k">module</span> mail
<span></span>
<span class="k">@doc</span> <span class="s">"""Sends `message` and counts the bytes that went out.</span>
  * message - the text to send
<span class="s">""</span>"
send(<span class="k">take</span> message: String) -&gt; Int:
    len_bytes(message)
<span></span>
<span class="k">@doc</span> <span class="s">"""Sends the same greeting twice."""</span>
notify() -&gt; Int:
    greeting = <span class="s">"Hello"</span>
    first = send(<span class="k">take</span> greeting)
    second = send(<span class="k">take</span> greeting)
    first + second</code></pre>
<p class="cap">drx says:</p>
<pre class="term" tabindex="0" role="region" aria-label="drx&#x27;s output"><code><span style="color:#8a8a8a">$</span> drx check mail
<span></span>
<span></span><span class="bar" style="border-left-color:#cd3131"><span style="color:#ffffff;background:#cd3131;font-weight:700"> ERROR </span>  <span style="color:#ffffff;font-weight:700">src/mail.ax, line 13</span>
<span></span>
    <span style="color:#afd7ff">second</span> = <span style="color:#5fafff">send</span>(<span style="color:#d787d7">take</span> <span style="color:#afd7ff">greeting</span>)
                  <span style="color:#cd3131">^^^^^^^^^^^^^</span>
<span></span>
<span style="color:#afd7ff">greeting</span> was given to <span style="color:#afd7ff">send</span> on line 12, so it cannot be
used again here.
<span></span>
<span style="color:#afd7ff">send</span> takes its message with <span style="color:#d787d7">take</span>: after the first call,
<span style="color:#afd7ff">send</span> owns <span style="color:#afd7ff">greeting</span> and this function no longer has it.
<span></span>
If <span style="color:#afd7ff">send</span> only reads the message, drop <span style="color:#d787d7">take</span> in three places:
here, on line 12, and in the signature of <span style="color:#afd7ff">send</span>:
<span></span>
    <span style="color:#5fafff">send</span>(<span style="color:#afd7ff">message</span>: <span style="color:#5fd7d7">String</span>) -&gt; <span style="color:#5fd7d7">Int</span>:
<span></span>
<span style="color:#8a8a8a">(AX0312. For more, run: drx explain AX0312)</span></span><span></span>
<span></span>
<span style="color:#cd3131;font-weight:700">1 error</span> in 1 file. The package was not built.</code></pre>
</figure>
</div>

In Rust, giving a value away looks the same as passing a number, which is copied: `send(greeting)`. rustc finds
the move and labels it, on line 9. In Draconyx the call itself says `take`, so the code shows the line that gives
the value away, not only the compiler's message.

## 5. A missing argument

A call of `total` that forgets the quantity.

<div class="vs">
<figure>
<p class="lang">Rust</p>
<pre tabindex="0" role="region" aria-label="Rust: shop.rs"><code><span class="t-sd">/// Works out what `quantity` items at `price` cost.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">total</span><span class="t-p">(</span><span class="t-n">price</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-n">quantity</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-p">)</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-n">price</span><span class="t-w"> </span><span class="t-o">*</span><span class="t-w"> </span><span class="t-n">quantity</span>
<span class="t-p">}</span>
<span></span>
<span class="t-sd">/// Works out the cost of one item at 12.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">checkout</span><span class="t-p">()</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-n">total</span><span class="t-p">(</span><span class="t-mi">12</span><span class="t-p">)</span>
<span class="t-p">}</span></code></pre>
<p class="cap">rustc says:</p>
<pre class="term" tabindex="0" role="region" aria-label="rustc&#x27;s output"><code><span style="color:#8a8a8a">$</span> rustc --edition 2024 --crate-type lib shop.rs
<span></span>
<span style="color:#f14c4c;font-weight:700">error[E0061]</span><span style="font-weight:700">: this function takes 2 arguments but 1 argument was supplied</span>
 <span style="color:#3b8eea;font-weight:700">--&gt; </span>shop.rs:8:5
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700">8</span> <span style="color:#3b8eea;font-weight:700">|</span>     total(12)
  <span style="color:#3b8eea;font-weight:700">|</span>     <span style="color:#f14c4c;font-weight:700">^^^^^</span><span style="color:#3b8eea;font-weight:700">----</span> <span style="color:#3b8eea;font-weight:700">argument #2 of type `u32` is missing</span>
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#23d18b;font-weight:700">note</span>: function defined here
 <span style="color:#3b8eea;font-weight:700">--&gt; </span>shop.rs:2:8
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700">2</span> <span style="color:#3b8eea;font-weight:700">|</span> pub fn total(price: u32, quantity: u32) -&gt; u32 {
  <span style="color:#3b8eea;font-weight:700">|</span>        <span style="color:#23d18b;font-weight:700">^^^^^</span>             <span style="color:#3b8eea;font-weight:700">-------------</span>
<span style="color:#29b8db;font-weight:700">help</span>: provide the argument
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700">8</span> <span style="color:#3b8eea;font-weight:700">| </span>    total(12<span style="color:#23d18b">, /* u32 */</span>)
  <span style="color:#3b8eea;font-weight:700">|</span>             <span style="color:#23d18b">+++++++++++</span>
<span></span>
<span style="color:#f14c4c;font-weight:700">error</span><span style="font-weight:700">: aborting due to 1 previous error</span>
<span></span>
<span style="font-weight:700">For more information about this error, try `rustc --explain E0061`.</span></code></pre>
</figure>
<figure>
<p class="lang">Draconyx</p>
<pre tabindex="0" role="region" aria-label="Draconyx: src/shop.ax"><code><span class="k">module</span> shop
<span></span>
<span class="k">@doc</span> <span class="s">"""Works out what `quantity` items at `price` cost.</span>
  * price - the price of one item
  * quantity - how many items are bought
<span class="s">""</span>"
total(price: Int, quantity: Int) -&gt; Int:
    price * quantity
<span></span>
<span class="k">@doc</span> <span class="s">"""Works out the cost of one item at 12."""</span>
checkout() -&gt; Int:
    total(price = 12)</code></pre>
<p class="cap">drx says:</p>
<pre class="term" tabindex="0" role="region" aria-label="drx&#x27;s output"><code><span style="color:#8a8a8a">$</span> drx check shop
<span></span>
<span></span><span class="bar" style="border-left-color:#cd3131"><span style="color:#ffffff;background:#cd3131;font-weight:700"> ERROR </span>  <span style="color:#ffffff;font-weight:700">src/shop.ax, line 12</span>
<span></span>
    <span style="color:#5fafff">total</span>(<span style="color:#afd7ff">price</span> = <span style="color:#ff875f">12</span>)
    <span style="color:#cd3131">^^^^^</span>
<span></span>
This call of <span style="color:#afd7ff">total</span> gives <span style="color:#afd7ff">price</span> but no <span style="color:#afd7ff">quantity</span>.
<span></span>
<span style="color:#afd7ff">total</span> is declared as <span style="color:#5fafff">total</span>(<span style="color:#afd7ff">price</span>: <span style="color:#5fd7d7">Int</span>, <span style="color:#afd7ff">quantity</span>: <span style="color:#5fd7d7">Int</span>), and
each of its parameters needs a value.
<span></span>
To fix it, write:
<span></span>
    <span style="color:#5fafff">total</span>(<span style="color:#afd7ff">price</span> = <span style="color:#ff875f">12</span>, <span style="color:#afd7ff">quantity</span> = <span style="color:#ff875f">1</span>)
<span></span>
<span style="color:#8a8a8a">(AX0249. For more, run: drx explain AX0249)</span></span><span></span>
<span></span>
<span style="color:#cd3131;font-weight:700">1 error</span> in 1 file. The package was not built.</code></pre>
</figure>
</div>

rustc labels the missing argument by its position, argument #2, underlines `quantity: u32` in the
definition and offers `total(12, /* u32 */)`. Draconyx calls name their arguments, so drx names it, `quantity`,
in the sentence itself.

## 6. One that `drx fix` repairs for you

A local name in camelCase, the habit of JavaScript and Java.

<div class="vs">
<figure>
<p class="lang">Rust</p>
<pre tabindex="0" role="region" aria-label="Rust: shop.rs"><code><span class="t-sd">/// Adds a 20% tax to `price`.</span>
<span class="t-k">pub</span><span class="t-w"> </span><span class="t-k">fn</span><span class="t-w"> </span><span class="t-nf">with_tax</span><span class="t-p">(</span><span class="t-n">price</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-p">)</span><span class="t-w"> </span><span class="t-p">-&gt;</span><span class="t-w"> </span><span class="t-kt">u32</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-kd">let</span><span class="t-w"> </span><span class="t-n">totalPrice</span><span class="t-w"> </span><span class="t-o">=</span><span class="t-w"> </span><span class="t-n">price</span><span class="t-w"> </span><span class="t-o">+</span><span class="t-w"> </span><span class="t-n">price</span><span class="t-w"> </span><span class="t-o">/</span><span class="t-w"> </span><span class="t-mi">5</span><span class="t-p">;</span>
<span class="t-w">    </span><span class="t-n">totalPrice</span>
<span class="t-p">}</span></code></pre>
<p class="cap">rustc says:</p>
<pre class="term" tabindex="0" role="region" aria-label="rustc&#x27;s output"><code><span style="color:#8a8a8a">$</span> rustc --edition 2024 --crate-type lib shop.rs
<span></span>
<span style="color:#e5e510;font-weight:700">warning</span><span style="font-weight:700">: variable `totalPrice` should have a snake case name</span>
 <span style="color:#3b8eea;font-weight:700">--&gt; </span>shop.rs:3:9
  <span style="color:#3b8eea;font-weight:700">|</span>
<span style="color:#3b8eea;font-weight:700">3</span> <span style="color:#3b8eea;font-weight:700">|</span>     let totalPrice = price + price / 5;
  <span style="color:#3b8eea;font-weight:700">|</span>         <span style="color:#e5e510;font-weight:700">^^^^^^^^^^</span> <span style="color:#e5e510;font-weight:700">help: convert the identifier to snake case: `total_price`</span>
  <span style="color:#3b8eea;font-weight:700">|</span>
  <span style="color:#3b8eea;font-weight:700">= </span><span style="font-weight:700">note</span>: `#[warn(non_snake_case)]` (part of `#[warn(nonstandard_style)]`) on by default
<span></span>
<span style="color:#e5e510;font-weight:700">warning</span><span style="font-weight:700">: 1 warning emitted</span></code></pre>
</figure>
<figure>
<p class="lang">Draconyx</p>
<pre tabindex="0" role="region" aria-label="Draconyx: src/shop.ax"><code><span class="k">module</span> shop
<span></span>
<span class="k">@doc</span> <span class="s">"""Adds a 20% tax to `price`.</span>
  * price - the price before tax
<span class="s">""</span>"
with_tax(price: Int) -&gt; Int:
    totalPrice = price + price / 5
    totalPrice</code></pre>
<p class="cap">drx says:</p>
<pre class="term" tabindex="0" role="region" aria-label="drx&#x27;s output"><code><span style="color:#8a8a8a">$</span> drx check shop
<span></span>
<span></span><span class="bar" style="border-left-color:#cd3131"><span style="color:#ffffff;background:#cd3131;font-weight:700"> ERROR </span>  <span style="color:#ffffff;font-weight:700">src/shop.ax, line 7</span>
<span></span>
    <span style="color:#afd7ff">totalPrice</span> = <span style="color:#afd7ff">price</span> + <span style="color:#afd7ff">price</span> / <span style="color:#ff875f">5</span>
    <span style="color:#cd3131">^^^^^^^^^^</span>
<span></span>
<span style="color:#afd7ff">totalPrice</span> is a local name, and local names are written in
lower_snake case.
<span></span>
The case tells values from types: a value is written
<span style="color:#afd7ff">total_price</span>, a type <span style="color:#5fd7d7">TotalPrice</span>.
<span></span>
Rename it <span style="color:#afd7ff">total_price</span>, here and on line 8.
<span></span>
<span style="color:#afd7ff">drx fix</span> makes this change for you.
<span></span>
<span style="color:#8a8a8a">(AX1201. For more, run: drx explain AX1201)</span></span><span></span>
<span></span>
<span style="color:#cd3131;font-weight:700">1 error</span> in 1 file. The package was not built.</code></pre>
</figure>
</div>

rustc builds the code and warns. Its suggestion is marked as one that may be wrong, so `cargo fix` leaves the
name as it is. drx refuses the name, and `drx fix` renames it on both lines:

<pre tabindex="0" role="region" aria-label="Draconyx: src/shop.ax after drx fix"><code><span class="k">module</span> shop
<span></span>
<span class="k">@doc</span> <span class="s">"""Adds a 20% tax to `price`.</span>
  * price - the price before tax
<span class="s">""</span>"
with_tax(price: Int) -&gt; Int:
    total_price = price + price / 5
    total_price</code></pre>

## For agents: the same report as JSON

Both compilers can print their reports as JSON, for editors, tools and AI agents. Here is the misspelled name
from the first example, once from each, with line breaks added. rustc prints one object per diagnostic, plus two
short ones for its closing lines; this is the first. drx prints one line per diagnostic.

<div class="vs">
<figure>
<p class="lang">Rust</p>
<pre tabindex="0" role="region" aria-label="rustc&#x27;s JSON command"><code><span style="color:#9d9583">$</span> rustc --edition 2024 --crate-type lib --error-format=json shop.rs</code></pre>
<p class="cap">rustc says:</p>
<pre class="json" tabindex="0" role="region" aria-label="rustc&#x27;s JSON"><code><span class="t-p">{</span>
<span class="t-w">  </span><span class="t-nt">"$message_type"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"diagnostic"</span><span class="t-p">,</span>
<span class="t-w">  </span><span class="t-nt">"message"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"cannot find value `quantitty` in this scope"</span><span class="t-p">,</span>
<span class="t-w">  </span><span class="t-nt">"code"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-nt">"code"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"E0425"</span><span class="t-p">,</span>
<span class="t-w">    </span><span class="t-nt">"explanation"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"An unresolved name was used.\n\nErroneous code examples:\n\n```compile_fail,E0425\nsomething_that_doesnt_exist::foo;\n// error: unresolved name `something_that_doesnt_exist::foo`\n\n// or:\n\ntrait Foo {\n    fn bar() {\n        Self; // error: unresolved name `Self`\n    }\n}\n\n// or:\n\nlet x = unknown_variable;  // error: unresolved name `unknown_variable`\n```\n\nPlease verify that the name wasn't misspelled and ensure that the\nidentifier being referred to is valid for the given situation. Example:\n\n```\nenum something_that_does_exist {\n    Foo,\n}\n```\n\nOr:\n\n```\nmod something_that_does_exist {\n    pub static foo : i32 = 0i32;\n}\n\nsomething_that_does_exist::foo; // ok!\n```\n\nOr:\n\n```\nlet unknown_variable = 12u32;\nlet x = unknown_variable; // ok!\n```\n\nIf the item is not defined in the current module, it must be imported using a\n`use` statement, like so:\n\n```\n# mod foo { pub fn bar() {} }\n# fn main() {\nuse foo::bar;\nbar();\n# }\n```\n\nIf the item you are importing is not defined in some super-module of the\ncurrent module, then it must also be declared as public (e.g., `pub fn`).\n"</span>
<span class="t-w">  </span><span class="t-p">},</span>
<span class="t-w">  </span><span class="t-nt">"level"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"error"</span><span class="t-p">,</span>
<span class="t-w">  </span><span class="t-nt">"spans"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span>
<span class="t-w">    </span><span class="t-p">{</span>
<span class="t-w">      </span><span class="t-nt">"file_name"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"shop.rs"</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"byte_start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">114</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"byte_end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">123</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"line_start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">3</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"line_end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">3</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"column_start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">13</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"column_end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">22</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"is_primary"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kc">true</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"text"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span>
<span class="t-w">        </span><span class="t-p">{</span>
<span class="t-w">          </span><span class="t-nt">"text"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"    price * quantitty"</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"highlight_start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">13</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"highlight_end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">22</span>
<span class="t-w">        </span><span class="t-p">}</span>
<span class="t-w">      </span><span class="t-p">],</span>
<span class="t-w">      </span><span class="t-nt">"label"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kc">null</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"suggested_replacement"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kc">null</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"suggestion_applicability"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kc">null</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"expansion"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kc">null</span>
<span class="t-w">    </span><span class="t-p">}</span>
<span class="t-w">  </span><span class="t-p">],</span>
<span class="t-w">  </span><span class="t-nt">"children"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span>
<span class="t-w">    </span><span class="t-p">{</span>
<span class="t-w">      </span><span class="t-nt">"message"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"a local variable with a similar name exists"</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"code"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kc">null</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"level"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"help"</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"spans"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span>
<span class="t-w">        </span><span class="t-p">{</span>
<span class="t-w">          </span><span class="t-nt">"file_name"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"shop.rs"</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"byte_start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">114</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"byte_end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">123</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"line_start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">3</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"line_end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">3</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"column_start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">13</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"column_end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">22</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"is_primary"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kc">true</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"text"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span>
<span class="t-w">            </span><span class="t-p">{</span>
<span class="t-w">              </span><span class="t-nt">"text"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"    price * quantitty"</span><span class="t-p">,</span>
<span class="t-w">              </span><span class="t-nt">"highlight_start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">13</span><span class="t-p">,</span>
<span class="t-w">              </span><span class="t-nt">"highlight_end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-mi">22</span>
<span class="t-w">            </span><span class="t-p">}</span>
<span class="t-w">          </span><span class="t-p">],</span>
<span class="t-w">          </span><span class="t-nt">"label"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kc">null</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"suggested_replacement"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"quantity"</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"suggestion_applicability"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"MaybeIncorrect"</span><span class="t-p">,</span>
<span class="t-w">          </span><span class="t-nt">"expansion"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kc">null</span>
<span class="t-w">        </span><span class="t-p">}</span>
<span class="t-w">      </span><span class="t-p">],</span>
<span class="t-w">      </span><span class="t-nt">"children"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[],</span>
<span class="t-w">      </span><span class="t-nt">"rendered"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-kc">null</span>
<span class="t-w">    </span><span class="t-p">}</span>
<span class="t-w">  </span><span class="t-p">],</span>
<span class="t-w">  </span><span class="t-nt">"rendered"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"error[E0425]: cannot find value `quantitty` in this scope\n --&gt; shop.rs:3:13\n  |\n3 |     price * quantitty\n  |             ^^^^^^^^^\n  |\nhelp: a local variable with a similar name exists\n  |\n3 -     price * quantitty\n3 +     price * quantity\n  |\n\n"</span>
<span class="t-p">}</span></code></pre>
</figure>
<figure>
<p class="lang">Draconyx</p>
<pre tabindex="0" role="region" aria-label="drx&#x27;s JSON command"><code><span style="color:#9d9583">$</span> drx check shop --json</code></pre>
<p class="cap">drx says:</p>
<pre class="json" tabindex="0" role="region" aria-label="drx&#x27;s JSON"><code><span class="t-p">{</span>
<span class="t-w">  </span><span class="t-nt">"code"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"AX0234"</span><span class="t-p">,</span>
<span class="t-w">  </span><span class="t-nt">"severity"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"error"</span><span class="t-p">,</span>
<span class="t-w">  </span><span class="t-nt">"message"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"`quantitty` is not a name this function knows."</span><span class="t-p">,</span>
<span class="t-w">  </span><span class="t-nt">"primary_span"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">    </span><span class="t-nt">"file"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"src/shop.ax"</span><span class="t-p">,</span>
<span class="t-w">    </span><span class="t-nt">"start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">8</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">13</span><span class="t-p">],</span>
<span class="t-w">    </span><span class="t-nt">"end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">8</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">22</span><span class="t-p">],</span>
<span class="t-w">    </span><span class="t-nt">"bytes"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">202</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">211</span><span class="t-p">]</span>
<span class="t-w">  </span><span class="t-p">},</span>
<span class="t-w">  </span><span class="t-nt">"secondary_spans"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[],</span>
<span class="t-w">  </span><span class="t-nt">"explanation"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"`total` has the parameters `price` and `quantity`, and nothing else in reach is called `quantitty`."</span><span class="t-p">,</span>
<span class="t-w">  </span><span class="t-nt">"suggested_edits"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span>
<span class="t-w">    </span><span class="t-p">{</span>
<span class="t-w">      </span><span class="t-nt">"span"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">        </span><span class="t-nt">"file"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"src/shop.ax"</span><span class="t-p">,</span>
<span class="t-w">        </span><span class="t-nt">"start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">8</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">13</span><span class="t-p">],</span>
<span class="t-w">        </span><span class="t-nt">"end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">8</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">22</span><span class="t-p">],</span>
<span class="t-w">        </span><span class="t-nt">"bytes"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">202</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">211</span><span class="t-p">]</span>
<span class="t-w">      </span><span class="t-p">},</span>
<span class="t-w">      </span><span class="t-nt">"replacement"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"quantity"</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"applicability"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"maybe"</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"description"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"replace `quantitty` with `quantity`"</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"consequence"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"`quantity` names the local `quantity`"</span>
<span class="t-w">    </span><span class="t-p">},</span>
<span class="t-w">    </span><span class="t-p">{</span>
<span class="t-w">      </span><span class="t-nt">"span"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">        </span><span class="t-nt">"file"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"src/shop.ax"</span><span class="t-p">,</span>
<span class="t-w">        </span><span class="t-nt">"start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">8</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">13</span><span class="t-p">],</span>
<span class="t-w">        </span><span class="t-nt">"end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">8</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">22</span><span class="t-p">],</span>
<span class="t-w">        </span><span class="t-nt">"bytes"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">202</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">211</span><span class="t-p">]</span>
<span class="t-w">      </span><span class="t-p">},</span>
<span class="t-w">      </span><span class="t-nt">"replacement"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"quantize"</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"also"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span>
<span class="t-w">        </span><span class="t-p">{</span>
<span class="t-w">          </span><span class="t-nt">"span"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">{</span>
<span class="t-w">            </span><span class="t-nt">"file"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"src/shop.ax"</span><span class="t-p">,</span>
<span class="t-w">            </span><span class="t-nt">"start"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">3</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">1</span><span class="t-p">],</span>
<span class="t-w">            </span><span class="t-nt">"end"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">3</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">1</span><span class="t-p">],</span>
<span class="t-w">            </span><span class="t-nt">"bytes"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span><span class="t-mi">13</span><span class="t-p">,</span><span class="t-w"> </span><span class="t-mi">13</span><span class="t-p">]</span>
<span class="t-w">          </span><span class="t-p">},</span>
<span class="t-w">          </span><span class="t-nt">"replacement"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"use std.tensor.quantize\n"</span>
<span class="t-w">        </span><span class="t-p">}</span>
<span class="t-w">      </span><span class="t-p">],</span>
<span class="t-w">      </span><span class="t-nt">"applicability"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"maybe"</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"description"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"replace `quantitty` with `quantize` and add `use std.tensor.quantize`"</span><span class="t-p">,</span>
<span class="t-w">      </span><span class="t-nt">"consequence"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-s2">"`quantize` names the std `std.tensor.quantize`"</span>
<span class="t-w">    </span><span class="t-p">}</span>
<span class="t-w">  </span><span class="t-p">],</span>
<span class="t-w">  </span><span class="t-nt">"help"</span><span class="t-p">:</span><span class="t-w"> </span><span class="t-p">[</span>
<span class="t-w">    </span><span class="t-s2">"Did you mean `quantity`, or `quantize` from `std.tensor`?"</span>
<span class="t-w">  </span><span class="t-p">]</span>
<span class="t-p">}</span></code></pre>
</figure>
</div>

rustc's object carries the message and the code, and in `code.explanation` the long explanation that
`rustc --explain E0425` prints, as Markdown, the same for every mistake with that code; the marked spans; each
help as a child, with its replacement and how safe it is to apply (`MaybeIncorrect` here); and in `rendered` the
report as the terminal shows it, without colour.

drx's carries the same three sentences as its terminal report: what is wrong in `message`, why in
`explanation`, what to do in `help`. Each suggested edit says what it changes and what the new name will refer
to, and whether `drx fix` may make it alone (`always`) or someone has to choose (`maybe`); here there are two
candidates, so it is `maybe`. The sentences keep their backticks, so a program can tell code from words.
drx's `explanation` is the reason for this mistake, in its own names; the long explanation, with examples, is not
in the JSON: `drx explain` prints it.

## When you want more: `drx explain`

`rustc --explain E0382` prints a longer explanation of a Rust error code. `drx explain` does the same for a
Draconyx one, in the same layout as the report, with an example of the mistake and its fix:

<pre class="term" tabindex="0" role="region" aria-label="drx explain AX0312"><code><span style="color:#8a8a8a">$</span> drx explain AX0312
<span></span>
<span></span><span class="bar" style="border-left-color:#cd3131"><span style="color:#ffffff;background:#cd3131;font-weight:700"> ERROR AX0312 </span>  <span style="color:#ffffff;font-weight:700">A value used after it was given away</span>
<span></span>
A value has one owner at a time. Passing it with <span style="color:#d787d7">take</span> gives it to the
function called, and the name that held it can no longer be read.
<span></span>
For example:
<span></span>
    <span style="color:#d787d7">@doc</span> <span style="color:#87d787">"""Sends `message` and counts the bytes that went out.</span>
    <span style="color:#87d787">  * message - the text to send</span>
    <span style="color:#87d787">"""</span>
    <span style="color:#5fafff">send</span>(<span style="color:#d787d7">take</span> <span style="color:#afd7ff">message</span>: <span style="color:#5fd7d7">String</span>) -&gt; <span style="color:#5fd7d7">Int</span>:
        <span style="color:#5fafff">len_bytes</span>(<span style="color:#afd7ff">message</span>)
<span></span>
    <span style="color:#d787d7">@doc</span> <span style="color:#87d787">"""Sends the same greeting twice."""</span>
    <span style="color:#5fafff">notify</span>() -&gt; <span style="color:#5fd7d7">Int</span>:
        <span style="color:#afd7ff">greeting</span> = <span style="color:#87d787">"Hello"</span>
        <span style="color:#afd7ff">first</span> = <span style="color:#5fafff">send</span>(<span style="color:#d787d7">take</span> <span style="color:#afd7ff">greeting</span>)
        <span style="color:#afd7ff">second</span> = <span style="color:#5fafff">send</span>(<span style="color:#d787d7">take</span> <span style="color:#afd7ff">greeting</span>)
    <span style="color:#cd3131">                  ^^^^^^^^^^^^^</span>
        <span style="color:#afd7ff">first</span> + <span style="color:#afd7ff">second</span>
<span></span>
To fix it, pass the value bare when the function only reads it, and drop
<span style="color:#d787d7">take</span> from its parameter too:
<span></span>
    <span style="color:#d787d7">@doc</span> <span style="color:#87d787">"""Sends `message` and counts the bytes that went out.</span>
    <span style="color:#87d787">  * message - the text to send</span>
    <span style="color:#87d787">"""</span>
    <span style="color:#5fafff">send</span>(<span style="color:#afd7ff">message</span>: <span style="color:#5fd7d7">String</span>) -&gt; <span style="color:#5fd7d7">Int</span>:
        <span style="color:#5fafff">len_bytes</span>(<span style="color:#afd7ff">message</span>)
<span></span>
    <span style="color:#d787d7">@doc</span> <span style="color:#87d787">"""Sends the same greeting twice."""</span>
    <span style="color:#5fafff">notify</span>() -&gt; <span style="color:#5fd7d7">Int</span>:
        <span style="color:#afd7ff">greeting</span> = <span style="color:#87d787">"Hello"</span>
        <span style="color:#afd7ff">first</span> = <span style="color:#5fafff">send</span>(<span style="color:#afd7ff">greeting</span>)
        <span style="color:#afd7ff">second</span> = <span style="color:#5fafff">send</span>(<span style="color:#afd7ff">greeting</span>)
        <span style="color:#afd7ff">first</span> + <span style="color:#afd7ff">second</span>
<span></span>
If the function changes the value, <span style="color:#d787d7">borrow</span> it at both ends instead.
<span></span>
<span style="color:#8a8a8a">(Spec: section 7.4, Ownership Is Linear: Use-After-Move.)</span></span></code></pre>

The mistakes are the same in both languages, and both compilers find them, in your own names, most often with
a fix. What changes is how it is said: plain sentences, with the reason for this mistake right beside it.

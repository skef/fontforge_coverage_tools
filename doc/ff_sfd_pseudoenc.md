# `ff_sfd_pseudoenc`

This tool organizes glyphs that do not have a Unicode mapping, which are
ordinarily displayed by [FontForge][1] in a pile at the end of the view window.
It requires Python 3 but has no other dependencies.

# Table of Contents

* [High-level description](#high-level-description)
* [Requirements and caveats](#requirements-and-caveats)
* [Running the script](#running-the-script)
	* [To change a file](#to-change-a-file)
	* [To check a file](#to-check-a-file)
	* [Other options](#other-options)
* [Configuration files](#configuration-files)
	* [Glyph selection](#glyph-selection)
		* [By name](#by-name)
		* [By Unicode codepoint](#by-unicode-codepoint)
	* [Interactions between selection sections](#interactions-between-selection-sections)
	* [`Top`-level directives](#top-level-directives)
* [How this works and why it is safe](#how-this-works-and-why-it-is-safe)

# High-level description

`ff_sfd_pseudoenc` reads a FontForge `.sfd` file and a “ini” format
configuration file and outputs a modified `.sfd` that displays unencoded glyphs
in a different order, optionally organized into groups. Unencoded glyphs are
those that have no Unicode codepoint, which in FontForge is recorded and
displayed as `-1`. Without intervention, FontForge generally displays unencoded
glyphs at the end of the main window in (roughly) the order they were added. 

Organizing these glyphs be of modest benefit even when a font has only a few of
them, particularly when comparing between different styles (e.g. regular, bold,
and italic). But the intended use-case is a font that has many unencoded glyphs
for any of these reasons:

* “Utility” glyphs included by reference in other glyphs but never displayed
  alone
* Ligatures
* Many character or character set variants (OpenType `salt`, `ssNN`, `cvNN`)
* Proportional and/or oldstyle figures (`onum`, `pnum`, etc.)
* Substantial codepoint subset variants, as with support for smallcaps (`smcp`)

Once there are more than 25 such glyphs it can be difficult to find an
individual one. FontForge does support glyph “Groups” (in the “Encoding” menu)
as a partial work-around, but the interface is clunky, and more importantly the
configuration of groups is stored in the user's configuration rather than in
the font. The application also supports custom encodings, but only up to a
small number of glyphs and (seemingly) not in a way compatible with full
Unicode. `ff_sfd_pseudoenc` gets around these problems by modifying `.sfd`
files directly to influence how unencoded glyphs are displayed, by means of
what could be called a “pseudo-encoding”.

# Requirements and caveats

* The only requirement for running the script itself is Python 3.
* It does not use the `fontforge` Python module (the relevant fields cannot be
  modified through that interface). 
* You must supply a configuration file -- glyph groups cannot be directly
  specified with command-line arguments. 
* It will only work with `.sfd` files with the `ISO 10646-1 (Unicode Full)`
  encoding, listed in the `Encoding:` header as `UnicodeFull`.
* The files must be read and written by FontForge with the `Encoding → Compact` option
  turned off. `Compact` can be used at any other time. 
* If the file is being converted for the first time or was saved incorrectly
  you can just save it as as `Unicode Full`/not-`Compact` and then run the
  script.

# Running the script

When `ff_sfd_pseudoenc` is run without any arguments it acts as a filter,
expecting the contents of a `.sfd` file to be passed as standard input and
writing the modified file to standard output:
```
ff_sfd_pseudoenc < current_file.sfd > new_file.sfd
```
If the `--input` (`-i`) option is specified the `.sfd` file will be read from
that pathname rather than standard input. 

The script will only run when a configuration file is provided, as described
[below](#configuration-files).

## To change a file

By default the modified file will be written to standard output, and can be
saved (on Unix-like systems) this way:
```
ff_sfd_pseudoenc --input input.sfd > saved.sfd
```
Or the output location can be specified with the `--output` (`-o`) flag:
```
ff_sfd_pseudoenc --input input.sfd --output saved.sfd
```
However, the script will return an error if `saved.sfd` already exists. To
override that check use `--overwrite`:
```
ff_sfd_pseudoenc --input input.sfd --output saved.sfd --overwrite
```
Note that the `--output` location must be different from `--input`, but if you
want the modified file to replace the input file you can use `--input` and
`--overwrite` without `--output`:
```
ff_sfd_pseudoenc --input input.sfd --overwrite
```
This saves the output to a temporary file in the same directory and then does a
rename, to minimize (but not eliminate) the chance of corruption. 

## To check a file

When the `--check` flag is added the script will not produce output and only
report any errors and whether the current glyph order is the same as the order
specified in the configuration file. When the order would not change it will
return exit code 0 and when it would and there are no other issues it will
return exit code 3. 

## Other options

* The `--verbose` (`-v`) flag will display more detailed diagnostic messages.
  It can be specified up to three times. 

* The `--silent` flag will turn off all messages, including fatal errors. The
  script will still return exit code 0 on success and non-zero on failure.

* The script normally reads the whole `.sfd` file into memory for the duration
  of execution. To avoid this add the `--memory` flag. When an explicit input
  file is specified it will be read twice, and must not change while the script
  runs. If the file is supplied by standard input a temporary version will be
  saved.

* The `--showconfpath` and `--showblocks` option are described in the next section. 

# Configuration files

To run the script you must supply a configuration file with 'ini' syntax. As
described above you can specify the name of the file with the `--config``
(`-c`) option. Or you can give it any of these names:

* The Font Name, as specified in the `FontName` header, followed by `.ini`.
* The Font Name with spaces replaced by hyphens, by underscores, or omitted,
  followed by `.ini`
* The same as above but with the Full Name, as specified in the `FullName`
  header.
* The same but with the Family name, as specified in the `FamilyName` header.
* `ff_sfd_pseudoenc.ini`

When the `.sfd` is supplied by standard input, the configuration file with one
of these names must be in the “working directory” of the script's execution.
When `--input` is specified the directory of that file will be checked first,
followed by the working directory. Running the script with the `--showconfpath`
option will print the potential configuration file locations for the supplied
`.sfd` file and then exit, as in:
```
Potential config file locations will be checked in this order:
    ../LibertinusSerif-Regular.ini
    ../LibertinusSerif-Regular.ini
    ../LibertinusSerif-Regular.ini
    ../LibertinusSerif-Regular.ini
    ../Libertinus Serif Regular.ini
    ../Libertinus_Serif_Regular.ini
    ../Libertinus-Serif-Regular.ini
    ../LibertinusSerifRegular.ini
    ../Libertinus Serif.ini
    ../Libertinus_Serif.ini
    ../Libertinus-Serif.ini
    ../LibertinusSerif.ini
    ../ff_sfd_pseudoenc.ini
    /home/mary/ft/libertine_complete_revs/LibertinusSerif-Regular.ini
    /home/mary/ft/libertine_complete_revs/LibertinusSerif-Regular.ini
    /home/mary/ft/libertine_complete_revs/LibertinusSerif-Regular.ini
    /home/mary/ft/libertine_complete_revs/LibertinusSerif-Regular.ini
    /home/mary/ft/libertine_complete_revs/Libertinus Serif Regular.ini
    /home/mary/ft/libertine_complete_revs/Libertinus_Serif_Regular.ini
    /home/mary/ft/libertine_complete_revs/Libertinus-Serif-Regular.ini
    /home/mary/ft/libertine_complete_revs/LibertinusSerifRegular.ini
    /home/mary/ft/libertine_complete_revs/Libertinus Serif.ini
    /home/mary/ft/libertine_complete_revs/Libertinus_Serif.ini
    /home/mary/ft/libertine_complete_revs/Libertinus-Serif.ini
    /home/mary/ft/libertine_complete_revs/LibertinusSerif.ini
    /home/mary/ft/libertine_complete_revs/ff_sfd_pseudoenc.ini
```

## Glyph selection

Other than an optional section called `top`, described [below](#top-level-dirctives),
the configuration file should contain a list of glyph selection sections, each
of which specifies which unencoded glyphs are included in what order.

Suppose that an .sfd file contains glyphs with the following names, the first
group Unicode-encoded and the second group unencoded:
```
    zero      one      two     three     four     five     six     seven 
    eight    nine                                                    
      A        B        C        D        E        F        G
      H        I        J        K        L        M        N        O
      P        Q        R        S        T        U        V        W
      X        Y        Z                                                  
               a        b        c        d        e        f        g
      h        i        j        k        l        m        n        o
      p        q        r        s        t        u        v        w
      x        y        z                                           

---

    a.alt   zero.old  one.old  one.fit  two.fit three.fit four.fit five.fit
   six.fit  eight.fit two.old three.old zero.fit seven.fit nine.fit k.sc
     a.sc     b.sc     c.sc     d.sc     e.sc     f.sc     g.sc     h.sc
     i.sc     j.sc     l.sc     m.sc     n.sc     o.sc     p.sc     q.sc
     r.sc     s.sc     t.sc     u.sc     v.sc     w.sc     x.sc     y.sc
     z.sc    q.sup    four.old five.old six.old seven.old eight.old nine.old
     K.alt   R.alt     h.alt    w.alt   J.alt.2  y.alt    W.alt.1  A.alt.1
    one.sc  zero.sc   two.sc   four.sc  six.sc  seven.sc  three.sc five.sc
   eight.sc
```
### By name

The most straightforward way to select unencoded glyphs is by name. This
section
```
[q.sup]
basenames: q.sup
```
selects just the `q.sup` glyph. You can also split the “basename” (before any
dot-extension name) and the extension(s), as in
```
[somealts]
basenames: K R h A
extensions: .alt
```
which selects `K.alt`, `R.alt`, and `h.alt`. Both the basename and the
extension names are case-sensitive. Distinct basenames must be separated by any
combination of commas and/or spaces. Extensions are specified in a single
string that must start with a period. These directives do not select `A.alt.1`
because that name has an *additional* extension. 

You can also select by extension name only, as in
```
[altones]
extensions: .alt.1
```
which selects `A.alt.1` and `W.alt.1`. The matching of extensions is *not*
ordered, so:
```
[altones_]
extensions: .1.alt
```
matches the same set of glyphs. Indeed, both these directives
```
[Aaltone]
basenames: A.alt
extensions: .1
```
and these
```
[Aaltone_]
basenames: A.1
extensions: .alt
```
select `A.alt.1`. 

If you want to select any glyphs that have some extensions among others you can
use `has_extensions`, so
```
[ones]
has_extensions: .1
```
matches W.alt.1 and A.alt.1. You can also select using a regular expression.
`nameregex` operates on the whole glyph name, so
```
[somescs]
nameregex: ^[d-f]\.sc$
```
selects `d.sc`, `e.sc`, and `f.sc`. `baseregex` ignores the extension, so
```
[somescs]
baseregex: ^[g-i]$
```
matches `g.sc`, `h.sc`, and `i.sc`. But you can also combine regular
expressions and extension matching—which is more natural to do with
`baseregex`—as in
```
[morealts]
baseregex: ^[B-X]$
has_extensions: .alt
```
which matches `J.alt.2`, `K.alt`, `R.alt`, and `W.alt.1`. 

The `extensions` directive can be combined with any other besides
`has_extensions`, while `has_extensions` can used on its own or with a regular
expression but not with `basenames` or with Unicode-based selection (discussed
[below](#by-unicode-codepoint)).

#### Ordering and “Holes”

When matching is by extension only or by regular expression, selected glyphs
are displayed in (roughly) alphanumeric order. When matching with `basenames`
selected glyphs are displayed in the specified order. And by default an
element in a `basenames` list that does not select a glyph will be given
an empty slot. The section
```
[somesups]
a.sup q.sup
```
Would therefore normally be displayed as an empty slot followed by `q.sup`. 
To remove any empty slots in a section you can set the `compact` directive
to true, so 
```
[somesups_]
a.sup q.sup
compact: True
```
would display `q.sup` by itself. 

### By Unicode codepoint

For convenince you can also indirectly match by Unicode codepoint. The directive
```
[somepoints]
codepoints: 0x33
```
matches the codepoint for the number 3. With the file specified above this
directive acts indentically to
```
[athree]
basenames: three
```
More generally, specified codepoints are “replaced” by the names of the glyphs
occupying those codepoints. Specifying *only* codepoints therefore has no 
effect, as any glyph with a codepoint is encoded by definition. But it is useful
in conjunction with `extensions`, as in:
```
[threesc]
codepoints: 0x33
extensions: .sc
```
which selects `three.sc`. Codepoints can be specified in ranges with a `-` as
well, and any number of individual points or ranges can be listed if separated
by a combination of commas and/or spaces, so:
```
[morepoints]
codepoints: 0x2e 0x30-0x39
extensions: .sc
```
corresponds to an empty slot (as there is no glyph for the `.` (period)
codepoint) followed by `zero.sc` through `nine.sc`. Adding `compact: True`
would eliminate the blank slot. The (positive) integers can be specified with
any string understood by the python `int()` function when passed base 0, and
therefore normal decimal integers, hexidecimals preceded by `0x`, and octals
preceded by `0o`.

Codepoints can be specified in any order and values can be repeated, but they
are always treated as if they are specified in increasing order without 
overlap. 

Codepoint ranges can also be selected by Unicode block name, as in:
```
[basic_latin]
blocks: Basic Latin
extensions: .sc
```
which is equivalent to `codepoints: 0x20-0x7e`. Block names are case
insensitive. Any number of blocks can be specified separated by (in contrast
with the other directives) a single comma followed by any number of spaces.
They can be listed in any order, but will always be treated as if specified in
order of increasing codepoint. The ``--showblocks`` directive will print the
names of all blocks for reference. 

#### “Narrowing” by General Category

It is also possible to “narrow” the specified codepoints by Unicode “General
Category”, as documented [here][2] and [here][3]. These directives
```
[latin_lower]
blocks: Basic Latin, Latin-1 Supplement, Latin Extended-A, Latin Extended-B
categories: ll
extensions: .sc
```
specify all the glyphs with the `.sc` extension and the same basename as any
glyph with a *lower case* codepoint in the first four Latin blocks. Multiple
categories can be separated by any combination of commas and spaces, selecting
codepoints of *any* of the listed categories. And just entering the first 
letter will select any category starting with that letter.

Among others, this feature makes `ff_sfd_pseudoenc` into not just an
organizational tool but a tracking tool. Any glyph considered to be lower case
is a candidate for a Smallcaps equivalent. With this feature you can not only
easily group all Smallcaps from a given block together, you can also see the
empty slots corresponding to any missing possibilities. (Note that you will
*not* see any empty slots for codepoints *without* corresponding glyphs,
because those have no name to map to.) Of course, if you do not want to
represent those possibilities you can set `compact` to `True`. 

## Interactions between selection sections

All configuration file sections must be given a unique name, and the name `top`
is reserved (see next section). By default each section is first “processed”
and then “displayed” in the order it appears. 

*Processing* is the selection of glyphs by the section. Processing order is
important because a glyph is assigned to the first section that selects it.
Suppose you have these directives:
```
[latin_lower]
blocks: Basic Latin, Latin-1 Supplement, Latin Extended-A, Latin Extended-B
categories: ll
extensions: .sc

[latin_figures]
blocks: Basic Latin
categories: nd
extensions: .sc

[latin_other]
has_extensions: .sc
```
The first selects lower-case latin letters and the second selects “number-like”
figures in the first Latin block. The third is a catch-all that selects any 
*other* glyphs with the `.sc` extension. If the third section were moved before
the first two it would select every `.sc` glyph and the others select none. 

You can change the relative order of processing of a section using the
`process_offset` directive.  These blocks
```
[latin_other]
has_extensions: .sc
process_offset: 2

[latin_lower]
blocks: Basic Latin, Latin-1 Supplement, Latin Extended-A, Latin Extended-B
categories: ll
extensions: .sc

[latin_figures]
blocks: Basic Latin
categories: nd
extensions: .sc
```
select glyphs just as the last ones do, but the `latin_other` section will be
displayed first. `process_offset` can also be negative, which will move the
processing of the section earlier. 

#### Display and `group_align`

*Display* and display order are more self-explanatory. The `display_offset`
directive is analogous to `process_offset`, and (for good or bad) allows file
order, processing order, and display order to be entirely independent.

The only other display-specific directive is `group_align`, which has a default
value of 8. The number of slots assigned to a group will be padded at the end
so that it is evenly divisible by the `group_align` value. It should therefore
be set to a multiple of the number of glyphs a user prefers to see in their
main window. (Or more likely the window should be set according to the chosen
value of `group_align`.)

The main reason to set group_align to another value at the section level is
to visually “merge” their display by setting it to 1. These directives:
```
[latin_lower]
blocks: Basic Latin, Latin-1 Supplement, Latin Extended-A, Latin Extended-B
categories: ll
extensions: .sc
group_align: 1

[latin_figures]
blocks: Basic Latin
categories: nd
extensions: .sc
```
Select figures first and then lowercase letters, but display them as if they were 
a single group. (One could also list the categories `ll` and `nd` together, but 
then the figures would appear before the letters because of their codepoint
orders.

Finally, any unencoded glyphs *not* selected by a section will be listed 
after those of the last section displayed, in the order they would have appeared
in without encoding (roughly the order in which they were added). 

## `Top`-level directives

The optional `top` section can appear anywhere in the configuration file and
contain any of these four directives:

* `group_align`: This sets the default group alignment value, which must be an
  integer greater than 0. It is overridden by the section-level directive and
  overrides the default value of 8.

* `compact`: This sets the default compact value, which must be `True` or
  `False`. It is overridden by the section-level directive and overrides the
  default value of False.

* `process_order`: When present this must contain a list of section names
  separated by commas and/or spaces. Unencoded glyphs will be assigned to
  sections in the specified order. This overrides any section-level
  `process_offset` directives and any section not included in the list will be
  ignored.

* `output_order`: When present this must contain a list of section names
  separated by commas and/or spaces. The glyphs assigned to sections will be
  displayed in the specified order. This overrides any section-level
  `output_offset` directives.

# How this works and why it is safe

Each glyph in a FontForge `.sfd` file is assigned three numbers on its
`Encoding` line. The documentation for this directive says:

> [The Encoding line] gives the encoding, first in the current font,
> then in unicode, and finally the original position (GID).

Using the `ISO 10646-1 (Unicode Full)` encoding, the second number will
be the Unicode codepoint for the glyph if it has one or -1 if it doesn't.
Without intervention the first number is equal to the second when the latter is
greater than -1, and therefore just repeats the Unicode assignment.

When the second number equals -1 the first is some number greater than
0x10FFFF—the highest codepoint value so far—loosely determined by the order in
which the glyph was added. It is actually *this number* that determines the
“slot” in which an unencoded glyph is displayed. All `ff_sfd_pseudoenc`
modifies is this number, and only when the second is -1. (Well, almost—the
`BeginChars` header has a value that corresponds to the maximum of these first
encoding numbers, and that is also set as needed.

This solution is *stable* because FontForge will not “reencode” a font
unless you tell it to, so as long as you save with the right encoding 
the values will not change. (And if you save the file wrong you can just
re-save it correctly and then run the script on it again.) 

The solution is *safe* because the default encoding values were arbitrary
anyway—they have no real semantic value other than influencing the display. (Or
to look at the question another way, if they were not essentially arbitrary for
a “UnicodeFull” encoding there would be some interface for changing them.)

[1]: https://fontforge.github.io
[2]: https://www.unicode.org/versions/Unicode11.0.0/ch04.pdf#G134153
[3]: https://en.wikipedia.org/wiki/Unicode_character_property#General_Category

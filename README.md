FontForge Coverage Tools
========================

This repository and Python package is a home for tools that support
[FontForge][1] font development. More narrowly, these tools address or work
around some of the limitations and annoyances of FontForge when a font has many
glyphs. 

The author contributes to a free font and is building these scripts along the
way. The (expected) eventual focus will be on unifying the specification of
precomposed and composing Unicode characters. However, as of this initial
release there is just a single script to organize unencoded glyphs.

List of Tools
=============

`ff_sfd_pseudoenc`
------------------

This tool allows a user to organize glyphs that do not have a Unicode mapping,
which are ordinarily displayed by FontForge in a pile at the end of the view
window. It requires Python 3 but has no other dependencies, and is documented
[here](doc/ff_sfd_pseudoenc.md).

[1]: https://fontforge.github.io

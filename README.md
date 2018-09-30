# FontForge Coverage Tools

This repository and Python package is a home for tools that support
[FontForge](https://fontforge.github.io) font development. More narrowly, these
tools address or work around some of the limitations and annoyances of
FontForge when a font has many glyphs. 

The repository's official home is on
[GitHub](https://github.com/skef/fontforge_coverage_tools), which is also the
best place to read this documentation. 

The author contributes to a free font and is building these scripts along the
way. The (expected) eventual focus will be on unifying the specification of
pre-composed and composing Unicode characters. However, as of this initial
release there is just a single script to organize unencoded glyphs.

# List of Tools

* [`ff_sfd_pseudoenc`](doc/ff_sfd_pseudoenc.md)

This tool allows a user to organize glyphs that do not have a Unicode mapping,
which are ordinarily displayed by FontForge in a pile at the end of the view
window. It requires Python 3 but has no other dependencies.

# Author

The repository is written and maintained by Skef Iterum. Questions about or
contributions to these tools should be communicated through the GitHub
interfaces for the repository.

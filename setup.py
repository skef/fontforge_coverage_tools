from distutils.core import setup

setup(
    name='fontforge_coverage_tools',
    description='Utilities to aid high-glyph-count FontForge development',
    url='http://github.com/skef/fontforge_coverage_tools',
    author='Skef Iterum',
    author_email='github@skef.org',
    license='Modified BSD',
    scripts=['bin/ff_sfd_pseudoenc'],
    python_requires='>=3'
)

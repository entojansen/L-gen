I) Dependencies ---------------------------------------------------------------

This application requires the following software:
1) Python 3 - https://www.python.org/download/releases/3.0/
MacOS comes with this by default.

Python 3 modules needed:
pylatex - to install this module on MacOS, open terminal and run the following command:
python -m pip install pylatex

2) Perl - https://www.activestate.com/products/perl/ or https://strawberryperl.com/
MacOS and most Linux distros comes with this by default.

3) LaTeX - https://miktex.org/download
MikTex is preferred for ease of use and installation.
During installaion, allow MikTex to either autoinstall or ask for permission to install missing packages.
Otherwise, use the MikTex package manager (use search bar) to ensure all necessary packages and their dependencies are installed.

LaTeX packages used:
memoir
fontenc
inputenc
microtype
geometry
savetrees
libertine
helvet
nimbusmononarrow
multicol
expl3
keyval
pdflatex


II) Useage --------------------------------------------------------------------
The core structure of this program is tripartite, as follows:
1) L-gen.py
2) xxxxx.format
3) xxxxx.tex


Column names cannot contain characters other than normal upper/lower-case latin alphabet (no numbers or symbols)



I) Dependencies ---------------------------------------------------------------

This application requires the following software:

1) Python 3 - https://www.python.org/download/releases/3.0/
MacOS comes with this by default.

Python modules needed:
pylatex - to install this module on MacOS, open terminal and run the following command:
python -m pip install pylatex

2) Perl - https://www.activestate.com/products/perl/ or https://strawberryperl.com/
MacOS and most Linux distros come with this by default.

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


II) Structure -----------------------------------------------------------------

The core structure of this program is tripartite, as follows:

1) ./src/L-gen.py
2) ./src/*.format (and/or ./src/format.txt)
3) ./out/*.tex

The python script [L-gen.py] searches for Excel files in the source folder [./src/*.xlsx], as well as a corresponding format file [./src/*.format] for each workbook.
For each Excel file used as input, the script writes a separate PDF file to the output folder [./out/*.pdf], along with the LaTeX source code [./out/*.tex].

1) L-gen.py
This file contains three functions that perform all data-handling operations and write output:

read_data(ext=[".xls", ".xlsx", ".xlsm", ".xlsb", ".odf", ".ods", ".odt"]):

	First in the main() function, read_data() searches and reads all Excel files contained in the source folder (but not in sub-directories).
	pandas.read_excel() is used as the read-in function for Excel formats.
	Any of the file types in list(ext) can be used and are compatible with the preceding read function.
	Note that CSV and TXT files are not included and not compatible with this program.
	Excel files are limited to a single sheet for use with L-gen.py due to internal use of the pandas.read_excel() function, which will read only the first sheet by default.
	All data is stored in a dictionary of pandas dataframes, with key-val pairs {"filename": dataframe}, and passed to function make_labels() below.

read_format(file="format.txt"):

	Within the main() function, a for loop iterates through the dictionary of dataframes and searches for a format file matching each Excel file.
	If a matching file is not found, the function searches for a default file called "format.txt", which serves as a generic formatting file.
	A generic format circumvents the need to have a matching format file for every single input file if the same format is used across input files.
	The format file is read as a dictionary and passed to make_labels() within the for loop.

make_labels(form, name, data):

	A single format file, filename, and dataframe are used to generate a PDF of labels and output LaTeX source code.
	The LaTeX file can be edited later to adjust formatting of individual label series, as desired.
	The package pylatex is used for LaTeX source generation and PDF file output with a compiler of choice (pdflatex, xetex, luatex, etc.).
	If the compiler is specified as latex, a DVI file will be created instead of a PDF file.

2) *.format / format.txt
There are 4 sections in each format file, consisting of lines containing commands formatted as: key %% value.
Examples, defaul values, and full explanations of their functionality are described in section III, below.

Mandatory commands:

	These commands must be included and specified in order for the script to run.
	Keywords in this section are used to specify fonts, text size, page geometry, and choice of TeX compiler.

Optional column modifiers:

	This section consists of a single line read into python as a dictionary using eval().
	The key: val pairs within this dictionary are formatted as "column_name": formula.
	For each column name specified, the given formula is applied to every value in the corresponding column.
	This is especially important for formatting dates and GPS coordinates.

Data inclusion:

	This section indicates which columns are used to generate entries (called lines) in the labels.
	Each keyword the name of a line, which is paired with the columns that will be used in that line.
	Specific formatting of the text is given in the next section.
	The arguments are passed to LaTeX to generate macros corresponding to each line, with column names as keys.
	The values are set using data read from the spreadsheet and written, for every row in the sheet, into the TeX file.

Layout formatting:

	This section sets the formatting of each line, using raw LaTeX code that is copied directly into the preable of the TeX file.
	The code indicated for each line is separated from other lines by a newline character, inserted automatically by the python script.
	An arbitrary number of lines is possible, but any variables used in a line must be specified with a matching line name in the previous section.
	Column names from the previous section are used to generate variables that are arranged/formatted as desired within a line.
	Specific values are filled in and printed based on the entries in the spreadsheet.

3) *.tex
The TeX source code used to generate a printable file is divided into a preamble and main document.
The preamble is where packages are called for later use, commands are newly created (or redefined), and formatting options are set.
In this implementation, the preamble is used to define a label environment, variables for use in the labels, and a command to generate the label.

The main body of the document is where these commands are executed; execution itself takes place in two parts.
Variables are supplied wth values from the spreadsheet, which are reprinted into the TeX file.
Label environments are then generated, populated, and repeated in series to yield the final product (a printable file).


III Useage --------------------------------------------------------------------

To use this software successfully, there are two critical components that will always need to be modified.
First, the spreadsheets themselves need to be formatted appropriately for use, and, second, the formatting files need to be completed.
Formatting the spreadsheets is comparatively simple, requiring only the addition of a single column and possibly renaming others to remove numbers and special characters.
Thus, the majority of this section is dedicated to providing a thorough explanation of how to modify and use the formatting files.
Each part of the format files will be discussed in detail, including default values, functionality, implementation, and data handling in both python and tex code.

1) Spreadsheet formatting
There are 2 considerations for the spreadsheets used for label generation; namely, special characters and the NumLabels column

Special characters:

	In general, special characters are not guaranteed to print if entered into the spreadsheet, although the tex file is UTF-8 compatible.
	It is recommended to use only alphanumeric characters (latin alphabet, arabic numerals) and standard punctuation, where possible.
	Accent characters and greek characters should function as intended, but this is not a given and will partly depend on the host system.

	Most importantly, the column names must be alphabetical only!
	Because of how LaTeX is implemented here, column names in the spreadsheet cannot contain characters other than upper/lower-case latin alphabet letters (no numbers or symbols).
	Note however that not every column needs to be used or called in the format file; therefore only the columns used to make labels need to follow this rule.

NumLabels Column:

	The number of labels generated for each row is controlled by a column called NumLabels (exactly as shown here), which should ideally be the first column in every input file.
	To indicate that no labels should be made for a given row in the spreadsheet, the pound sign # is entered rather than a number.
	This causes the line to be interpreted as a comment, and it is skipped by the read_excel() function, rather than being read into memory.

	If NumLabels is not the first column and # is indicated, any data following the # character will be interpreted as a comment and not read.
	This will cause an incomplete read of the line and yield either an error or an incomplete label.
	Alternatively, the number 0 can be used to indicate that no labels should be made for a row.
	This is less memory efficient (and slower) but allows NumLabels to be placed as any column in the spreadsheet.
	Entering a value of 0 will simply cause a blank line to be printed in the PDF file, rather than a series of labels.

2) Format files
This file (or set of files) contains commands used to control the data included, layout, and format of the labels generated from each input spreadsheet.
Having these files obviates the need to adjust the core python script every time a different layout is desired for a new dataset.
At the same time, these files allow for multiple label types to be created from a series of spreadsheets in a single run.

General notes:

	Format files are constructed from a series of key/value pairs read into a python dictionary.
	Each line should contain exactly one key/value pair.
	The values are used to either modify or directly write onto the TeX file, as described below.

	L-gen.py searches for the "%%" delimiter to identify which lines contain a key:val pair for parsing into a dictionary.
	If "%%" is not present on a line, the line is interpreted as a comment and skipped.
	The order of the lines and content of non-reading lines are not important.

Mandatory commands:

	As the name suggests, these commands must be present in the file to run L-gen.py and write the TeX file.
	
	pg_size %% letterpaper
	pg_margins %% left=1cm,right=1cm,top=0.8cm,bottom=0.8cm
	font_rm %% libertine
	font_sf %% helvet
	font_tt %% nimbusmononarrow
	sans_serif %% 1
	compress_cols %% 1
	font_size %% 3pt
	font_skip %% 4pt
	label_w_max %% 45pt
	label_h_max %% 27.5pt
	baselinestretch %% 0.76
	cols %% 12
	col_sep %% 0.01cm
	compiler %% pdflatex
	

Optional column modifiers:


Data inclusion:

Layout formatting:

	A "line" here means a single formatted entry on the label, which may span more than one line on the printed page.


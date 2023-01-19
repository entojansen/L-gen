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
The values used in the sections below are tailored to a debugging sample based on a subset of target user input.
Below, each command, value in format.txt (i.e., the "default" format), function, and use in TeX or python is explained.
Verbatim code in LaTeX is put in double square brackets [[]], while verbatim code in python is placed in double angle brackets <<>>.

General notes:

	Format files are constructed from a series of key/value pairs read into a python dictionary.
	Each line should contain exactly one key/value pair.
	The values are used to either modify or directly write onto the TeX file, as described below.

	L-gen.py searches for the "%%" delimiter to identify which lines contain a key:val pair for parsing into a dictionary.
	If "%%" is not present on a line, the line is interpreted as a comment and skipped.
	The order of the lines and content of non-reading lines are not important.

Mandatory commands:

	As the name suggests, these commands must be present in the file to run L-gen.py and write the TeX file.
	These commands are largely related to global formatting and package options and are set in the preamble of the TeX file.

	pg_size %% letterpaper

		Determines the page size used when setting the document paper size in LaTeX.
		Many other options available; e.g., "a4paper" for A4 paper size.

		Read into python and called in function make_labels() : <<doc_options = ["10pt", form["pg_size"]]>>
		*Note -- <<form>> is the name of the dictionary containing key/value pairs from the formatting file; i.e., <<form = {... "pg_size": "letterpaper", ...}>>

		Used by pylatex : <<doc = pl.Document(documentclass="memoir", document_options=doc_options, ...)>>
		*Note -- <<pl>> is handle for pylatex module as set by <<import pylatex as pl>>

		Writes TeX command : [[\documentclass[10pt,letterpaper]{memoir}%]]

	pg_margins %% left=1cm,right=1cm,top=0.8cm,bottom=0.8cm

		Sets page margins using the [[geometry]] package in LaTeX.
		Can be adjusted to use any value; units include mm, in, pt, em, &c...

		Called and used by pylatex : <<doc = pl.Document(documentclass="memoir", ... geometry_options=form["pg_margins"])>>

		Writes TeX commands : [[\usepackage{geometry}%
								\geometry{left=1cm,right=1cm,top=0.8cm,bottom=0.8cm}%]]

	font_rm %% libertine

		Sets the "roman modern" font (i.e., serif font) to Linux Libertine using the [[libertine]] package.
		Specifically calls a font package that must be installed separately, and can be exchanged with other font packages; e.g., [[palatino]].

		Called and used by pylatex : <<doc.packages.append(pl.Package(form["font_rm"]))>>

		Writes TeX command : [[\usepackage{libertine}%]]

	font_sf %% helvet

		Sets the sans serif font to Helvetica using the [[helvet]] package.
		Specifically calls a font package that must be installed separately, as described above.
		Sans serif fonts scaled by 0.95 to match serif fonts.

		Called and used by pylatex : <<doc.packages.append(pl.Package(form["font_sf"], "scaled=0.95"))>>

		Writes TeX command : [[\usepackage[scaled=0.95]{helvet}%]]

	font_tt %% nimbusmononarrow

		Sets the sans serif font to Nimbus 15 Mono Narrow using the [[nimbusmononarrow]] package.
		Specifically calls a font package that must be installed separately, as described above.

		Called and used by pylatex : <<doc.packages.append(pl.Package(form["font_tt"]))>>

		Writes TeX command : [[\usepackage{nimbusmononarrow}%]]

	sans_serif %% 1

		Specifies whether or not to make sans serif font the default font for the document.
		A value of 0 leaves serif fonts as the document font by default.
		A value of 1 changes the document font to the sans serif font by default.

		Called and used by pylatex :  <<if int(form["sans_serif"]):
											sans_cmd = pl.UnsafeCommand("renewcommand", [r"\familydefault", r"\sfdefault"])
											doc.preamble.append(sans_cmd)
										else:
											pass>>

		If set to 1, writes TeX command : [[\renewcommand{\familydefault}{\sfdefault}%]]
		Else if set to 0, no command is written, since document default is serif font.

	compress_cols %% 1

		Specifies whether or not to "compress" columns in document by removing empty spaces between labels.
		Normally, label dimensions are defined by width and height, which enforces the size of the invisible box around the text.
		Compression allows the text to flow without extra space between labels, and the invisible box is set equal to the height of the text.
		Normal colums are nice for cutting labels with wide margins, or using a paper cutter because the labels form a neat grid.
		Compressed columns are better for cutting strips of labels with scissors, with minimal white space, and for saving paper (grid alignment is not enforced).

		-------------
		|			|	
		|	Normal	|		-------------
		|			|		| Compress	|
		-------------	vs	-------------
		|			|		| Compress	|
		|	Normal	|		-------------
		|			|
		-------------

		Called and used by pylatex :  <<if int(form["compress_cols"]):
											lab_box_def = r"\parbox[t]{\format@width}{#1}\newline\newline"
										else:
											lab_box_def = r"\parbox[t][\format@height]{\format@width}{#1}\newline"

										lab_box_cmd = pl.UnsafeCommand("newcommand", r"\labelbox", options=1, extra_arguments=lab_box_def)
										doc.preamble.append(lab_box_cmd)>>

		If set to 1, writes TeX command : [[\newcommand{\labelbox}[1]{\parbox[t]{\format@width}{#1}\newline\newline}%]]
		Else if set to 0, write instead : [[\newcommand{\labelbox}[1]{\parbox[t][\format@height]{\format@width}{#1}\newline}]]
		*Note -- [[\newline\newline]] adds a thin extra space between labels in compressed columns for ease of cutting.

	font_size %% 3pt

		Sets the font size to 3pt.
		Implementation is surprisingly complex, and relies on the memoir document class.
		Memoir class allows arbitrarily small fonts to be set.
		A group of key/val pairs called [[format]] is then created in LaTeX, with the key [[fsize]] set equal to the desired font size.
		To reference this stored vale, a new command [[\fsize]] is created in the preamble.
		This new command is finally used in the document section to set the font.

		Called and used by pylatex :  <<doc = pl.Document(documentclass="memoir", font_size=r"fontsize{\fsize}{\fskip}\selectfont", ...)

										...

										format_extra_args = "NumLabels,height,width,fsize,fskip,stretch,cols"
										format_def = pl.UnsafeCommand(r"define@cmdkeys", r"format", options=r"format@", extra_arguments=format_extra_args)
										doc.preamble.append(format_def)

										format_args = ["format", (... + "fsize={},".format(form["font_size"]) + ...)]
										format_cmd = pl.base_classes.Command("setkeys", arguments=format_args)
										doc.preamble.append(format_cmd)

										...

										fsize_cmd = pl.UnsafeCommand("newcommand", r"\fsize", extra_arguments=r"\format@fsize")

										...

										doc.preamble.append(fsize_cmd)>>

		Writes TeX commands : [[\define@cmdkeys{format}[format@]{NumLabels,height,width,fsize,fskip,stretch,cols}%
								\setkeys{format}{height=27.5pt,width=45pt,fsize=3pt,fskip=4pt,stretch=0.76,cols=12}%
								\newcommand{\fsize}{\format@fsize}%

								...

								\begin{document}%
									\pagestyle{empty}%
									\fontsize{\fsize}{\fskip}\selectfont%

									...

								\end{document}]]

		*Note -- The first 3 lines in the verbatim TeX code are written by all but the first line of python code, which actually sets the font size in the document.
				 This was done to avoid writing any formatting values directly into the document section, thus restricting formatting parameters to the preamble.
	
	font_skip %% 4pt

		Sets the line height/skip to 4pt.
		Similar to previous command in implementation.
		A group of key/val pairs called [[format]] is then created in LaTeX, with the key [[fskip]] set equal to the desired font size.
		To reference this stored vale, a new command [[\fskip]] is created in the preamble.
		This new command is finally used in the document section to set the font.

		Called and used by pylatex :  <<doc = pl.Document(documentclass="memoir", font_size=r"fontsize{\fsize}{\fskip}\selectfont", ...)

										...

										format_extra_args = "NumLabels,height,width,fsize,fskip,stretch,cols"
										format_def = pl.UnsafeCommand(r"define@cmdkeys", r"format", options=r"format@", extra_arguments=format_extra_args)
										doc.preamble.append(format_def)

										format_args = ["format", (... + "fskip={},".format(form["font_skip"]) + ...)]
										format_cmd = pl.base_classes.Command("setkeys", arguments=format_args)
										doc.preamble.append(format_cmd)

										...

										fsize_cmd = pl.UnsafeCommand("newcommand", r"\fskip", extra_arguments=r"\format@fskip")

										...

										doc.preamble.append(fskip_cmd)>>

		Writes TeX commands : [[\define@cmdkeys{format}[format@]{NumLabels,height,width,fsize,fskip,stretch,cols}%
								\setkeys{format}{height=27.5pt,width=45pt,fsize=3pt,fskip=4pt,stretch=0.76,cols=12}%
								\newcommand{\fsize}{\format@fsize}%

								...

								\begin{document}%
									\pagestyle{empty}%
									\fontsize{\fsize}{\fskip}\selectfont%

									...

								\end{document}]]

		*Note -- As before, this was done to restrict formatting parameters to the preamble.
	
	label_w_max %% 45pt

		Sets the maximum label box width t0 45pt, which looks good for this set of labels.
		This parameter is most likely to need adjustment to fit user needs and is largely aesthetic.
		As before, a formatting parameter and command are created to access this value.
		This value is referenced in the preamble when the [[\labelbox]] command is created (see compress_cols above).

		Called and used by pylatex :  <<format_extra_args = "NumLabels,height,width,fsize,fskip,stretch,cols"
										format_def = pl.UnsafeCommand(r"define@cmdkeys", r"format", options=r"format@", extra_arguments=format_extra_args)
										doc.preamble.append(format_def)

										format_args = ["format", (... + "width={},".format(form["label_w_max"]) + ...)]
										format_cmd = pl.base_classes.Command("setkeys", arguments=format_args)
										doc.preamble.append(format_cmd)

										...

										if int(form["compress_cols"]):
											lab_box_def = r"\parbox[t]{\format@width}{#1}\newline\newline"
										else:
											lab_box_def = r"\parbox[t][\format@height]{\format@width}{#1}\newline">>

		Writes TeX commands : [[\define@cmdkeys{format}[format@]{NumLabels,height,width,fsize,fskip,stretch,cols}%
								\setkeys{format}{height=27.5pt,width=45pt,fsize=3pt,fskip=4pt,stretch=0.76,cols=12}%

								...

								\newcommand{\labelbox}[1]{\parbox[t]{\format@width}{#1}\newline\newline}%]]

		*Note -- If compress_cols set to 0, write instead : [[\newcommand{\labelbox}[1]{\parbox[t][\format@height]{\format@width}{#1}\newline}]].

	label_h_max %% 27.5pt

		Sets the maximum label box height to 27.5pt, which looks good for this set of labels.
		Identical in implementation as previous, but only called in TeX if compress_cols is set to 0.
		In other words, labels are given a set height only if the columns are not compressed.

		Called and used by pylatex :  <<format_extra_args = "NumLabels,height,width,fsize,fskip,stretch,cols"
										format_def = pl.UnsafeCommand(r"define@cmdkeys", r"format", options=r"format@", extra_arguments=format_extra_args)
										doc.preamble.append(format_def)

										format_args = ["format", ("height={},".format(form["label_h_max"]) + ...)]
										format_cmd = pl.base_classes.Command("setkeys", arguments=format_args)
										doc.preamble.append(format_cmd)

										...

										if int(form["compress_cols"]):
											lab_box_def = r"\parbox[t]{\format@width}{#1}\newline\newline"
										else:
											lab_box_def = r"\parbox[t][\format@height]{\format@width}{#1}\newline">>

		Writes TeX commands : [[\define@cmdkeys{format}[format@]{NumLabels,height,width,fsize,fskip,stretch,cols}%
								\setkeys{format}{height=27.5pt,width=45pt,fsize=3pt,fskip=4pt,stretch=0.76,cols=12}%]]

		*Note -- Label height is invoked only if compress_cols set to 0 : [[\newcommand{\labelbox}[1]{\parbox[t][\format@height]{\format@width}{#1}\newline}]].

	baselinestretch %% 0.76

		Formats the inter-line spacing by the amount specified; adjusted based on aesthetic preferences.
		In this case the line spacing is reduced to 0.76 to account for smaller font height.
		Used as a formatting parameter in LaTeX as described above.

		Called and used by pylatex :  <<format_extra_args = "NumLabels,height,width,fsize,fskip,stretch,cols"
										format_def = pl.UnsafeCommand(r"define@cmdkeys", r"format", options=r"format@", extra_arguments=format_extra_args)
										doc.preamble.append(format_def)

										format_args = ["format", (... + "stretch={},".format(form["baselinestretch"]) + ...)]
										format_cmd = pl.base_classes.Command("setkeys", arguments=format_args)
										doc.preamble.append(format_cmd)

										...

										stretch_cmd = pl.UnsafeCommand("renewcommand", [r"\baselinestretch", r"\format@stretch"])
										doc.preamble.append(stretch_cmd)>>

		Writes TeX commands : [[\define@cmdkeys{format}[format@]{NumLabels,height,width,fsize,fskip,stretch,cols}%
								\setkeys{format}{height=27.5pt,width=45pt,fsize=3pt,fskip=4pt,stretch=0.76,cols=12}%

								...

								\renewcommand{\baselinestretch}{\format@stretch}%]]


	cols %% 12

		This command defines the number of columns in the document with a maximum 20 columns.
		Used by the LaTeX package [[multicol]], in a [[multicols*]] environment, which fills each column before moving to the next.
		The [[multicols]] environment (without the *, and not used here) will distribute text evenly between columns to fill out each row.
		Formatted with other parameters and called in the document section of the TeX file.

		Called and used by pylatex :  <<format_extra_args = "NumLabels,height,width,fsize,fskip,stretch,cols"
										format_def = pl.UnsafeCommand(r"define@cmdkeys", r"format", options=r"format@", extra_arguments=format_extra_args)
										doc.preamble.append(format_def)

										format_args = ["format", (... + "cols={}".format(form["cols"]))]
										format_cmd = pl.base_classes.Command("setkeys", arguments=format_args)
										doc.preamble.append(format_cmd)

										...

										cols_cmd = pl.UnsafeCommand("newcommand", r"\cols", extra_arguments=r"\format@cols")

										...

										doc.preamble.append(cols_cmd)

										...

										with doc.create(MultiCol(arguments=pl.utils.NoEscape(r"\cols"))) as mcols:
											... >>>>

		Writes TeX commands : [[\define@cmdkeys{format}[format@]{NumLabels,height,width,fsize,fskip,stretch,cols}%
								\setkeys{format}{height=27.5pt,width=45pt,fsize=3pt,fskip=4pt,stretch=0.76,cols=12}%

								...

								\newcommand{\cols}{\format@cols}%

								...

								\begin{document}%

								...

									\begin{multicols*}{\cols}%

									...

									\end{multicols*}%
								\end{document}]]

	col_sep %% 0.01cm

		Sets the amount of extra spacing between adjacent columns.
		Adjusted based on aesthetic preferences, and minimized in this case.

		Called and used by pylatex : <<col_sep_cmd = r"\setlength{\columnsep}{" + "{}".format(form["col_sep"]) + r"}">>

		Writes TeX command : [[\setlength{\columnsep}{0.01cm}%]]

	compiler %% pdflatex

		Indicates the preferred compiler for the TeX file.
		Normally pdflatex is used to generate PDF files, but xetex and luatex are also suitable options.
		If the compiler is set to "latex", a DVI file will be produced instead.

		Called and used by pylatex to compile TeX file : <<doc.generate_pdf(..., compiler=form["compiler"])>>


Optional column modifiers:

	The optional column modifiers specified by val_mods are formulae that are applied to every value in a given column of the spreadsheet.
	These are called only in python and do not interact at all with the TeX file.
	Because these formulae are specified in the format file, they are implemented in the make_labels() function.
	For clarity and explanation, each key/val pair in the dictionary is placed on a new line.
	However, the entry for val_mods in the format file should be placed on a single line, unlike the example below:
	
		val_mods %% {"Latitude": "'{:.5f}'.format(val)",
					 "Longitude": "'{:.5f}'.format(val)",
					 "DateCollected": "val.strftime('%d/%m/%Y')",
					 "DateCollEnd": "val.strftime('%d/%m/%Y') if hasattr(val,'strftime') else val"}

	This command is read verbatim and evaluated to create a python dictionary.
	The key/val pairs correspond to the name of the column needing modification and the formula to be used.
	Due to the use of eval() to read the values, the names and formulae must be put in double quotation marks: ""
	If a string is used in a formula for formatting purposes, the string should be delimited with single quotation marks: ''
	The python variable <<val_mods>> is created as follows:

		<<try:
			  val_mods = eval(form["val_mods"])
			  for func in val_mods:
				  data[func] = data[func].apply(lambda val: eval(val_mods[func]))
		  except KeyError:
			  pass>>

		*Note -- <<form>> is the dictionary creaded from the formatting file, while <<data>> is the pandas dataframe created from the spreadsheet.

	The line <<data[func] = data[func].apply(lambda val: eval(val_mods[func]))>> can be written in pseudocode as:

		column = column.apply(formula), where the formula comes from val_mods.

	Thus, the values in the column are overwritten with new values that have the formula applied to them.
	To achieve this, a funciton is defined and called using <<lambda>>; e.g., (lambda x: x + 1), which adds 1 to each value <<x>>.
	The funcitons used in the default file (format.txt) have two roles.
	First, the coordinates found in columns "Latitude" and "Longitude" are formatted to display 5 decimal places with standard string formatting.
	Second, the dates found in columns "DateCollected" and "DateCollEnd" are formatted to display "mm/dd/yyyy", using the .strftime method.
	*Note -- "DateCollEnd" has some values that are null dates (00/00/00).
			 These are not printed, as explained in Layout formatting, below.
			 However, they can cause issues with .strftime because they are not read by excel as dates (just as text).
			 A check is performed to veryify whether .strftime is a valid attribute for the value, and formatted only if so.

Data inclusion:

	line_a_cols %% Country,AdmOne
	line_b_cols %% LocalityName,DateCollected,DateCollEnd
	line_c_cols %% Latitude,Longitude
	line_d_cols %% CollectedBy
	line_e_cols %% Method,Habitat
	line_f_cols %% ElevationM,CollectionCode

Layout formatting:

	A "line" here means a single formatted entry on the label, which may span more than one line on the printed page.

	line_a_form %% \textbf{\MakeUppercase{\LineA@Country:}}~\LineA@AdmOne
	line_b_form %% \def\nulldate{00/00/00} {\LineB@LocalityName}, \LineB@DateCollected {\ifx\LineB@DateCollEnd\nulldate \else{~--~\LineB@DateCollEnd}\fi}
	line_c_form %% \texttt{\fontsize{3.25pt}{3pt}\selectfont \LineC@Latitude, \LineC@Longitude}
	line_d_form %% \LineD@CollectedBy
	line_e_form %% \def\nullmethod{} {\ifx\LineE@Method\nullmethod \else{\LineE@Method~-- }\fi}{\LineE@Habitat}
	line_f_form %% \LineF@ElevationM, \LineF@CollectionCode

# -*- coding: utf-8 -*-
"""
L-gen.py
Automated locality label generation
by Andrew Jansen, PhD
Dec. 2022
V1
"""

from os import listdir as ld
from pandas import read_excel
import pylatex as pl
from string import whitespace as str_ws
import warnings


# suppress warnings from pandas re: extensions not known by system
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


class MultiCol(pl.base_classes.Environment):
    _latex_name = 'multicols*'


class LabelBox(pl.base_classes.CommandBase):
    _latex_name = "labelbox"


class LabelGen(pl.base_classes.CommandBase):
    _latex_name = "lgen"


class Repeat(pl.base_classes.CommandBase):
    _latex_name = "Repeat"


def read_data(ext=[".xls", ".xlsx", ".xlsm", ".xlsb", ".odf", ".ods", ".odt"]):
    # insert docstring here
    files = [fn for fn in ld(".") if any([e in fn for e in ext])]
    # note, Excel file cannot be read if open elsewhere!
    data = [read_excel(fn, comment="#").dropna(how="all").fillna("")
            for fn in files]
    ddict = dict(zip(files, data))
    return ddict


def read_format(file="format.txt"):
    '''
    Func: read_format() accepts a file name as input, opens the file and
          converts the keyword=value lines into dict entries for later use.
          Functionally this enables user input to control label style and
          format from an external file, which is critical because the final
          package will be converted into a standalone ".exe" file.

    Parameters
    ----------
    file : str, optional
        Name of file containing label formatting parameters passed to LaTex.
        The default is "format.txt".

    Returns
    -------
    fdict : dict
        Dictionary object containing parsed data from formatting file.

    '''

    fdict = {}
    with open(file, "r") as formatting:
        for line in formatting:
            if "%%" in line:
                fkey, fval = line.split(r"%%")
                fdict[fkey.strip(str_ws)] = fval.strip(str_ws)
            else:
                pass

    return fdict


def make_labels(form, name, data):
    doc_options = ["10pt", form["pg_size"]]

    doc = pl.Document(documentclass="memoir",
                      document_options=doc_options,
                      font_size=r"fontsize{\fsize}{\fskip}\selectfont",
                      lmodern=False,
                      textcomp=False,
                      microtype=True,
                      page_numbers=False,
                      geometry_options=form["pg_margins"])

    doc.packages.append(pl.Package("savetrees"))
    doc.packages.append(pl.Package(form["font_rm"]))
    doc.packages.append(pl.Package(form["font_sf"], "scaled=0.95"))
    doc.packages.append(pl.Package(form["font_tt"]))

    if int(form["sans_serif"]):
        sans_cmd = pl.UnsafeCommand("renewcommand", [r"\familydefault",
                                                     r"\sfdefault"])
        doc.preamble.append(sans_cmd)
    else:
        pass

    doc.packages.append(pl.Package("multicol"))
    col_sep_cmd = r"\setlength{\columnsep}{" + \
        "{}".format(form["col_sep"]) + r"}"
    doc.preamble.append(pl.utils.NoEscape(col_sep_cmd))
    doc.preamble.append(pl.utils.NoEscape(r"\setlength{\parindent}{0pt}"))
    doc.preamble.append(pl.utils.NoEscape(r"\setlength{\parskip}{0pt}"))

    doc.packages.append(pl.Package("expl3"))
    repeat_cmd = r"\cs_new_eq:NN \Repeat \prg_replicate:nn"
    doc.preamble.append(pl.utils.NoEscape(r"\ExplSyntaxOn"))
    doc.preamble.append(pl.utils.NoEscape(repeat_cmd))
    doc.preamble.append(pl.utils.NoEscape(r"\ExplSyntaxOff"))

    doc.packages.append(pl.Package("keyval"))

    doc.preamble.append(pl.utils.NoEscape(r"\makeatletter"))

    line_keys = []
    for key in sorted(form.keys()):
        if key[0:4] == "line" and key[-4:] == "cols":
            index = key[5:-5]
            line_name = "Line" + index.upper()
            line_var = line_name + r"@"
            line_def = pl.UnsafeCommand(r"define@cmdkeys", line_name,
                                        options=line_var,
                                        extra_arguments=form[key])
            doc.preamble.append(line_def)
            line_keys.append([key, line_name])
        else:
            pass

    format_extra_args = "NumLabels,height,width,fsize,fskip,stretch,cols"
    format_def = pl.UnsafeCommand(r"define@cmdkeys", r"format",
                                  options=r"format@",
                                  extra_arguments=format_extra_args)
    doc.preamble.append(format_def)

    format_args = ["format", ("height={},".format(form["label_h_max"]) +
                              "width={},".format(form["label_w_max"]) +
                              "fsize={},".format(form["font_size"]) +
                              "fskip={},".format(form["font_skip"]) +
                              "stretch={},".format(form["baselinestretch"]) +
                              "cols={}".format(form["cols"]))]
    format_cmd = pl.base_classes.Command("setkeys", arguments=format_args)
    doc.preamble.append(format_cmd)

    reps_cmd = pl.UnsafeCommand("newcommand", r"\reps",
                                extra_arguments=r"\format@NumLabels")
    fsize_cmd = pl.UnsafeCommand("newcommand", r"\fsize",
                                 extra_arguments=r"\format@fsize")
    fskip_cmd = pl.UnsafeCommand("newcommand", r"\fskip",
                                 extra_arguments=r"\format@fskip")
    cols_cmd = pl.UnsafeCommand("newcommand", r"\cols",
                                extra_arguments=r"\format@cols")

    doc.preamble.append(reps_cmd)
    doc.preamble.append(fsize_cmd)
    doc.preamble.append(fskip_cmd)
    doc.preamble.append(cols_cmd)

    if int(form["compress_cols"]):
        lab_box_def = r"\parbox[t]{\format@width}{#1}\newline\newline"
    else:
        lab_box_def = r"\parbox[t][\format@height]{\format@width}{#1}\newline"

    lab_box_cmd = pl.UnsafeCommand("newcommand", r"\labelbox", options=1,
                                   extra_arguments=lab_box_def)
    doc.preamble.append(lab_box_cmd)

    stretch_cmd = pl.UnsafeCommand("renewcommand", [r"\baselinestretch",
                                                    r"\format@stretch"])
    doc.preamble.append(stretch_cmd)

    # doc.preamble.append(pl.utils.NoEscape(r"\def\nulldate{00/00/00}"))
    # doc.preamble.append(pl.utils.NoEscape(r"\def\nullmethod{}"))

    label_text = r""
    for key in sorted(form.keys()):
        if key[0:4] == "line" and key[-4:] == "form":
            if label_text:
                label_text += "\n"
            else:
                label_text += r"\raggedright"
            label_text += "\n\t" + form[key]
        else:
            pass

    label = pl.utils.NoEscape(label_text)
    lgen_cmd = pl.UnsafeCommand("newcommand", r"\lgen", extra_arguments=label)
    doc.preamble.append(lgen_cmd)

    doc.preamble.append(pl.utils.NoEscape(r"\makeatother"))

    doc.append(pl.utils.NoEscape(r"\raggedright"))

    with doc.create(MultiCol(arguments=pl.utils.NoEscape(r"\cols"))) as mcols:
        try:
            val_mods = eval(form["val_mods"])
            for func in val_mods:
                data[func] = data[func].apply(lambda val: eval(val_mods[func]))
        except KeyError:
            pass
        for row in data.to_dict(orient='records'):
            for line_pair in line_keys:
                args = [line_pair[1], (",").join(
                        ["{}={{{}}}".format(key, row[key])
                         for key in form[line_pair[0]].split(",")]
                        )]
                setkeys = pl.UnsafeCommand("setkeys", args)
                mcols.append(setkeys)
            num_lab = ["format", "NumLabels={:.0f}".format(row["NumLabels"])]
            mcols.append(pl.UnsafeCommand("setkeys", num_lab))
            mcols.append(Repeat(arguments=pl.utils.NoEscape(r"\reps"),
                         options=None,
                         extra_arguments=LabelBox(LabelGen())))
            mcols.append(LabelBox(""))

    doc.generate_pdf(r"../out/" + name,
                     clean_tex=False,
                     compiler=form["compiler"])


def main():
    data = read_data()
    for file in data.items():
        name = file[0][:file[0].rfind(".")]
        try:
            form = read_format(name + ".format")
        except FileNotFoundError:
            form = read_format()
        make_labels(form, name, file[1])


if __name__ == "__main__":
    main()

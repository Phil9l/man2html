# MAN2HTML
Simple console application for converting from man (nroff format) into html for my university python course.

## Description
Converts nroff data into html format.

## Usage
`./main.py --input FILE [--output FILE]`

### Example
`./main.py --input tmp.txt --output output.html`
Or to convert from man directly use the following one:
```bash
zcat ``man -w g++`` > in.txt; ./main.py -i in.txt -o out.html
```

### Options
* `--input FILE` — input file in nroff format
* `--output FILE` — output file (will have html format)

## Structure
### utils.py
Subsidiary functions.
* `man2html(text_lines)` — converts nroff text into html one by one
* `modify_line(line)` — converts one line from nroff into html
* `apply_part_tags(line)` — modifies line with one kind of tags while possible
* `apply_part_tags_once(line)` — modifies line with the same kind of tags one
* `apply_not_closing_tags(line)` — modifies line with one kind of tags that doesn't have closing ones
* `change_font(line)` — changes current font based on `line` tags
* `update_font(positions)` — updates current font based on nroff rules
### main.py
Small script using utils to convert data from nroff into html format.

# `macro_expander`

This is a python module for doing basic macro expansion in text, which is a simpler form of template rendering. The module
provides a class named `MacroProcessor` that will parse text for macros and call a handler (callback) for each. Users can easily define their
own macros by writing handler functions in a file named `macros.py`.

## Installing

```bash
$ pip install macro-expander
```

## Usage

The module provides a command line script named `expand-macros.py` that takes a text file as its first argument and an output file as it second argument. The
script reads the text file, searches for "macros", and then replaces each macro with its expansion. The syntax/pattern for specifying a macro in the text is predefined
by the module and is similar to LaTeX commands, but the macro expansion is performed by a python function, which can be supplied by the user. This allows a user
to easily add new macros by simply writing a function with the correct signature.

Several macros are already provided. For example, say we have a text files named `input.txt` with the text
```
The `ls` command is used to list the files and directories in a directory. For example, running `ls` in your home directory will produce output similar to this:
$ ls
\shell{ls}
```
If we run
```
$ expand-macros.py input.txt output.txt
``
The `expand-macros.py` script will find the `shell` macro, run the command(s) inside the `{}`, and replace it with the output of the commands, producing something like
```
The `ls` command is used to list the files and directories in a directory. For example, running `ls` in your home directory will produce output similar to this:
```
$ ls
Audio Conan Desktop Documents
Downloads Pictures Videos
```
in a file named `output.txt`.

## Macros

The syntax for macros is inspired by LaTeX commands. Macro names are prefixed with a `\`, followed by an optional set of square brackets `[]`, followed by one or more sets of curly brackets `{}`.
```
\macro_name[optional text]{argument text}{more argument text}
```
If the macro does not take any arguments, it still must include one set of empty curly brackets to identify the end of the macro name.
The syntax may be a little clumsy to those not familiar with LaTeX, but it is flexible.

### Defining new macros

To define a new macro, you just need to provide a callback function in a file named `macros.py` somewhere in python's import path.
The module will attempt to import `macros` and load all callback
functions. The callback function should accept arguments
```
def example_macro(args, opts):
  ...
  return new_text
```
The `macro_expander` will take care of parsing macros in the input text, look for a
callback function to expand each macro it finds. The list of arguments following the macro name will be
passed as the first argument, and the text inside the optional `[]` will be passed as the second argument. Arguments and the optional text are
passed in as strings. The callback function is responsible for processing these for any special meaning (to support key1=value1,key2=value2 style options to be set inside the `[]` for example).
The callback return the text that should be used to replace the macro, and the `macro_expander` module handles the expansion.


### Included macros

#### mathimg

Replaces a LaTeX snippet with an image of the rendered LaTeX. Useful for inserting LaTeX math into markdown files for example. Requires [tex2im](https://github.com/CD3/tex2im), a command line tool for converting
LaTeX snippets to PNG.

Example:

```
Coulomb's Law is:

\mathimg{\vec{F} = \frac{k q_1 q_2}{r^2} \hat{r}}
```
will produce
```
Coulomb's Law is:

![](./mathimg-a12c90dd39e0ee8cb5025183d44ec431cad68d6d-image.png)
```
The file mathimg-a12c90dd39e0ee8cb5025183d44ec431cad68d6d-image.png is created by `tex2im` and contains an image of the equation. The `mathimg` also accepts
an output format option. For example, to specify HTML
```
Coulomb's Law is:

\mathimg[o="html"]{\vec{F} = \frac{k q_1 q_2}{r^2} \hat{r}}
```
which will produce
```
Coulomb's Law is:

<img src="data:image/png;base64,{IMAGE}" >
```
where `{IMAGE}` will be the binary representation of the image. This gives a method for directly embedding the image into an HTML page for example.

#### scriptimg

Similar to mathimg, but instead of LaTeX, an arbitrary script is ran to produce the image that will be inserted. The script just needs to create a file named `out.png` with the image, and it will be inserted
in the same way that mathimg inserts it. For example, to insert a graph using gnuplot
```
This is a graph of sine and cosine:
\scriptimg{#! /usr/bin/gnuplot
set term png
set output 'out.png'

set xlabel "x"
set grid
set xrange[0:2*pi]

plot sin(x), cos(x)
}
```
Note the shebang. The argument text will be written to a temporary file, made executable, and executed. The shebang is necessary to make gnuplot run the script. Obviously you should not run `expand-macros.py` on text from
untrusted sources.

#### shell

Writes the argument text to a temporary file, runs it as a shell script, and replaces the macro with the output of the script. This is useful for writing documentation about a command line utilities.

#### file

Inserts the contents of a file.

```
Consider the following snippet of code:

\file{snippet.cpp}
```

This will insert the text from `snippet.cpp` into the output file.



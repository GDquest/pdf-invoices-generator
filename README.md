# Invoices-cli: create invoices from the command-line

Invoices generates clean and lightweight invoices fast, in batches, right on your computer, from the command line.

There are plenty of complete applications with modern user interfaces to create invoices one-by-one. But I couldn't find an open source tool to:

1. Generate invoices in large batches.
2. Create invoices in a simple way, from a CSV file or the command-line.

That's what invoices-cli is. It is a simple yet efficient Python program that is meant to play nice with your shell.

⚠ Invoices-cli is currently in development. Although it works, it doesn't have a command line interface yet.

Contributors are welcome! See the [open issues](https://github.com/NathanLovato/pdf-invoices-generator/issues)

## How it works ##

The tool takes a template HTML files and css, and fill them up with information from your configuration, company, and invoices file.

![screenshot of a generated invoice](https://i.imgur.com/767Xdjp.png)

## Installing dependencies for development and testing ##

The tool relies on [weasyprint](https://weasyprint.readthedocs.io/en/stable/), a library to render web pages to PDF and PNG. The project uses pipenv to manage dependencies and easily install everything.

If you don't have pipenv, install it with:

```bash
pip install pipenv
```

Then, in the invoices project directory, call:

```
pipenv install
```



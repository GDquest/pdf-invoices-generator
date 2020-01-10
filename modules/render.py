import os
from itertools import starmap


def render(dir_out: str, as_png: bool = False):
    """Renders the html files found in the dir_out either as PDF or PNG image files.
    """
    dir_html = os.path.join(dir_out, "html")
    html_files = (path for path in os.listdir(dir_html) if path.endswith(".html"))
    extension = ".png" if as_png else ".pdf"
    arguments = map(lambda file: (file, dir_out, dir_html, extension), html_files)
    paths = starmap(_get_file_paths, arguments)

    import weasyprint

    for path_html, path_out in paths:
        html = weasyprint.HTML(filename=path_html)
        if as_png:
            html.write_png(path_out)
        else:
            html.write_pdf(path_out)


def _get_file_paths(
    filename: str, dir_out: str, dir_html: str, extension: str
) -> tuple:
    """Returns (path_html, path_out), a tuple containing the html file to render from and
    the place to render it to.
    """
    path_html = os.path.join(dir_html, filename)
    name = os.path.splitext(filename)[0]
    path_out = os.path.join(dir_out, name) + extension
    return path_html, path_out

import datetime
import os
import re
from itertools import starmap
import time


def render(args, dir_out: str, as_png: bool = False):
    """Renders the html files found in the dir_out either as PDF or PNG image files.
    """
    dir_html = os.path.join(dir_out, "html")
    html_file_paths = [path for path in os.listdir(dir_html) if path.endswith(".html")]
    files_to_render = [path for path in html_file_paths if _is_in_date_range(path, args.start_date, args.end_date)]
    extension = ".png" if as_png else ".pdf"
    arguments = map(lambda file: (file, dir_out, dir_html, extension), files_to_render)
    paths = starmap(_get_file_paths, arguments)

    import weasyprint

    weasyprint.CSS(string="@page { size: A4; margin: 1cm }")

    count, total = 1, len(files_to_render)
    time_start = time.time()
    print(f"Rendering {total} files.")
    for path_html, path_out in paths:
        print(f"Rendering file {count} out of {total}", end="\r" if count != total else "\n")
        html = weasyprint.HTML(filename=path_html)
        if as_png:
            html.write_png(path_out)
        else:
            html.write_pdf(path_out)
        count += 1
    print(f"Rendered {total} files in {round(time.time() - time_start, 1)} seconds.")


def _is_in_date_range(
    file_path: str, start_date: datetime.date, end_date: datetime.date
) -> bool:
    name: str = os.path.split(file_path)[-1]
    match: re.Match = re.match(r"^(\d{4}-\d{2}-\d{2})", name)
    file_date = datetime.date.fromisoformat(match[1])
    return True if start_date <= file_date <= end_date else False


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

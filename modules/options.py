"""
Module to access and set the program's options
"""

options = {}


def get(option=""):
    return options[option] if option in options else ""

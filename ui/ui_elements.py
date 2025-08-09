from tkinter import *

def create_entry(parent, **kwargs):
    return Entry(parent, **kwargs)

def create_button(parent, **kwargs):
    return Button(parent, **kwargs)

def create_listbox(parent, **kwargs):
    return Listbox(parent, **kwargs)

def create_scrollbar(parent, **kwargs):
    return Scrollbar(parent, **kwargs)

def create_dropdown(parent, variable, options, font=None, **kwargs):
    dropdown = OptionMenu(parent, variable, *options)
    if font:
        dropdown.config(font=font)
        dropdown["menu"].config(font=font)
    for key, value in kwargs.items():
        dropdown.config({key: value})
    return dropdown
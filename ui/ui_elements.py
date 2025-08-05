from tkinter import *

def create_entry(parent, **kwargs):
    return Entry(parent, **kwargs)

def create_button(parent, **kwargs):
    return Button(parent, **kwargs)

def create_listbox(parent, **kwargs):
    return Listbox(parent, **kwargs)

def create_scrollbar(parent, **kwargs):
    return Scrollbar(parent, **kwargs)

def create_dropdown(parent, variable, values, **kwargs):
    return OptionMenu(parent, variable, *values)
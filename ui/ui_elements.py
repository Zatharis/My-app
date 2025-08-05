from tkinter import *
from tkinter import ttk

def create_entry(parent, font, bg="#e5c3cc", fg="black"):
    return Entry(parent, font=font, bg=bg, fg=fg)

def create_button(parent, text, command, bg="#8a6276", fg="black", font=None, width=None):
    return Button(parent, text=text, command=command, bg=bg, fg=fg, font=font, width=width)

def create_dropdown(parent, variable, values, style="CustomCombobox.TCombobox"):
    return ttk.Combobox(parent, textvariable=variable, values=values, state="readonly", style=style)

def create_listbox(parent, font, bg="#f5dfe8", fg="black"):
    return Listbox(parent, font=font, bg=bg, fg=fg)

def create_scrollbar(parent):
    return Scrollbar(parent)
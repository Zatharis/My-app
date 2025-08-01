









from tkinter import *
from tkinter import ttk
from datetime import date 
import os
from tkinter import font as tkfont


#Get today's date
today = date.today()
date_string = today.strftime("%m-%d-%y")


task_file = "tasks.txt"


#function to run when button is clicked
def get_task():
   user_input = entry_widget.get()
   due_date = due_date_entry.get().strip()
   if user_input.strip() != "":
    if due_date:
       task_text = f"[{due_date}] - {user_input} (Due: {due_date})"
    else:
       task_text = f"[{date_string}] - {user_input}"
    task_listbox.insert(END, task_text)
    save_task(task_text)
    entry_widget.delete(0, END)
    due_date_entry.delete(0, END)


def save_task(task_text):
   with open(task_file, "a") as f:
       f.write(task_text + "\n")


def load_tasks():
   if os.path.exists(task_file):
       with open(task_file, "r") as f:
           for line in f:
               task_listbox.insert(END, line.strip())


def delete_task():
   seleted_index = task_listbox.curselection()
   if seleted_index:
       task_text = task_listbox.get(seleted_index)
       task_listbox.delete(seleted_index)
       delete_task_from_file(task_text)


def delete_task_from_file(task_text):
   if os.path.exists(task_file):
       with open(task_file, "r") as f:
           lines = f.readlines()
       with open(task_file, "w") as f:
           for line in lines:
               if line.strip() != task_text:
                   f.write(line)




#Create window
root = Tk()
root.title("My Task Manager")
root.configure(bg="#ad7b93")
custom_font = tkfont.Font(family="courier 10 pitch", size=16)



#style
style = ttk.Style()
style.configure("Mainframe.TFrame", background="#aaaaaa")






#Main layout frame
mainframe = ttk.Frame(root, padding="3 3 12 12", style="Mainframe.TFrame")
mainframe.grid(column=0, row=0, sticky=(N, W, S, E))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


mainframe.columnconfigure(0, weight=1)
mainframe.columnconfigure(1, weight=0)
mainframe.columnconfigure(2, weight=1)




#date label
date_label = ttk.Label(mainframe, text=date_string, font=custom_font)
date_label.grid(column=1, row=0, pady=5)

#entry Widget for due date
due_date_lable = ttk.Label(mainframe, text="Due Date (MM-DD-YY):", font=custom_font)
due_date_lable.grid(column=0, row=1, pady=5, sticky=E)

due_date_entry = Entry(mainframe, width=10, bg="#dddddd", bd=2, relief="solid", highlightbackground="#aaa", highlightthickness=1, font=custom_font)
due_date_entry.grid(column=0, row=2, pady=5, sticky=W)

#Entry widget for task input
entry_widget = Entry(mainframe, width=50, bg="#dddddd", bd=2, relief="solid", highlightbackground="#aaa", highlightthickness=1, font=custom_font)
entry_widget.grid(column=1, row=1, pady=5)
entry_widget.bind("<Return>", lambda event: get_task())


#Submit button
submit_button = Button(root, text="Add task", command=get_task, bg="#d5a6bd", relief="raised", bd=2, font=custom_font)
submit_button.grid(column=1, row=2, pady=5)


#listbox to show tasks
task_listbox = Listbox(mainframe, width=60, height=10, bg="#d5a6bd", bd=2, relief="solid", highlightbackground="#aaa", highlightthickness=1, font=custom_font)
task_listbox.grid(column=1, row=3, pady=10)

#scrollbar for the listbox
Scrollbar = Scrollbar(mainframe, orient=VERTICAL, command=task_listbox.yview)
Scrollbar.grid(column=2, row=3, sticky='ns', pady=10)
task_listbox.config(yscrollcommand=Scrollbar.set)



#delet task button
delete_button = Button(mainframe, text="Mark as Done (Delete)", command=delete_task, bg="#d5a6bd", relief="raised", bd=2, font=custom_font)
delete_button.grid(column=1, row=4, pady=5)


load_tasks()




root.mainloop()






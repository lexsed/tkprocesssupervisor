


# test treewview ttk


import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk()
root.title("Treeview")

tree = ttk.Treeview(root, columns=("one", "two"), show="headings")
tree.pack()

tree.insert("", "end", 0, values=('1','First Item'))
tree.insert("", "end", 1, values=('2','Second Item'))
tree.insert("", "end", 2, values=('3','Last Item'))


tree.focus(1)

tree.tag_configure("warning", background="yellow")
tree.tag_configure("running", background="lightgreen")


tree.item(1)['values']=('1','2')
tree.item(1, tags="warning")
tree.column("# 1",anchor=tk.CENTER, stretch=tk.NO, width=20)




root.mainloop()


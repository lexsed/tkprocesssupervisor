from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg , NavigationToolbar2Tk
import tkinter as tk
import matplotlib.pyplot as plt
 
root = tk.Tk()
fig, ax = plt.subplots()

ax.plot([1,2,3,4,5,6,7,8], [1,2,3,4,5,6,7,8])
 
canvas = FigureCanvasTkAgg(fig, root)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

toolbar = NavigationToolbar2Tk(canvas, root)

toolbar.pack(fill=tk.BOTH, expand=True)




 
root.mainloop()
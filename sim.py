# Use Tkinter for python 2, tkinter for python 3
import itertools
import tkinter as tk


class GWSim(tk.Frame):
    def __init__(self, *args, **kwargs):
        # Create main window
        root = tk.Tk()

        # Add base frame to window
        tk.Frame.__init__(self, root, *args, **kwargs)

        # Store instance variables
        self._root = root
        self._parent = self._root
        self._canvas = tk.Canvas(self._root, width=250, height=250)
        self._canvas.pack(side=tk.TOP)

        # Create grid
        self._grid = Grid(parent=self, canvas=self._canvas, dim=(5, 5), cell_size=(50, 50))
        # self._grid.pack(side="left")
        self._grid.grid(row=0, column=0)

        # Pack widgets
        # self.pack(side="top", fill="both", expand=True)

    def run(self):
        self._root.mainloop()


class Grid(tk.Frame):
    def __init__(self, parent, canvas, dim, cell_size, *args, **kwargs):
        # Add base frame to window
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # Instance variables
        self._parent = parent
        self._canvas = canvas
        self._dim = dim
        self._cell_size = cell_size

        # self._cell = Cell(parent=self, canvas=self._canvas)
        # self._cell.pack()
        for row, col in itertools.product(range(5), range(5)):
            x1 = col * cell_size[0] + 3
            y1 = row * cell_size[1] + 3
            x2 = x1 + cell_size[0]
            y2 = y1 + cell_size[1]

            # Create the frame and pack it into the main window
            frame = Cell(parent=self, canvas=self._canvas, x1=x1, y1=y1, x2=x2, y2=y2)
            frame.grid(row=row, column=col)
            # frame.pack_propagate(False)
            # frame.place(x=x1, y=y1)

    def _visualize_grid(self):
        width, height = self._cell_size
        for i in range(self._dim[0]):
            for j in range(self._dim[1]):
                self._canvas.create_rectangle(
                    i * width, j * width, (i + 1) * width, (j + 1) * width, fill="white", width=1
                )


class Cell(tk.Frame):
    def __init__(self, parent, canvas, x1, y1, x2, y2, *args, **kwargs):
        # Add base frame to window
        tk.Frame.__init__(self, parent, *args, **kwargs)

        # Instance variables
        self._canvas = canvas
        # self.render()

        self._canvas.create_rectangle(
            x1, y1, x2+3, y2+3, width=2, dash=(5, 1)
        )

    # def render(self):


class Sprite(tk.Frame):
    def __init__(self, parent, canvas, x1, y1, x2, y2, *args, **kwargs):
        pass


if __name__ == "__main__":
    # root = tk.Tk()
    sim = GWSim(width=800, height=400)
    sim.run()

    # root.mainloop()

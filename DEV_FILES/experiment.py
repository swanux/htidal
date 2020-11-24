#!/usr/bin/env python3
import gi, math

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Grid(Gtk.Window):
    widget_list = []
    WIDGET_SIZE = 140
    COLS = 1
    NUM = 50
    WIDTH = 0

    def calcule_columns(self, scroll, grid):
        width = scroll.get_allocated_width()
        if self.WIDTH != width:
            self.WIDTH = width
            cols = width / (self.WIDGET_SIZE + grid.get_column_spacing())
            if (cols > len(self.widget_list)): cols = len(self.widget_list)
            return cols
        else:
            return self.COLS
		
    def on_resize(self, arg1, arg2, scroll, grid):
        new_cols = self.calcule_columns(scroll, grid)
        print("New: ", new_cols)
        if  new_cols == self.COLS or new_cols == 0 or new_cols > len(self.widget_list): return
        self.COLS = new_cols
        self.remove_widgets(grid)
        self.load_widgets(grid)
		
    def remove_widgets(self, grid):
        print("remove")
        if self.widget_list == 0: return
        for wid in grid.get_children():
            # print(wid)
            grid.remove(wid)

    def create_grid(self):
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(False)
        grid.set_border_width(0)
        return grid
		
    def load_widgets(self, grid):
        i,j = 0,0
        COLS = self.COLS
        print("Load")
        # print("Actual: ", COLS)
        if len(self.widget_list) == 0:
            print("FUCK")
            return
        for wid in self.widget_list:
            grid.attach(wid, i, j, 1, 1)
            i+=1
            # print(i, COLS)
            if i == math.floor(COLS):
                i=0
                j+=1
                print(i, COLS, j)

    def __init__(self):
        def callback(widget):
            this = widget.get_label()
            dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK)
            dialog.set_title("Window title %s" % this.split(" ")[1])
            dialog.set_markup("You chose <b>%s</b>, try it again!" % this)
            dialog.run()
            dialog.destroy()

        Gtk.Window.__init__(self, title="Grid")
		
        self.resize(self.WIDGET_SIZE*6, self.WIDGET_SIZE*2)
        self.set_position(Gtk.WindowPosition.CENTER)

        grid_main = self.create_grid()
        scroll = Gtk.ScrolledWindow()
        scroll.set_border_width(0)
        scroll.add(grid_main)
        scroll.connect("size-allocate", self.on_resize, scroll, grid_main)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.add(scroll)

        z = 1
        while z is not self.NUM+1:
            button = Gtk.Button()
            button.set_label("Button %s" % z)
            button.connect("clicked", callback)
            self.widget_list.append(button)
            z+=1

        self.load_widgets(grid_main)


win = Grid()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

# Result: Cool stuff and actually works, but not suitable for Python at all (due to performance issues) Better try with something else (Rust/Go) later...
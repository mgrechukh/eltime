import gi
from gi.repository import GLib, Gtk, Gdk, GObject

class InfoDialog(Gtk.Dialog):
    def __init__(self, parent, text):
        super().__init__(title="Recorded activities", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        self.set_default_size(350, 200)
        box = self.get_content_area()

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        box.add(scrolledwindow)

        textview = Gtk.TextView()
        textbuffer = textview.get_buffer()
        textbuffer.set_text(text)
        scrolledwindow.add(textview)

        self.show_all()

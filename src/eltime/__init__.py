#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk, Gdk, GObject
import os
import math

from .texts import css, markup_true, markup_false

from .info_dialog import InfoDialog

from .sqlrecorder import SqliteRecorder

from datetime import date, datetime, timedelta

# Define our own newWindow class.
class newWindow(Gtk.Window):
    def __init__(self):
        self.progress = False
        self.started_at = None
        self.started_with = None

        self.recorder = SqliteRecorder(os.path.expanduser("~/.config/eltime.db"))
        # Call the constructor of the super class.
        # Set the value of the property title to Geeks for Geeks.
        Gtk.Window.__init__(self, title ="Eltime")

        self.box = Gtk.Box(spacing=4)
        self.add(self.box)

        self.liststore = Gtk.ListStore(str)

        for item in self.recorder.get_entries():
            self.liststore.append([item])

        self.entrycompletion = Gtk.EntryCompletion()
        self.entrycompletion.set_model(self.liststore)
        self.entrycompletion.set_text_column(0)
        self.entrycompletion.set_minimum_key_length(0)
        self.entrycompletion.set_inline_selection(True)
        self.entrycompletion.set_inline_completion(True)

        # Create a button widget, connect to its clicked signal
        # and add it as child to the top-level window.
        self.button = Gtk.ToggleButton()
        self.button.connect("toggled", self.update_ui)
        self.label = Gtk.Label()
        self.label.set_markup(markup_true)
        self.button.add(self.label)
        self.set_focus(self.button)
        self.box.pack_start(self.button, True, True, 0)

        self.entry = Gtk.Entry(placeholder_text = '(name your activity)')
        self.entry.connect("activate", self.enter)
        self.entry.connect("focus-in-event", lambda widget, list: self.entry.emit('changed'))
        self.entry.set_completion(self.entrycompletion)
        self.box.pack_start(self.entry, True, True, 0)

        self.timer = Gtk.Entry()
        self.timer.set_no_show_all(True)
        self.timer.set_editable(False)
        self.timer.set_can_focus(False)
        self.timer.set_alignment(xalign=1)
        self.timer.get_style_context().add_class('grayed')

        self.box.pack_start(self.timer, True, True, 0)

        self.set_resizable(False)

        accel = Gtk.AccelGroup()
        accel.connect(Gdk.keyval_from_name('H'), Gdk.ModifierType.CONTROL_MASK, 0, self.ctrl_h)
        accel.connect(Gdk.keyval_from_name('Q'), Gdk.ModifierType.CONTROL_MASK, 0, Gtk.main_quit)
        self.add_accel_group(accel)

    def enter(self, widget = None):
        print("change button state")
        self.button.set_active(not self.button.get_active())

    def ctrl_h(self, *args):
        print("ctrl-h pressed", args)

        yesterday = datetime.combine(date.today()- timedelta(days=1), datetime.min.time())
        data = self.recorder.get_aggregated_stats(yesterday.timestamp())
        print(data)

        dailysum = {}
        report = []
        for l in data:
            day, hour, duration, entry = l
            if not day in dailysum:
                dailysum[day] = 0
            rounded_minutes = math.ceil(duration / 600.0) * 10        
            dailysum[day] += rounded_minutes
            report.append("%s %.0f minutes (%s)" % (hour, rounded_minutes, entry.strip() or 'unnamed task'))

        if report:
            report.append('---')
        for x in dailysum:
            report.append("TOTAL day %s: %.0f minutes" % (x, dailysum[x]))
        print(report)
        dialog = InfoDialog(self, "\n".join(report))
        dialog.run()
        dialog.destroy()

    # When we click on the button this method
    # will be called
    def update_ui(self, widget = None):
        if self.button.get_active():
            print("starting activity", self.entry.get_text())
            self.started_at = datetime.now()
            self.started_with = self.entry.get_text()
            self.display_clock()

            self.label.set_markup(markup_false)
            self.entry.set_visible(False)
            self.timer.set_visible(True)
            self.set_focus(self.button)

        else:
            print("end activity", self.entry.get_text())
            self.liststore.clear()
            for item in self.recorder.get_entries():
                self.liststore.append([item])

            self.started_at = None
            self.label.set_markup(markup_true)
            self.entry.set_visible(True)
            self.timer.set_visible(False)
            self.set_focus(self.button)

    def start_timer(self):
        #  this takes 2 args: (how often to update in millisec, the method to run)
        GLib.timeout_add(1000, self.display_clock)

    def display_clock(self):
        if not self.started_at:
            print("nothing to do")
            return

        self.recorder.update_session(self.started_at.timestamp(), self.started_with)

        total_seconds = (datetime.now() - self.started_at).total_seconds()
        hours = total_seconds // 3600
        minutes = total_seconds % 3600 // 60
        seconds = total_seconds % 60
        print(datetime.now())
        print(datetime.now() - self.started_at)
        print(hours, minutes, seconds)
        message = "%02d:%02d:%02d" % (hours, minutes, seconds)
        if self.started_with:
            message = "(%s) " % self.started_with + message
        print("updating", message)
        self.timer.set_text(message)
        GLib.timeout_add(1000, self.display_clock)

def main_gui():
    cssProvider = Gtk.CssProvider()
    cssProvider.load_from_data(css.encode('utf-8'))
    screen = Gdk.Screen.get_default()
    styleContext = Gtk.StyleContext()
    styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    win = newWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.set_decorated(False)
    win.set_keep_above(True)
    win.set_opacity(0.7)
    Gtk.main()

def main():
    # todo: cli reporting and control
    return main_gui() 

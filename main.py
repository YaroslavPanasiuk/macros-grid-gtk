#!/usr/bin/env python3
import sys
import os
import subprocess
import json
import argparse
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib

CUSTOM_CONFIG_PATH = None

def execute_command(button, command):
    subprocess.run(command, shell=True)

def apply_dynamic_css(widget, css_string):
    provider = Gtk.CssProvider()
    provider.load_from_data(css_string.encode('utf-8'))
    widget.get_style_context().add_provider(
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_USER
    )

def create_button(item):
    btn = Gtk.Button()
    cmd = item.get("command", "echo 'No command'")
    btn.connect("clicked", execute_command, cmd)

    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    box.set_halign(Gtk.Align.CENTER)
    box.set_valign(Gtk.Align.CENTER)

    icon_name = item.get("icon")
    if icon_name:
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon_size = item.get("icon_size", -1)
        if icon_size > 0:
            icon.set_pixel_size(icon_size)
        box.append(icon)

    label_text = item.get("label", "Unknown")
    label = Gtk.Label(label=label_text)
    box.append(label)

    btn.set_child(box)
    btn.set_hexpand(True)
    btn.set_vexpand(True)

    bg_color = item.get("bg_color")
    if bg_color:
        css = f"button {{ background-color: {bg_color}; background-image: none; }}"
        apply_dynamic_css(btn, css)

    return btn

def build_layout(node, orientation):
    if isinstance(node, dict):
        return create_button(node)
    
    if isinstance(node, list):
        # Create a box that forces equal size for all its children
        box = Gtk.Box(orientation=orientation, spacing=10)
        box.set_homogeneous(True)
        box.set_hexpand(True)
        box.set_vexpand(True)
        
        # Alternate orientation for the next nesting level
        next_orient = Gtk.Orientation.VERTICAL if orientation == Gtk.Orientation.HORIZONTAL else Gtk.Orientation.HORIZONTAL
        
        for item in node:
            child = build_layout(item, next_orient)
            if child:
                box.append(child)
        return box
        
    return None

def on_activate(app):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Load Global CSS (style.css)
    global_provider = Gtk.CssProvider()
    css_path = os.path.join(base_dir, 'style.css')
    if os.path.exists(css_path):
        global_provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            global_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    builder = Gtk.Builder()
    ui_path = os.path.join(base_dir, 'layout.ui')
    builder.add_from_file(ui_path)

    win = builder.get_object("main_window")
    win.set_application(app)

    if CUSTOM_CONFIG_PATH:
        commands_path = CUSTOM_CONFIG_PATH
    else:
        config_dir = os.path.join(GLib.get_user_config_dir(), 'macro-grid')
        main_config_path = os.path.join(config_dir, 'config.json')
        commands_path = os.path.join(base_dir, 'commands.json')

        if os.path.exists(main_config_path):
            try:
                with open(main_config_path, 'r') as f:
                    main_config = json.load(f)
                    commands_path = main_config.get("commands_file", commands_path)
            except (json.JSONDecodeError, IOError):
                pass

    commands_path = os.path.expanduser(commands_path)

    try:
        with open(commands_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {"settings": {}, "commands": []}

    try:
        with open(commands_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {"settings": {}, "commands": []}

    commands = config.get("commands", [])
    main_layout = build_layout(commands, Gtk.Orientation.VERTICAL)

    win_bg = config.get("settings", {}).get("window_bg_color")
    if win_bg:
        apply_dynamic_css(win, f"window.background {{ background-color: {win_bg}; }}")
    
    if main_layout:
        # Re-apply external margins to the root box
        main_layout.set_margin_top(20)
        main_layout.set_margin_bottom(20)
        main_layout.set_margin_start(20)
        main_layout.set_margin_end(20)
        win.set_child(main_layout)

    win.present()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')
    args, unknown = parser.parse_known_args()

    if args.config:
        CUSTOM_CONFIG_PATH = os.path.abspath(args.config)

    app = Gtk.Application(application_id='com.example.GtkApp')
    app.connect('activate', on_activate)
    sys.exit(app.run([sys.argv[0]] + unknown))
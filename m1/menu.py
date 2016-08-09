#!/usr/bin/env python3

import curses
import json
import sys
import re
import os
import logging
from pathlib import Path
import subprocess
from os.path import expanduser
import menuitem
from menuitem import MenuItem

class Menu:
    def __init__(self, parent = None, screen = None):
        self.parent = parent
        self.screen = screen

        self.name = ""
        self.action = ""
        self.items = []
        self.hotkeys = dict()
        self.active_row = 2

        if screen != None:
            curses.init_pair(1, curses.COLOR_WHITE, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)

    def add_item(self, jsonConfig):
        item = MenuItem()

        if 'name' in jsonConfig:
            item.name = menuitem.cut_name(jsonConfig['name'])
            
        if 'action' in jsonConfig:
            item.action = jsonConfig['action']
            self.items.append(item)

        if 'generator' in jsonConfig:
            item.generator = jsonConfig['generator']
            logging.debug("using generator:" + item.generator)
            args = []
            argRegexp = '(-?\S+)|(".+")'
            m = re.findall(argRegexp, item.generator)
            for match in m:
                match0 = match[0]
                if match0 != None and match0 != '':
                    command =  match0.replace('~', str(Path.home()))
                    print(command)
                    args.append(match0.replace('~', str(Path.home())))
                else:
                    args.append(match[1])
            process = subprocess.run(args, stdout=subprocess.PIPE)
            config = json.loads(process.stdout.decode("UTF-8"))
            logging.debug("generated:" + str(config))
            for generated_item in config['menu']:
                self.add_item(generated_item)

        if 'key' in jsonConfig:
            item.hotkey = jsonConfig['key']

        if 'menu' in jsonConfig: 
            item.menu = Menu(parent = self, screen = self.screen)
            for sub_item in jsonConfig['menu']:
                item.menu.add_item(sub_item)
            self.items.append(item)
            item.menu.create_hotkeys()

    def draw(self):
        if self.screen != None:
            self.screen.border()
            self.screen.addstr(0, 2,  "  M1 Cli Menu  ")
        row = 2
        # todo position instead of string concat
        for menuItem in self.items:
            title = menuItem.name
            if menuItem.menu != None or menuItem.generator != None:
                title ="[ "  + title + " ]"
            else:
                title = "  " + title
            title = menuitem.formalize_name(title)
            if menuItem.hotkey != None:
                title = menuItem.hotkey + "   " + title
            else:
                title = "    " + title
            if (self.active_row == row):
                # todo separate making title
                if self.screen != None:
                    self.screen.addstr(row, 2, "--->> " + title + " <<---", curses.color_pair(1))
            else:
                if self.screen != None:
                    self.screen.addstr(row, 2, "      " + title + "      ")
            row = row + 1 
        self.screen.refresh()
        return self
    
    def next(self):
        self.active_row = self.active_row + 1
        if len(self.items) == self.active_row - 2:
            self.active_row = 2;
        return self

    def prev(self):
        self.active_row = self.active_row - 1
        if self.active_row < 2:
            self.active_row = len(self.items) + 2 - 1
        return self

    def back(self):
        if self.parent != None:
            self.screen.clear()
            return self.parent
        return self

    def go_in(self):
        selected_item = self.items[self.active_row - 2]
        submenu = selected_item.menu
        if submenu != None:
            self.screen.clear()
            return submenu
        return self

    def execute(self):
        selected_item = self.items[self.active_row - 2]
        action = selected_item.action
        if action != None:
            args = action.split(" ")
            subprocess.run(args)
            sys.exit()

        return self.go_in()

    def handle_hotkey(self, key):
        if key in self.hotkeys.keys():
            selected_item = self.hotkeys[key]
            action = selected_item.action
            if action != None:
                args = action.split(" ")
                subprocess.run(args)
                sys.exit()

            submenu = selected_item.menu
            if submenu != None:
                self.screen.clear()
                return submenu

        return self

    def create_hotkeys(self):
        i = ord('a');
        for item in self.items:
            if item.hotkey != None:
                self.hotkeys[item.hotkey] = item
            else:
                if item.name != None:
                    item.hotkey = item.name[0]
                    self.hotkeys[item.hotkey] = item

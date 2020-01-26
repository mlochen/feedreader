#!/usr/bin/env python3

# Copyright (C) 2020 Marco Lochen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from db_if import db_if
import cgi
import math
import time

def get_feed_list(active_feed_id):
    s = '<div id="feed_list"><form method="post">'\
        '<table align="center" id="feed_table">'\
        '<tr><th colspan="2">feeds</th></tr>'
    db.reset_updated_items(active_feed_id)
    for feed in db.get_feeds(active_feed_id):
        tr_class = ' class="active_row"' if (feed['feed_id'] == active_feed_id) else ''
        feed_id = feed['feed_id']
        classes = ["feed_title"]
        if (feed['disabled'] != 0):
            classes.append("disabled")
        if (feed['updated_items'] != 0):
            classes.append("new_items")
        title = feed['title']
        updated_items = ""
        if (feed['updated_items'] != 0):
            updated_items = " (" + str(feed['updated_items']) + ")"

        s = s + f'<tr{tr_class}><td>'\
                f'<input name="del" value="{feed_id}" type="checkbox"></td>'\
                f'<td class="{" ".join(classes)}">'\
                f'<a href="/cgi-bin/feeds.py?id={feed_id}">{title}{updated_items}</a>'\
                f'</td></tr>\n'
    s = s + '</table>'\
            '<input type="submit" class="button" value="delete"></form>'\
            '<form method="post"><input name="add" class="button" type="text">'\
            '<input type="submit" class="button" value="add"></form>'\
            '</div>'
    return s

def get_item_list(feed_id):
    s = '<div id="item_list">'
    for item in db.get_feed_items(feed_id):
        classes = "item unseen" if (item['seen'] == 0) else "item"
        link = item['link']
        author = item['author'] + " - " if (item['author'] != "") else ""
        title = item['title']
        timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(item['published']))
        summary = item['summary']

        s = s + f'<div class="{classes}">'\
                f'<a class="title" href="{link}">{author}{title}</a><br>'\
                f'<div class="date">{timestring}</div><br>'\
                f'<div class="summary">{summary}</div>'
        s = s + get_enclosure_list(item['item_id'])
        s = s + '</div><hr>\n'
    db.set_seen(feed_id)
    s = s + '</div>'
    return s

def get_enclosure_list(item_id):
    s = ''
    enclosures = db.get_enclosures(item_id)
    if (len(enclosures) != 0):
        s = s + '<ul>'
        for enclosure in enclosures:
            href = enclosure['href']
            length = enclosure['length']
            type = enclosure['type']

            s = s + f'<li class="enclosure"><a href="{href}">{href.split("/")[-1]}</a>'\
                    f' ({get_size_string(length)} {type})</li>'
        s = s + '</ul>'
    return s

def get_size_string(bytes):
    log = math.floor(math.log(bytes, 1024))
    value = bytes / math.pow(1024, log)
    unit = ["bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"][log]
    return "%.2f%s" % (value, unit)

db = db_if()
attr = cgi.FieldStorage()

print('''Content-type: text/html

<!DOCTYPE HTML><html lang="en"><head><title>My Feeds</title>
<link rel="stylesheet" type="text/css" href="/feeds/style.css">
<link rel="icon" type="image/png" href="/feeds/icon.png">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>''')

if ('add' in attr):
    db.add_feed(attr.getfirst("add"))

if ('del' in attr):
    for feed_id in attr.getlist("del"):
        db.delete_feed(feed_id)

feed_id = -1
if ('id' in attr):
    feed_id = int(attr['id'].value)

print(get_feed_list(feed_id))

if ('id' in attr):
    print(get_item_list(feed_id))

print('</body></html>')

db.commit()


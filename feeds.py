#!/usr/bin/python3

from db_if import db_if
import cgi
import datetime
import math

def get_feed_list(active_feed_id):
    s = ''
    for feed in db.get_feeds(active_feed_id):
        tr_class = ' class="active_row"' if (feed['feed_id'] == active_feed_id) else ''
        classes = []
        if (feed['disabled'] != 0):
            classes.append("disabled")
        if (feed['updated_items'] != 0):
            classes.append("new_items")

        s = s + f'<tr' + tr_class + '><td>'\
            f'<input name="del" value="{feed["feed_id"]}" type="checkbox"></td>'\
            f'<td class="{" ".join(classes)}">'\
            f'<a href="/cgi-bin/feeds.py?id={feed["feed_id"]}">{feed["title"]} ({feed["updated_items"]})</a>'\
            f'</td></tr>\n'
    return s

def get_item_list(feed_id):
    s = ''
    for item in db.get_feed_items(feed_id):
        timestring = datetime.datetime.fromtimestamp(item["published"]).strftime("%A, %d. %B %Y %I:%M%p")

        if (item["seen"] == 0):
            classes = "item unseen"
        else:
            classes = "item"
        s = s + f'<div class="{classes}">'\
            f'<a class="title" href="{item["link"]}">'
        if (item["author"] != ""):
            s = s + f'{item["author"]} - '
        s = s + f'{item["title"]}</a><br>'\
            f'<div class="date">{timestring}</div><br>'\
            f'<div class="summary">{item["summary"]}</div>'

        s = s + get_enclosure_list(item["item_id"])

        s = s + f'</div>'\
            f'<hr>\n\n\n'
            # alles auf seen setzen
    return s

def get_enclosure_list(item_id):
    s = ''
    enclosures = db.get_enclosures(item_id)
    if (len(enclosures) != 0):
        s = s + '<ul>'
        for enclosure in enclosures:
            s = s + f'<li class="enclosure">'\
                    f'<a href="{enclosure["href"]}">{enclosure["href"].split("/")[-1]}</a>'\
                    f' ({get_size_string(enclosure["length"])} {enclosure["type"]})'\
                    f'</li>'
        s = s + '</ul>'
    return s

def get_size_string(bytes):
    log = math.floor(math.log(bytes, 1024))
    value = bytes / math.pow(1024, log)
    unit = ["bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"][log]
    return "%.2f%s" % (value, unit)

db_path = "/srv/http/feeds/feeds.db"
db = db_if(db_path)
attr = cgi.FieldStorage()

print("Content-type: text/html")
print("")
print('<!DOCTYPE HTML><html lang="en"><head><title>My Feeds</title>')
print('<link rel="stylesheet" type="text/css" href="/feeds/style.css">')
print('<link rel="icon" type="image/png" href="/feeds/icon.png">')
print('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"></head><body>')
print('<div id="feed_list">')

if ('add' in attr):
    db.add_feed(attr.getfirst("add"))

if ('del' in attr):
    for feed_id in attr.getlist("del"):
        db.delete_feed(feed_id)

feed_id = -1
if ('id' in attr):
    feed_id = int(attr['id'].value)

print('<form method="post">')
print('<table align="center" id="feed_table">')
print('<tr><th colspan="2">feeds</th></tr>')

print(get_feed_list(feed_id))

print('</table>')
print('<input type="submit" value="delete"></form>')
print('<form method="post"><input name="add" type="text"><input type="submit" value="add"></form>')
print('</div>')
print('<div id="item_list">')

if ('id' in attr):
    print(get_item_list(feed_id))

print('</div>')
print('</body></html>')


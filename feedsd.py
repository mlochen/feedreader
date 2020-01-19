#!/usr/share/python3

import calendar
import feedparser
import hashlib
import random
import sqlite3
import time

db_path = "./feeds.db"
min_refresh_time = 30 * 60
max_refresh_time = 90 * 60

class db_if:
    """interface to the database"""

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def get_feeds_due(self):
        self.cursor.execute("SELECT * FROM feeds WHERE next_retrieval < ?", (int(time.time()),))
        feeds = self.cursor.fetchall()
        return feeds
                
    def update_feed_data(self, feed_id, key, value):
        self.cursor.execute("UPDATE feeds SET " + key + " = ? WHERE feed_id = ?", (value, feed_id))

    def add_feed(self, href):
        values = (None, href, "", 0, 0, 0, False, 0)
        self.cursor.execute("INSERT INTO feeds VALUES (?, ?, ?, ?, ?, ?, ?, ?)", values)

    def delete_feed(self, feed_id):
        self.cursor.execute("DELETE FROM enclosures WHERE item_id IN\
                             SELECT item_id FROM items WHERE feed_id = ?", (feed_id,))
        self.cursor.execute("DELETE FROM items WHERE feed_id = ?", (feed_id,))
        self.cursor.execute("DELETE FROM feeds WHERE feed_id = ?", (feed_id,))

    def check_item_exists(self, item_id):
        self.cursor.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
        rows = self.cursor.fetchall()
        return len(rows) != 0

    def add_item(self, feed_id, item_id, item, enclosures):
        values = (item_id, feed_id) + item
        self.cursor.execute("INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
        for enclosure in enclosures:
            values = (None, item_id) + enclosure
            self.cursor.execute("INSERT INTO enclosures VALUES (?, ?, ?, ?, ?)", values)

    def commit(self):
        self.conn.commit()


def refresh_feeds(db_if):
    print("refreshing feeds")
    feed_rows = db_if.get_feeds_due()
    for feed_row in feed_rows:
        print("getting feed")
        feed = feedparser.parse(feed_row['href'])
        if ('status' in feed and feed['status'] == 301):
            db_if.update_feed_data(feed_row['feed_id'], "href", feed['href'])
            return
        if ('status' in feed and feed['status'] == 410):
            db_if.update_feed_data(feed_row['feed_id'], "disabled", 1)
            return
        if ('title' in feed.feed and feed.feed['title'] != feed_row['title']):
            db_if.update_feed_data(feed_row['feed_id'], "title", feed.feed['title'])

        updated_items = parse_items(db_if, feed_row['feed_id'], feed['entries'])

        print("updated items", updated_items)
        time_now = int(time.time())
        next_retrieval = time_now + random.randrange(min_refresh_time, max_refresh_time)

        db_if.update_feed_data(feed_row['feed_id'], "last_retrieval", time_now)
        db_if.update_feed_data(feed_row['feed_id'], "next_retrieval", next_retrieval)
        
        if updated_items != 0:
            db_if.update_feed_data(feed_row['feed_id'], "last_activity", time_now)
            db_if.update_feed_data(feed_row['feed_id'], "updated_items", updated_items)
    db_if.commit()

def parse_items(db_if, feed_id, items):
    updated_items = 0
    for item in items:
        feed_item_id = u""
        author = u""
        title = u""
        link = u""
        published = 0
        summary = u""
        enclosures = list()

        if ('id' in item):
            feed_item_id = item['id']
        if ('author' in item):
            author = item['author']
        if ('title' in item):
            title = item['title']
        if ('link' in item):
            link = item['link']
        if ('published_parsed' in item):
            published = calendar.timegm(item['published_parsed'])
        if ('summary' in item):
            summary = item['summary']
        if ('enclosures' in item):
            enclosures = get_enclosures(item['enclosures'])

        item_string = str.encode(feed_item_id + author + title + link + str(published) + summary)
        item_hash = hashlib.sha256(item_string).hexdigest()
        item_tuple = (int(time.time()), False, author, title, feed_item_id, link, published, summary)
        if not db_if.check_item_exists(item_hash):
            db_if.add_item(feed_id, item_hash, item_tuple, enclosures)
            updated_items = updated_items + 1
    return updated_items

def get_enclosures(enclosures):
    enclosure_list = list()
    for enclosure in enclosures:
        href = u""
        length = 0
        type = u""

        if ('href' in enclosure):
            href = enclosure['href']
        if ('length' in enclosure):
            length = enclosure['length']
        if ('type' in enclosure):
            type = enclosure['type']

        enclosure_list.append((href, length, type))
    return enclosure_list

db = db_if(db_path)
while (True):
    refresh_feeds(db)
    time.sleep(60)


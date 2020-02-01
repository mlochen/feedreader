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

import sqlite3
import time

DB_PATH = "/var/www/feedreader/feeds.db"

class FeedDBInterface:
    """interface to the feed database"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS feeds ("
                            "feed_id INTEGER PRIMARY KEY,"
                            "href VARCHAR,"
                            "title VARCHAR,"
                            "last_retrieval TIMESTAMP,"
                            "next_retrieval TIMESTAMP,"
                            "last_activity TIMESTAMP,"
                            "disabled BOOLEAN,"
                            "updated_items INTEGER"
                            ")")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS items ("
                            "item_id VARCHAR PRIMARY KEY,"
                            "feed_id INTEGER,"
                            "retrieved TIMESTAMP,"
                            "seen BOOLEAN,"
                            "author VARCHAR,"
                            "title VARCHAR,"
                            "feed_item_id VARCHAR,"
                            "link VARCHAR,"
                            "published TIMESTAMP,"
                            "summary VARCHAR,"
                            "FOREIGN KEY(feed_id) REFERENCES feeds(feed_id)"
                            ")")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS enclosures ("
                            "enclosure_id INTEGER PRIMARY KEY,"
                            "item_id VARCHAR,"
                            "href VARCHAR,"
                            "length INTEGER,"
                            "type VARCHAR,"
                            "FOREIGN KEY(item_id) REFERENCES items(item_id)"
                            ")")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS feed_id "
                            "ON feeds(feed_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS item_id "
                            "ON items(item_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS enclosure_id "
                            "ON enclosures(enclosure_id)")

    def get_feeds(self, feed_id):
        self.cursor.execute("SELECT * FROM feeds ORDER BY last_activity DESC")
        feeds = self.cursor.fetchall()
        return feeds

    def reset_updated_items(self, feed_id):
        self.cursor.execute("UPDATE feeds SET updated_items = 0 "
                            "WHERE feed_id = ?", (feed_id,))

    def add_updated_items(self, feed_id, value):
        self.cursor.execute("UPDATE feeds SET "
                            "updated_items = updated_items + ? "
                            "WHERE feed_id = ?", (value, feed_id))

    def get_feeds_due(self):
        self.cursor.execute("SELECT * FROM feeds "
                            "WHERE next_retrieval < ?", (int(time.time()),))
        feeds_due = self.cursor.fetchall()
        return feeds_due
                
    def update_feed_data(self, feed_id, key, value):
        self.cursor.execute("UPDATE feeds SET " + key + " = ? "
                            "WHERE feed_id = ?", (value, feed_id))

    def add_feed(self, href):
        values = (None, href, "", 0, 0, 0, False, 0)
        self.cursor.execute("INSERT INTO feeds "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", values)

    def delete_feed(self, feed_id):
        self.cursor.execute("DELETE FROM enclosures WHERE item_id IN "
                            "(SELECT item_id FROM items "
                            "WHERE feed_id = ?)", (feed_id,))
        self.cursor.execute("DELETE FROM items WHERE feed_id = ?", (feed_id,))
        self.cursor.execute("DELETE FROM feeds WHERE feed_id = ?", (feed_id,))

    def get_feed_items(self, feed_id):
        self.cursor.execute("SELECT item_id, feed_id, max(retrieved), seen,"
                            "author, title, feed_item_id, link, published,"
                            "summary, count() as count "
                            "FROM items "
                            "WHERE feed_id = ? "
                            "GROUP BY feed_item_id "
                            "ORDER BY published DESC LIMIT 100", (feed_id,))
        items = self.cursor.fetchall()
        return items

    def get_related_feed_items(self, feed_id, item_id):
        self.cursor.execute("SELECT * FROM items "
                            "WHERE feed_id = ? AND feed_item_id IN "
                            "(SELECT feed_item_id FROM items "
                            "WHERE item_id = ?)"
                            "ORDER BY retrieved DESC", (feed_id, item_id))
        items = self.cursor.fetchall()
        return items

    def set_seen(self, feed_id):
        self.cursor.execute("UPDATE items SET seen = TRUE "
                            "WHERE feed_id = ?", (feed_id,))

    def get_enclosures(self, item_id):
        self.cursor.execute("SELECT * FROM enclosures "
                            "WHERE item_id = ?", (item_id,))
        enclosures = self.cursor.fetchall()
        return enclosures

    def check_item_exists(self, item_id):
        self.cursor.execute("SELECT * FROM items "
                            "WHERE item_id = ?", (item_id,))
        rows = self.cursor.fetchall()
        return len(rows) != 0

    def add_item(self, feed_id, item_id, item, enclosures):
        values = (item_id, feed_id) + item
        self.cursor.execute("INSERT INTO items "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
        for enclosure in enclosures:
            values = (None, item_id) + enclosure
            self.cursor.execute("INSERT INTO enclosures "
                                "VALUES (?, ?, ?, ?, ?)", values)

    def commit(self):
        self.conn.commit()


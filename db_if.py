#!/usr/share/python3

import sqlite3
import time

class db_if:
    """interface to the database"""

    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def get_feeds(self, feed_id):
        self.cursor.execute("UPDATE feeds SET updated_items = 0 WHERE feed_id = ?", (feed_id,))
        self.cursor.execute("SELECT * FROM feeds ORDER BY last_activity DESC")
        feeds = self.cursor.fetchall()
        self.conn.commit()
        return feeds

    def get_feeds_due(self):
        self.cursor.execute("SELECT * FROM feeds WHERE next_retrieval < ?", (int(time.time()),))
        feeds_due = self.cursor.fetchall()
        return feeds_due
                
    def update_feed_data(self, feed_id, key, value):
        if (key == "updated_items"):
            self.cursor.execute("UPDATE feeds SET updated_items = "\
                                "updated_items + ? WHERE feed_id = ?", (value, feed_id))
        else:
            self.cursor.execute("UPDATE feeds SET " + key + " = ? WHERE feed_id = ?", (value, feed_id))
        self.conn.commit()

    def add_feed(self, href):
        values = (None, href, "", 0, 0, 0, False, 0)
        self.cursor.execute("INSERT INTO feeds VALUES (?, ?, ?, ?, ?, ?, ?, ?)", values)
        self.conn.commit()

    def delete_feed(self, feed_id):
        self.cursor.execute("DELETE FROM enclosures WHERE item_id IN "\
                            "(SELECT item_id FROM items WHERE feed_id = ?)", (feed_id,))
        self.cursor.execute("DELETE FROM items WHERE feed_id = ?", (feed_id,))
        self.cursor.execute("DELETE FROM feeds WHERE feed_id = ?", (feed_id,))
        self.conn.commit()

    def get_feed_items(self, feed_id):
        self.cursor.execute("SELECT * FROM items WHERE feed_id = ? ORDER BY published DESC LIMIT 100", (feed_id,))
        items = self.cursor.fetchall()
        self.cursor.execute("UPDATE items SET seen = TRUE WHERE feed_id = ?", (feed_id,))
        self.conn.commit()
        return items

    def get_enclosures(self, item_id):
        self.cursor.execute("SELECT * FROM enclosures WHERE item_id = ?", (item_id,))
        enclosures = self.cursor.fetchall()
        return enclosures

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
        self.conn.commit()


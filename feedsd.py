#!/usr/share/python3

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

import calendar
from db_if import db_if
import feedparser
import hashlib
import random
import time

db_path = "./feeds.db"
min_refresh_time = 30 * 60
max_refresh_time = 90 * 60

def refresh_feeds(db_if):
    print("refreshing feeds")
    feed_rows = db_if.get_feeds_due()
    for feed_row in feed_rows:
        print("getting feed", feed_row["title"])
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

-- Copyright (C) 2020 Marco Lochen

-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 2 of the License, or
-- (at your option) any later version.

-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.

-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

create table feeds (feed_id integer primary key,
                    href varchar,
                    title varchar,
                    last_retrieval timestamp,
                    next_retrieval timestamp,
                    last_activity timestamp,
                    disabled boolean,
                    updated_items integer);
create table items (item_id varchar primary key,
                    feed_id integer,
                    retrieved timestamp,
                    seen boolean,
                    author varchar,
                    title varchar,
                    feed_item_id varchar,
                    link varchar,
                    published timestamp,
                    summary varchar,
                    foreign key(feed_id) references feeds(feed_id));
create table enclosures (enclosure_id integer primary key,
                    item_id varchar,
                    href varchar,
                    length integer,
                    type varchar,
                    foreign key(item_id) references items(item_id));

create index feed_id on feeds(feed_id);
create index item_id on items(item_id);
create index enclosure_id on enclosures(enclosure_id);

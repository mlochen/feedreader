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

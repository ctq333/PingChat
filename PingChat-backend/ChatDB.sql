CREATE DATABASE IF NOT EXISTS ChatDB DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE ChatDB;
create table users
(
    id         bigint auto_increment
        primary key,
    username   varchar(64)                          not null,
    password   varchar(128)                         not null,
    nickname   varchar(64)                          null,
    avatar_url varchar(256)                         null,
    is_admin   tinyint(1) default 0                 null,
    is_banned  tinyint(1) default 0                 null,
    created_at datetime   default CURRENT_TIMESTAMP null,
    updated_at datetime   default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    is_muted   tinyint(1) default 0                 null,
    constraint username
        unique (username)
);

create table friends
(
    id         bigint auto_increment
        primary key,
    user_id    bigint                                                            not null,
    friend_id  bigint                                                            not null,
    remark     varchar(64)                                                       null,
    created_at datetime                                default CURRENT_TIMESTAMP null,
    status     enum ('pending', 'accepted', 'blocked') default 'accepted'        null,
    constraint user_id
        unique (user_id, friend_id),
    constraint friends_ibfk_1
        foreign key (user_id) references users (id),
    constraint friends_ibfk_2
        foreign key (friend_id) references users (id)
);

create index friend_id
    on friends (friend_id);

create table groupchat
(
    id         bigint auto_increment
        primary key,
    name       varchar(128)                       not null,
    owner_id   bigint                             not null,
    avatar_url varchar(256)                       null,
    notice     text                               null,
    created_at datetime default CURRENT_TIMESTAMP null,
    updated_at datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    constraint groupchat_ibfk_1
        foreign key (owner_id) references users (id)
);

create table group_members
(
    id        bigint auto_increment
        primary key,
    group_id  bigint                               not null,
    user_id   bigint                               not null,
    is_admin  tinyint(1) default 0                 null,
    joined_at datetime   default CURRENT_TIMESTAMP null,
    muted     tinyint(1) default 0                 null,
    constraint group_id
        unique (group_id, user_id),
    constraint group_members_ibfk_1
        foreign key (group_id) references groupchat (id),
    constraint group_members_ibfk_2
        foreign key (user_id) references users (id)
);

create index user_id
    on group_members (user_id);

create index owner_id
    on groupchat (owner_id);

create table messages
(
    id             bigint auto_increment
        primary key,
    sender_id      bigint                     not null,
    receiver_id    bigint                     null,
    group_id       bigint                     null,
    msg_type       varchar(20)                not null,
    content        text                       null,
    send_time      datetime                   not null,
    delivered_time datetime                   null,
    read_time      datetime                   null,
    status         varchar(20) default 'sent' null,
    extra          json                       null,
    constraint messages_ibfk_1
        foreign key (sender_id) references users (id)
);

create table message_receipts
(
    id             bigint auto_increment
        primary key,
    message_id     bigint   not null,
    user_id        bigint   not null,
    delivered_time datetime null,
    read_time      datetime null,
    constraint message_receipts_ibfk_1
        foreign key (message_id) references messages (id),
    constraint message_receipts_ibfk_2
        foreign key (user_id) references users (id)
);

create index message_id
    on message_receipts (message_id);

create index user_id
    on message_receipts (user_id);

create index group_id
    on messages (group_id);

create index idx_group_id
    on messages (group_id);

create index idx_receiver_id
    on messages (receiver_id);

create index idx_send_time
    on messages (send_time);

create index idx_sender_id
    on messages (sender_id);

create index receiver_id
    on messages (receiver_id);

create index sender_id
    on messages (sender_id);

create table user_login_logs
(
    id          bigint auto_increment
        primary key,
    user_id     bigint                               not null,
    login_time  datetime   default CURRENT_TIMESTAMP null,
    ip_address  varchar(64)                          null,
    device_info varchar(128)                         null,
    success     tinyint(1) default 1                 null,
    constraint user_login_logs_ibfk_1
        foreign key (user_id) references users (id)
);

create index user_id
    on user_login_logs (user_id);


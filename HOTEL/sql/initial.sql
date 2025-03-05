CREATE DATABASE IF NOT EXISTS flask_hotel_db;

USE flask_hotel_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

drop database if exists ocean_vista;

create database if not exists ocean_vista;

create table if not exists users (
    email varchar(150) not null primary key,
    name varchar(150) not null, 
    password varchar(100) not null, 
    phone_number varchar(15), 
    address_line_1 varchar(100),
    address_line_2 varchar(100),
    city varchar(50),
    state varchar(50),
    zipcode varchar(10),
    rewards int default 0,
    room_number varchar(30)
);

create table if not exists rooms (
    id int auto_increment, 
    img varchar(500) not null,
    room_number varchar(30) not null primary key, 
    room_type enum ('standard', 'deluxe', 'suite'),
    number_beds enum ('1','2'),
    rate int not null, 
    check_in time default '00:00:00',
    check_out time default '00:00:00',
    available enum ('available','booked','maintenance') default 'available',
    max_guests int default 2,
    free_wifi enum ('Y','N') default 'N',
    free_breakfast enum ('Y','N') default 'N',
    pool ('Y','N') default 'N',
    gym enum ('Y','N') default 'N',
    golf enum ('Y','N') default 'N',
    wheelchair_accessible enum ('Y','N') default 'N'
);

create table if not exists bookings (
    email varchar(150) not null primary key,
    name varchar(150) not null, 
    check_in time default '00:00:00',
    check_out time default '00:00:00',
    room_number varchar(30) not null primary key,
    fees int default 0
)

create table if not exists faq (
    id int auto_increment primary key,
    question varchar(150),
    answer varchar(500)
)

INSERT INTO users (username, email, password) VALUES ('admin', 'admin@example.com', 'password123');

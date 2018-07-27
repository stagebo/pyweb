DROP TABLE IF EXISTS t_jieba;
CREATE TABLE t_jieba
(
    f_time datetime NOT NULL,
    f_content nvarchar(2048) NOT NULL,
    f_ip nvarchar(64),
    f_city nvarchar(256)
);

DROP TABLE IF EXISTS t_comment;
CREATE TABLE t_comment
(
    f_id nvarchar(64) primary key not null,
    f_root_id nvarchar(64),
    f_pid nvarchar(64),
    f_time datetime,
    f_user_id nvarchar(64),
    f_user_type smallint,
	f_nickname nvarchar(64),
    f_content nvarchar(2048),
    f_ip nvarchar(16),
    f_city nvarchar(128),
    f_email nvarchar(32),
    f_praise int,
    f_trample int
);
DROP  TABLE IF EXISTS t_statistics;
CREATE TABLE t_statistics
(
    f_time datetime primary key not null,
    f_ip int,
    f_pv int,
    f_lip int,
    f_lpv int
);
DROP TABLE IF EXIXTS t_game_image;
CREATE TABLE t_game_image (
	id INT PRIMARY KEY auto_increment,
	f_url nvarchar (128),
	f_url1 nvarchar (128),
	f_url2 nvarchar (128),
	f_url3 nvarchar (128),
	f_url4 nvarchar (128),
	f_url5 nvarchar (128),
	f_url6 nvarchar (128),
	f_url7 nvarchar (128),
	f_url8 nvarchar (128),
	f_url9 nvarchar (128)
)
/*
create database marketDB character set utf8mb4;
CREATE USER administrador@localhost IDENTIFIED BY 'admin123';
GRANT ALL PRIVILEGES ON marketdb.* TO administrador@localhost;
FLUSH PRIVILEGES;
*/
SELECT * FROM marketdb.administracion_empresa;

USE master;
GO
CREATE DATABASE MundialDB;
GO
restore database MundialDB from disk = '/backup/full.bak' with recovery, replace; 
GO
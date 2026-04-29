docker exec -it fase2-mundial bash
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P Mundial.123 -C

SELECT name FROM sys.databases;
GO

USE MundialDB;
GO

BACKUP DATABASE MundialDB
TO DISK = '/backups/completo/full0.bak'
WITH FORMAT, 
     MEDIANAME = 'SQLServerBackups', 
     NAME = 'Full Backup del Mundial v0';
GO

# backup database MundialDB to disk = '/backups/completo/full1.bak' with format, medianame = 'SQLServerBackups', name = 'Full Backup del Mundial v1';

BACKUP DATABASE MundialDB
TO DISK = '/backups/diferencial/diff1.bak'
WITH DIFFERENTIAL,
     NAME = 'Diferencial del Mundial v1';
GO

# backup database MundialDB to disk = '/backups/diferencial/diff1.bak' with differential, name = 'Diferencial del Mundial v1';
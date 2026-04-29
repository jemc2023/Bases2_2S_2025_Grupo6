docker exec -it fase2-mundial-backup bash
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P Mundial.123 -C


CREATE DATABASE MundialDB;
GO

# Completo
RESTORE DATABASE MundialDB
FROM DISK = '/backups/completo/full0.bak'
WITH RECOVERY, REPLACE;
GO

# restore database MundialDB from disk = '/backups/completo/full0.bak' with recovery, replace;


# Diferencial
RESTORE DATABASE MundialDB
FROM DISK = '/backups/completo/full0.bak'
WITH NORECOVERY, REPLACE;
GO

RESTORE DATABASE MundialDB
TO DISK = '/backups/diferencial/diff1.bak'
WITH RECOVERY;
GO

# restore database MundialDB from disk = '/backups/completo/full0.bak' with norecovery, replace;
# restore database MundialDB from disk = '/backups/diferencial/diff2.bak' with recovery;
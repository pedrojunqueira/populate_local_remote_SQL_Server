CREATE TABLE person (
    personid INT IDENTITY(1,1) NOT NULL,
    firstName NVARCHAR(100),
    lastName NVARCHAR(100),
    age INT,
    DOB DATE,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT PK_person PRIMARY KEY (personid)
);
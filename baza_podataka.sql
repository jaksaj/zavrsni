ALTER DATABASE pmf
    COLLATE Latin1_General_CI_AS;

-- Table Razina
CREATE TABLE Razina (
    id INT IDENTITY(1,1) PRIMARY KEY,
    naziv VARCHAR(100)
);

-- Table Studij
CREATE TABLE Studij (
    isvu INT PRIMARY KEY,
    naziv VARCHAR(100),
    akronim VARCHAR(20),
    modul VARCHAR(100),
    razinaId INT,
    FOREIGN KEY (razinaId) REFERENCES Razina(id)
);

-- Table Semestar
CREATE TABLE Semestar (
    id INT IDENTITY(1,1) PRIMARY KEY,
    studijId INT,
    brojSemestra INT,
    FOREIGN KEY (studijId) REFERENCES Studij(isvu)
);

-- Table Kolegij
CREATE TABLE Kolegij (
    isvu INT PRIMARY KEY,
    PMkod VARCHAR(10),
    naziv VARCHAR(100),
    ects DECIMAL(3,1)
);

-- Table Djelatnik
CREATE TABLE Djelatnik (
    id INT PRIMARY KEY,
    ime VARCHAR(100), 
    prezime VARCHAR(100), 
    titula VARCHAR(50), 
    nastavnaTitula VARCHAR(50) 
);

-- Table AkademskaGodina
CREATE TABLE AkademskaGodina (
    id INT IDENTITY(1,1) PRIMARY KEY,
    naziv VARCHAR(100),
    godinaPocetak INT,
    godinaZavrsetak INT
);

-- Table KolegijGodina
CREATE TABLE KolegijGodina (
    id INT IDENTITY(1,1) PRIMARY KEY,
    kolegijId INT,
    akademskaGodinaId INT,
    FOREIGN KEY (kolegijId) REFERENCES Kolegij(isvu),
    FOREIGN KEY (akademskaGodinaId) REFERENCES AkademskaGodina(id)
);

-- Table NositeljKolegij
CREATE TABLE NositeljKolegij (
    kolegijId INT,
    nositeljId INT,
    PRIMARY KEY (kolegijId, nositeljId),
    FOREIGN KEY (kolegijId) REFERENCES KolegijGodina(id),
    FOREIGN KEY (nositeljId) REFERENCES Djelatnik(id)
);

-- Table SemestarGodina
CREATE TABLE SemestarGodina (
    id INT IDENTITY(1,1) PRIMARY KEY,
    semestarId INT,
    akademskaGodinaId INT,
    FOREIGN KEY (semestarId) REFERENCES Semestar(id),
    FOREIGN KEY (akademskaGodinaId) REFERENCES AkademskaGodina(id)
);

-- Table SemestarKolegij
CREATE TABLE SemestarKolegij (
    kolegijId INT,
    semestarId INT,
    erasmusStudenti INT,
    obavezan BIT,
    PRIMARY KEY (kolegijId, semestarId),
    FOREIGN KEY (kolegijId) REFERENCES KolegijGodina(id),
    FOREIGN KEY (semestarId) REFERENCES SemestarGodina(id)
);

-- Table TipNastave
CREATE TABLE TipNastave (
    id INT IDENTITY(1,1) PRIMARY KEY,
    akronim VARCHAR(5),
    naziv VARCHAR(50)
);

-- Table KolegijNastava
CREATE TABLE KolegijNastava (
    tipNastaveId INT,
    kolegijId INT,
    brojSati INT,
    PRIMARY KEY (tipNastaveId, kolegijId),
    FOREIGN KEY (tipNastaveId) REFERENCES TipNastave(id),
    FOREIGN KEY (kolegijId) REFERENCES KolegijGodina(id)
);
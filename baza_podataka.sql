CREATE TABLE Razina (
    id INT IDENTITY(1,1) PRIMARY KEY,
    naziv VARCHAR(100)
);

CREATE TABLE Studij (
    isvu INT PRIMARY KEY,
    naziv VARCHAR(100),
    akronim VARCHAR(20),
    modul VARCHAR(100),
    razinaId INT,
    FOREIGN KEY (razinaId) REFERENCES Razina(id)
);

CREATE TABLE Semestar (
    id INT IDENTITY(1,1) PRIMARY KEY,
    studijId INT,
    brojSemestra INT,
    FOREIGN KEY (studijId) REFERENCES Studij(isvu)
);

CREATE TABLE Kolegij (
    isvu INT PRIMARY KEY,
    PMkod VARCHAR(10),
    naziv VARCHAR(100),
    ects DECIMAL(3,1)
);

CREATE TABLE Djelatnik (
    id INT PRIMARY KEY,
    ime VARCHAR(100), 
    prezime VARCHAR(100), 
    titula VARCHAR(50), 
    nastavnaTitula VARCHAR(50) 
);

CREATE TABLE AkademskaGodina (
    godinaPocetak INT PRIMARY KEY
);

CREATE TABLE KolegijGodina (
    id INT IDENTITY(1,1) PRIMARY KEY,
    kolegijId INT,
    akademskaGodinaId INT,
    erasmusStudenti INT,
    FOREIGN KEY (kolegijId) REFERENCES Kolegij(isvu),
    FOREIGN KEY (akademskaGodinaId) REFERENCES AkademskaGodina(godinaPocetak)
);

CREATE TABLE NositeljKolegij (
    kolegijId INT,
    nositeljId INT,
    PRIMARY KEY (kolegijId, nositeljId),
    FOREIGN KEY (kolegijId) REFERENCES KolegijGodina(id),
    FOREIGN KEY (nositeljId) REFERENCES Djelatnik(id)
);

CREATE TABLE SemestarGodina (
    id INT IDENTITY(1,1) PRIMARY KEY,
    semestarId INT,
    akademskaGodinaId INT,
    FOREIGN KEY (semestarId) REFERENCES Semestar(id),
    FOREIGN KEY (akademskaGodinaId) REFERENCES AkademskaGodina(godinaPocetak)
);

CREATE TABLE SemestarKolegij (
    kolegijId INT,
    semestarId INT,
    obvezan BIT,
    PRIMARY KEY (kolegijId, semestarId),
    FOREIGN KEY (kolegijId) REFERENCES KolegijGodina(id),
    FOREIGN KEY (semestarId) REFERENCES SemestarGodina(id)
);

CREATE TABLE TipNastave (
    id INT IDENTITY(1,1) PRIMARY KEY,
    akronim VARCHAR(5),
    naziv VARCHAR(50)
);

CREATE TABLE KolegijNastava (
    tipNastaveId INT,
    kolegijId INT,
    brojSati INT,
    PRIMARY KEY (tipNastaveId, kolegijId),
    FOREIGN KEY (tipNastaveId) REFERENCES TipNastave(id),
    FOREIGN KEY (kolegijId) REFERENCES KolegijGodina(id)
);
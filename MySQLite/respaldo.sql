PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE Ubicacion(idUbicacion INTEGER PRIMARY KEY AUTOINCREMENT, nombreLugar TEXT NOT NULL, direccion TEXT, tipoLugar TEXT CHECK(tipoLugar IN ('plaza','tienda','mercado','otro')),contacto TEXT);
INSERT INTO Ubicacion VALUES(1,'Plaza Central','Av. SiempreViva #777','plaza','7351234567');
CREATE TABLE Maquinas(idMaquina INTEGER PRIMARY KEY, nombreMaquina TEXT NOT NULL, fechaInstalacion DATE, estatus TEXT CHECK(estatus IN('activa','mantenimiento','fuera_de_servicio'))NOT NULL,modelo TEXT, descripcion TEXT, Ubicacion_idUbicacion INTEGER NOT NULL,FOREIGN KEY (Ubicacion_idUbicacion) REFERENCES Ubicacion (idUbicacion) ON DELETE NO ACTION ON UPDATE NO ACTION);
INSERT INTO Maquinas VALUES(1,'Garra A1','2025-10-25','activa','GX-200','Maquina con luces LED',1);
CREATE TABLE IF NOT EXISTS "Stock" (
    idStock INTEGER PRIMARY KEY AUTOINCREMENT,
    producto TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    ultimaAct TEXT DEFAULT (datetime('now','localtime')),
    Maquina_idMaquina INTEGER,
    Ubicacion_idUbicacion INTEGER,
    FOREIGN KEY (Maquina_idMaquina) REFERENCES Maquina(idMaquina) ON DELETE NO ACTION ON UPDATE NO ACTION,
    FOREIGN KEY (Ubicacion_idUbicacion) REFERENCES Ubicacion(idUbicacion) ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE TABLE Recaudacion (idRecaudacion INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT DEFAULT (datetime('now','localtime')), monto DECIMAL(10,2) NOT NULL, Maquina_idMaquina INTEGER, Ubicacion_idUbicacion INTEGER, FOREIGN KEY (Maquina_idMaquina) REFERENCES Maquinas(idMaquina) ON DELETE NO ACTION ON UPDATE NO ACTION, FOREIGN KEY (Ubicacion_idUbicacion) REFERENCES Ubicacion(idUbicacion) ON DELETE NO ACTION ON UPDATE NO ACTION);
INSERT INTO sqlite_sequence VALUES('Ubicacion',1);
COMMIT;

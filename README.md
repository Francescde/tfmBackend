# RouterFirstVersion 

## Instalacio 

#### dependencies
les dependencies són:
Flask==1.0.2
Flask-Cors==3.0.7
Flask-RESTful==0.3.7
GDAL==2.4.0
geog==0.0.2
Jinja2==2.10
psycopg2==2.8.2
Instalar amb:
```
pip install -r requirements.txt
```
#### Posar a punt la base de dades:
generar una bd per configurar la connexio es fa al fitxer **database.json** de **configurationFiles**

Executar el fitxer **sqlFiles/inserta_taules.sql**
depositar via **osm2psql** la cartografia necesaria a la bd (amb la opcio --slim)
depositar la cartografia de bombers a la bd jo he empreat **Qgis**
executar el script **storegraphToDB.py**

#### Compilar les llibreries de explirar en c:
Dins de router executar 
```
g++ -c -fPIC dijkstraListCFile4.cc -o dijkstraListCFile3.o
g++ -shared -W1,-soname,dijkstraListCFile3.so -o dijkstraListCFile3.so dijkstraListCFile3.o


g++ -c -fPIC dijkstraMultimodalTotal.cc -o dijkstraMultimodalTotal.o
g++ -shared -W1,-soname,dijkstraMultimodalTotal.so -o dijkstraMultimodalTotal.so dijkstraMultimodalTotal.o
```

#### Executar flask:
El port i host es poden modificar a **configurationFiles/flaskConfig.json**
executar
```
python index.py
```

import json
import pyodbc


def deep_search(obj, key, results=None):
    if results is None:
        results = set()
    if not obj:
        return list(results)
    if key in obj:
        results.add(obj[key])
    for k, v in obj.items():
        if isinstance(v, dict):
            deep_search(v, key, results)
    return list(results)

def find_child_keys(obj, key, results=None):
    if results is None:
        results = set()
    if not obj:
        return list(results)
    if key in obj and isinstance(obj[key], dict):
        for child_key in obj[key]:
            results.add(child_key)
    for k, v in obj.items():
        if isinstance(v, dict):
            find_child_keys(v, key, results)
    return list(results)

def find_child_key_values(obj, key, results=None):
    if results is None:
        results = {}
    if not obj:
        return results
    if key in obj and isinstance(obj[key], dict):
        for child_key, child_value in obj[key].items():
            results[child_key] = child_value
    for k, v in obj.items():
        if isinstance(v, dict):
            find_child_key_values(v, key, results)
    return results

def find_key_values_at_depth(obj, depth, current_depth=0, results=None):
    if results is None:
        results = {}
    if not obj:
        return results
    if current_depth == depth:
        results.update(obj)
    else:
        for k, v in obj.items():
            if isinstance(v, dict):
                find_key_values_at_depth(v, depth, current_depth + 1, results)
    return results

def get_grandchild_values(obj):
    grandchild_values = []
    for child_key, child_value in obj.items():
        if isinstance(child_value, dict):
            grandchild_values.extend(child_value.values())
    return grandchild_values

def save_to_db(cursor, conn, table_name, columns, data):
    cursor.execute(f"SELECT {columns[0]} FROM {table_name}")
    existing_values = [value[0] for value in cursor.fetchall()]
    
    data = [row for row in data if row[0] not in existing_values]
    
    if data:
        columns_str = ', '.join(columns)
        values_str = ', '.join(['?'] * len(columns))
        sql_statement = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
        
        cursor.executemany(sql_statement, data)
        conn.commit()

def save_to_db_without_check(cursor, conn, table_name, columns, data):    
    if data:
        columns_str = ', '.join(columns)
        values_str = ', '.join(['?'] * len(columns))
        sql_statement = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
        cursor.executemany(sql_statement, data)
        conn.commit()

def mapirajStraniKljuc(cursor,id, column_name, foreign_table, foreign_column, data_list):
    for item in data_list:
        cursor.execute(f"SELECT {id} FROM {foreign_table} WHERE {foreign_column} = ?", (item[column_name],))
        foreign_id = cursor.fetchone()[0]
        item[column_name] = foreign_id

def unosGodine():
    while True:
        godinaPocetak = input("Unesite godinu početka akademske godine: ")
        print(f"Unijeli ste: {godinaPocetak}")
        potvrda = input("Je li ovo točno? (da/ne): ").strip().lower()
        if potvrda == 'da':
            return godinaPocetak
        
def format_values(values):
    return [[value] for value in values]

with open('fakultetPodaci2023.JSON', 'r', encoding='utf-8') as f:
    data = f.read()

try:

    godinaPocetak = unosGodine()

    jsonData = json.loads(data)

    conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                      "Server=DESKTOP-3L6T4TD\SQLEXPRESS;"
                      "Database=pmf;"
                      "Trusted_Connection=yes;"
                      "charset=utf8;")
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM AkademskaGodina WHERE godinaPocetak = ?", (godinaPocetak,))
    exists = cursor.fetchone()

    if not exists:
        cursor.execute('''
            INSERT INTO AkademskaGodina (godinaPocetak)
            VALUES (?)
        ''', (godinaPocetak,))

    akademskaGodinaId = godinaPocetak

    razine = deep_search(jsonData, 'razina')
    razineFormatirano = format_values(razine)
    save_to_db(cursor, conn, 'Razina', ['naziv'], razineFormatirano)

    tipoviNastave = find_child_keys(jsonData, 'satnica')
    tipoviNastaveFormatirano = format_values(tipoviNastave)
    save_to_db(cursor, conn, 'TipNastave', ['akronim'], tipoviNastaveFormatirano)

    studiji = get_grandchild_values(jsonData)
    studijiTablica = []
    semestriTablica = []
    kolegijiTablica = []
    for studij in studiji:
        zapis_studij = {
            'isvu': studij['Info']['ISVU'],
            'akronim': studij['Info']['akronim'],
            'razina': studij['Info']['razina'],
            'naziv': studij['Info']['studij'],
            'modul': studij['Info']['modul'],
        }
        studijiTablica.append(zapis_studij)

        for sem_key, sem_value in studij.items():
            if sem_key.isdigit():
                zapis_semestar = {
                    'studij': studij['Info']['ISVU'],
                    'semester': sem_value['semester'],
                }
                semestriTablica.append(zapis_semestar)
                for group_type in ["obvezni", "izborni"]:
                    group_data = sem_value.get(group_type, {})
                    if isinstance(group_data, dict):
                        for group_key, group_value in group_data.items():
                            groupID = group_value.get("groupID")
                            for predmet_key, predmet_value in group_value.get("predmeti", {}).items():
                                kolegij = {
                                    "studij": studij['Info']['ISVU'],
                                    "semester": sem_value['semester'],
                                    "groupID": groupID,
                                    "subjectID": predmet_value.get("subjectID"),
                                    "PMkod": predmet_value.get("PMkod"),
                                    "ISVU": predmet_value.get("ISVU"),
                                    "naziv": predmet_value.get("naziv"),
                                    "ECTS": predmet_value.get("ECTS"),
                                    "satnica": predmet_value.get("satnica"),
                                    "nositelji": predmet_value.get("nositelji"),
                                    "erasmus": predmet_value.get("erasmus"),
                                    "obvezan": 1 if group_type == "obvezni" else 0
                                }
                                kolegijiTablica.append(kolegij)

    mapirajStraniKljuc(cursor,'id', 'razina', 'razina', 'naziv', studijiTablica)
    studijiTablica = [(studij['isvu'], studij['akronim'], studij['razina'], studij['naziv'], studij['modul']) for studij in studijiTablica]
    save_to_db(cursor, conn, 'Studij', ['isvu', 'akronim', 'razinaId', 'naziv', 'modul'], studijiTablica)

    mapirajStraniKljuc(cursor,'isvu', 'studij', 'Studij', 'isvu', semestriTablica)
    semestriTablica = [(semestar['studij'], semestar['semester']) for semestar in semestriTablica]
    save_to_db(cursor, conn, 'Semestar', ['studijId', 'brojSemestra'], semestriTablica)

    cursor.execute("SELECT id, studijId, brojSemestra FROM Semestar")
    semestar_rows = cursor.fetchall()

    semestar_id_map = { (row[1], row[2]): row[0] for row in semestar_rows }

    semestriGodina = []
    for semestar in semestriTablica:
        studijId = semestar[0]
        brojSemestra = semestar[1]
        semestarId = semestar_id_map[(studijId, brojSemestra)]
        semestriGodina.append((semestarId, akademskaGodinaId))

    save_to_db_without_check(cursor, conn, 'SemestarGodina', ['semestarId', 'akademskaGodinaId'], semestriGodina)

    unique_isvu = set()
    kolegiji = []
    kolegijiGodina = []
    kolegijNositelji = []
    unique_kolegiji = []

    for kolegij in kolegijiTablica:
        isvu = kolegij['ISVU']
        if isvu not in unique_isvu:
            unique_isvu.add(isvu)
            unique_kolegiji.append(kolegij)
            kolegiji.append((kolegij['ISVU'], kolegij['PMkod'], kolegij['naziv'], kolegij['ECTS']))
            erasmus_value = 0 if kolegij.get('erasmus') is None else kolegij['erasmus']        
            kolegijiGodina.append((kolegij['ISVU'],akademskaGodinaId, erasmus_value))
    
    save_to_db(cursor, conn, 'Kolegij', ['isvu', 'PMkod', 'naziv', 'ects'], kolegiji)
    save_to_db(cursor, conn, 'KolegijGodina', ['kolegijId', 'akademskaGodinaId','erasmusStudenti'], kolegijiGodina)

    djelatniciPodaci = find_child_key_values(jsonData, 'nositelji')
    djelatnici = []
    for djelatnik in djelatniciPodaci.values():
        zapis_djelatnik = {
            'id': djelatnik['userID'],
            'firstName': djelatnik['firstName'],
            'lastName': djelatnik['lastName'],
            'title': djelatnik['title'],
            'teachingTitle': djelatnik['teachingTitle'],
        }
        djelatnici.append(zapis_djelatnik)
    djelatnici = [(djelatnik['id'],djelatnik['firstName'], djelatnik['lastName'], djelatnik['title'], djelatnik['teachingTitle']) for djelatnik in djelatnici]
    save_to_db(cursor, conn, 'djelatnik', ['id','ime', 'prezime', 'titula', 'nastavnaTitula'], djelatnici)

    for kolegij in unique_kolegiji:
        isvu = kolegij['ISVU']
        cursor.execute("SELECT id FROM KolegijGodina WHERE kolegijId = ? AND akademskaGodinaId = ?", (isvu, akademskaGodinaId))
        kolegijGodinaIdRedak = cursor.fetchone()
        if kolegijGodinaIdRedak:
            kolegijGodinaId = kolegijGodinaIdRedak[0]
            if kolegij['satnica'] and isinstance(kolegij['satnica'], dict):
                for tip, broj_sati in kolegij['satnica'].items():
                    cursor.execute("SELECT id FROM TipNastave WHERE akronim = ?", (tip,))
                    tip_nastave_id_row = cursor.fetchone()
                    if tip_nastave_id_row:
                        tip_nastave_id = tip_nastave_id_row[0]
                        cursor.execute("INSERT INTO KolegijNastava (tipNastaveId, kolegijId, brojSati) VALUES (?, ?, ?)",
                                    (tip_nastave_id, kolegijGodinaId, broj_sati))
            if isinstance(kolegij['nositelji'], dict):
                for nositelj in kolegij['nositelji'].values():
                    nositelj_id = nositelj['userID']
                    cursor.execute("SELECT id FROM Djelatnik WHERE id = ?", (nositelj_id,))
                    nositelj_id_row = cursor.fetchone()
                    if nositelj_id_row:
                        nositelj_id = nositelj_id_row[0]
                        kolegijNositelji.append((kolegijGodinaId, nositelj_id))

    save_to_db(cursor, conn, 'NositeljKolegij', ['kolegijId', 'nositeljId'], kolegijNositelji)

    for kolegij in kolegijiTablica:
        isvu = kolegij['ISVU']
        studij = kolegij['studij']
        semestar = kolegij['semester']
        obvezan = kolegij['obvezan'] 

        cursor.execute("SELECT id FROM KolegijGodina WHERE kolegijId = ? AND akademskaGodinaId = ?", (isvu, akademskaGodinaId))
        kolegijGodinaIdRedak = cursor.fetchone()
        if kolegijGodinaIdRedak:
            kolegijGodinaId = kolegijGodinaIdRedak[0]
            
            cursor.execute("SELECT id FROM Semestar WHERE studijId = ? AND brojSemestra = ?", (studij, semestar))
            semestarIdRedak = cursor.fetchone()
            if semestarIdRedak:
                semestarId = semestarIdRedak[0]

                cursor.execute("SELECT id FROM SemestarGodina WHERE semestarId = ? AND akademskaGodinaId = ?", (semestarId, akademskaGodinaId))
                semestarGodinaIdRedak = cursor.fetchone()
                if semestarGodinaIdRedak:
                    semestarGodinaId = semestarGodinaIdRedak[0]

                    cursor.execute("INSERT INTO SemestarKolegij (kolegijId, semestarId, obvezan) VALUES (?, ?, ?)",
                                (kolegijGodinaId, semestarGodinaId, obvezan))

    conn.commit()
    cursor.close()
    conn.close()

except json.JSONDecodeError as error:
    print('Error parsing JSON:', error)
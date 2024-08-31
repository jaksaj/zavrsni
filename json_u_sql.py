import json
import os
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

def update_foreign_key(cursor,id, column_name, foreign_table, foreign_column, data_list):
    for item in data_list:
        cursor.execute(f"SELECT {id} FROM {foreign_table} WHERE {foreign_column} = ?", (item[column_name],))
        foreign_id = cursor.fetchone()[0]
        item[column_name] = foreign_id

def prompt_for_academic_year():
    while True:
        start_year = input("Enter the start year of the academic year: ")
        end_year = input("Enter the end year of the academic year: ")
        print(f"You entered: Start Year = {start_year}, End Year = {end_year}")
        confirm = input("Is this correct? (yes/no): ").strip().lower()
        if confirm == 'yes':
            return start_year, end_year
        
def format_values(values):
    return [[value] for value in values]

with open('fakultetPodaci2023.JSON', 'r', encoding='utf-8') as f:
    data = f.read()

try:

    start_year, end_year = prompt_for_academic_year()

    jsonData = json.loads(data)

    conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                      "Server=DESKTOP-3L6T4TD\SQLEXPRESS;"
                      "Database=pmf;"
                      "Trusted_Connection=yes;"
                      "charset=utf8;")
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO AkademskaGodina (godinaPocetak, godinaZavrsetak)
    OUTPUT INSERTED.ID
    VALUES (?, ?)
    ''', (start_year, end_year))

    akademskaGodinaId = cursor.fetchone()[0]

    razina_values = deep_search(jsonData, 'razina')
    formatted_razina_values = format_values(razina_values)
    save_to_db(cursor, conn, 'Razina', ['naziv'], formatted_razina_values)

    tip_nastave_values = find_child_keys(jsonData, 'satnica')
    formatted_tip_nastave_values = format_values(tip_nastave_values)
    save_to_db(cursor, conn, 'TipNastave', ['akronim'], formatted_tip_nastave_values)

    studiji = get_grandchild_values(jsonData)
    table_studiji = []
    table_semestri = []
    table_kolegiji = []
    for studij in studiji:
        zapis_studij = {
            'isvu': studij['Info']['ISVU'],
            'akronim': studij['Info']['akronim'],
            'razina': studij['Info']['razina'],
            'naziv': studij['Info']['studij'],
            'modul': studij['Info']['modul'],
        }
        table_studiji.append(zapis_studij)

        for sem_key, sem_value in studij.items():
            if sem_key.isdigit():
                zapis_semestar = {
                    'studij': studij['Info']['ISVU'],
                    'semester': sem_value['semester'],
                }
                table_semestri.append(zapis_semestar)
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
                                    "obavezan": 1 if group_type == "obvezni" else 0
                                }
                                table_kolegiji.append(kolegij)

    update_foreign_key(cursor,'id', 'razina', 'razina', 'naziv', table_studiji)
    table_studiji = [(studij['isvu'], studij['akronim'], studij['razina'], studij['naziv'], studij['modul']) for studij in table_studiji]
    save_to_db(cursor, conn, 'Studij', ['isvu', 'akronim', 'razinaId', 'naziv', 'modul'], table_studiji)

    update_foreign_key(cursor,'isvu', 'studij', 'Studij', 'isvu', table_semestri)
    table_semestri = [(semestar['studij'], semestar['semester']) for semestar in table_semestri]
    save_to_db(cursor, conn, 'Semestar', ['studijId', 'brojSemestra'], table_semestri)

    cursor.execute("SELECT id, studijId, brojSemestra FROM Semestar")
    semestar_rows = cursor.fetchall()

    semestar_id_map = { (row[1], row[2]): row[0] for row in semestar_rows }

    semestar_godina_data = []
    for semestar in table_semestri:
        studijId = semestar[0]
        brojSemestra = semestar[1]
        semestarId = semestar_id_map[(studijId, brojSemestra)]
        semestar_godina_data.append((semestarId, akademskaGodinaId))

    save_to_db_without_check(cursor, conn, 'SemestarGodina', ['semestarId', 'akademskaGodinaId'], semestar_godina_data)

    unique_isvu = set()
    kolegiji = []
    kolegijiGodina = []
    kolegijNositelji = []
    unique_kolegiji = []

    for kolegij in table_kolegiji:
        isvu_value = kolegij['ISVU']
        if isvu_value not in unique_isvu:
            unique_isvu.add(isvu_value)
            unique_kolegiji.append(kolegij)
            kolegiji.append((kolegij['ISVU'], kolegij['PMkod'], kolegij['naziv'], kolegij['ECTS']))
            kolegijiGodina.append((kolegij['ISVU'],akademskaGodinaId))
    
    save_to_db(cursor, conn, 'Kolegij', ['isvu', 'PMkod', 'naziv', 'ects'], kolegiji)
    save_to_db(cursor, conn, 'KolegijGodina', ['kolegijId', 'akademskaGodinaId'], kolegijiGodina)

    djelatnici = find_child_key_values(jsonData, 'nositelji')
    table_djelatnici = []
    for djelatnik in djelatnici.values():
        zapis_djelatnik = {
            'id': djelatnik['userID'],
            'firstName': djelatnik['firstName'],
            'lastName': djelatnik['lastName'],
            'title': djelatnik['title'],
            'teachingTitle': djelatnik['teachingTitle'],
        }
        table_djelatnici.append(zapis_djelatnik)
    table_djelatnici = [(djelatnik['id'],djelatnik['firstName'], djelatnik['lastName'], djelatnik['title'], djelatnik['teachingTitle']) for djelatnik in table_djelatnici]
    save_to_db(cursor, conn, 'djelatnik', ['id','ime', 'prezime', 'titula', 'nastavnaTitula'], table_djelatnici)

    for kolegij in unique_kolegiji:
        isvu_value = kolegij['ISVU']
        cursor.execute("SELECT id FROM KolegijGodina WHERE kolegijId = ? AND akademskaGodinaId = ?", (isvu_value, akademskaGodinaId))
        kolegij_godina_id_row = cursor.fetchone()
        if kolegij_godina_id_row:
            kolegij_godina_id = kolegij_godina_id_row[0]
            if kolegij['satnica'] and isinstance(kolegij['satnica'], dict):
                for tip, broj_sati in kolegij['satnica'].items():
                    cursor.execute("SELECT id FROM TipNastave WHERE akronim = ?", (tip,))
                    tip_nastave_id_row = cursor.fetchone()
                    if tip_nastave_id_row:
                        tip_nastave_id = tip_nastave_id_row[0]
                        cursor.execute("INSERT INTO KolegijNastava (tipNastaveId, kolegijId, brojSati) VALUES (?, ?, ?)",
                                    (tip_nastave_id, kolegij_godina_id, broj_sati))
            if isinstance(kolegij['nositelji'], dict):
                for nositelj in kolegij['nositelji'].values():
                    nositelj_id = nositelj['userID']
                    cursor.execute("SELECT id FROM Djelatnik WHERE id = ?", (nositelj_id,))
                    nositelj_id_row = cursor.fetchone()
                    if nositelj_id_row:
                        nositelj_id = nositelj_id_row[0]
                        kolegijNositelji.append((kolegij_godina_id, nositelj_id))

    save_to_db(cursor, conn, 'NositeljKolegij', ['kolegijId', 'nositeljId'], kolegijNositelji)

    for kolegij in table_kolegiji:
        isvu_value = kolegij['ISVU']
        studij_value = kolegij['studij']
        semester_value = kolegij['semester']
        erasmus_value = 0 if kolegij.get('erasmus') is None else kolegij['erasmus']        
        is_obavezan = kolegij['obavezan']  # Directly use the stored obavezan value

        cursor.execute("SELECT id FROM KolegijGodina WHERE kolegijId = ? AND akademskaGodinaId = ?", (isvu_value, akademskaGodinaId))
        kolegij_godina_id_row = cursor.fetchone()
        if kolegij_godina_id_row:
            kolegij_godina_id = kolegij_godina_id_row[0]
            
            cursor.execute("SELECT id FROM Semestar WHERE studijId = ? AND brojSemestra = ?", (studij_value, semester_value))
            semestar_id_row = cursor.fetchone()
            if semestar_id_row:
                semestar_id = semestar_id_row[0]

                cursor.execute("SELECT id FROM SemestarGodina WHERE semestarId = ? AND akademskaGodinaId = ?", (semestar_id, akademskaGodinaId))
                semestar_godina_id_row = cursor.fetchone()
                if semestar_godina_id_row:
                    semestar_godina_id = semestar_godina_id_row[0]

                    cursor.execute("INSERT INTO SemestarKolegij (kolegijId, semestarId, erasmusStudenti, obavezan) VALUES (?, ?, ?, ?)",
                                (kolegij_godina_id, semestar_godina_id, erasmus_value, is_obavezan))

    conn.commit()
    cursor.close()
    conn.close()

except json.JSONDecodeError as error:
    print('Error parsing JSON:', error)
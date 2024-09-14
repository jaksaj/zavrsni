import json
import pyodbc
import time
from collections import defaultdict

execution_times = {}

def measureTime(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            print("Naziv upita: ", name)
            print("Vrijeme izvršavanja upita: ", execution_time)
            execution_times[name] = execution_time
            return result
        return wrapper
    return decorator

def printQueryResults():
    print("Rezultati upita:", cursor.fetchall())

with open('fakultetPodaci2023.JSON', 'r', encoding='utf-8') as f:
    data = f.read()

jsonData = json.loads(data)

conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                    "Server=DESKTOP-3L6T4TD\SQLEXPRESS;"
                    "Database=pmf;"
                    "Trusted_Connection=yes;"
                    "charset=utf8;")
cursor = conn.cursor()

@measureTime("Broj kolegija po nositelju")
def execute_query1():
    cursor.execute("select d.ime,d.prezime, COUNT(d.id) as 'Broj kolegija' from Djelatnik d left join NositeljKolegij nk on nk.nositeljId=d.id left join KolegijGodina kg on kg.id=nk.kolegijId where kg.akademskaGodinaId=2023 group by d.id, d.ime, d.prezime order by COUNT(d.id) desc")
    print("Rezultati upita:", cursor.fetchall())


@measureTime("Kolegiji jednog nositelja")
def execute_query2():
    cursor.execute("select d.ime,d.prezime, k.naziv from Djelatnik d left join NositeljKolegij nk on nk.nositeljId=d.id left join KolegijGodina kg on kg.id=nk.kolegijId left join Kolegij k on k.isvu=kg.kolegijId where kg.akademskaGodinaId=2023 and d.prezime='Zaharija'")
    print("Rezultati upita:", cursor.fetchall())

@measureTime("Sati nastave po ECTS")
def execute_query3():
    cursor.execute("select k.naziv, k.ects, SUM(kn.brojSati) as 'Broj sati', SUM(kn.brojSati)/k.ects as 'Broj sati po ECTS' from KolegijGodina kg left join Kolegij k on k.isvu=kg.kolegijId left join KolegijNastava kn on kn.kolegijId=kg.id where kg.akademskaGodinaId=2023 and k.ects=5 group by k.naziv, k.ects order by [Broj sati po ECTS] desc")
    print("Rezultati upita:", cursor.fetchall())

@measureTime("Kolegiji jednog studija")	
def execute_query4():
    cursor.execute("Select k.naziv,k.ects,s.brojSemestra, sk.obvezan from SemestarKolegij sk  left join SemestarGodina sg on sk.semestarId=sg.id left join KolegijGodina kg on kg.id=sk.kolegijId left join Semestar s on s.id=sg.semestarId left join Kolegij k on k.isvu=kg.kolegijId left join Studij st on st.isvu=s.studijId where st.akronim='PD-I' and sg.akademskaGodinaId=2023 order by s.brojSemestra, sk.obvezan desc")
    print("Rezultati upita:", cursor.fetchall())

@measureTime("Svi kolegiji po studiju i semestru")
def execute_query5():
    cursor.execute("Select k.naziv,k.ects,s.brojSemestra, sk.obvezan, st.naziv, st.modul, r.naziv from SemestarKolegij sk  left join SemestarGodina sg on sk.semestarId=sg.id left join KolegijGodina kg on kg.id=sk.kolegijId left join Semestar s on s.id=sg.semestarId left join Kolegij k on k.isvu=kg.kolegijId left join Studij st on st.isvu=s.studijId left join Razina r on r.id=st.razinaId where sg.akademskaGodinaId=2023 order by r.naziv,st.naziv ,st.modul,s.brojSemestra, sk.obvezan desc")
    print("Rezultati upita:", cursor.fetchall())

execute_query1()
execute_query2()
execute_query3()
execute_query4()
execute_query5()


@measureTime("Broj kolegija po nositelju (JSON)")
def execute_json1(jsonData):
    result = {}

    def extract_predmeti(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "predmeti":
                    for predmet_id, predmet_data in value.items():
                        isvu = predmet_data.get("ISVU")
                        
                        nositelji = predmet_data.get("nositelji", {})
                        nositelji_list = []
                        if isinstance(nositelji, dict):
                            for nositelj_id, nositelj_data in nositelji.items():
                                nositelji_list.append({
                                    "userID": nositelj_data.get("userID"),
                                    "firstName": nositelj_data.get("firstName"),
                                    "lastName": nositelj_data.get("lastName")
                                })
                        
                        result[predmet_id] = {
                            "ISVU": isvu,
                            "nositelji": nositelji_list
                        }
                else:
                    extract_predmeti(value)
        elif isinstance(data, list):
            for item in data:
                extract_predmeti(item)

    extract_predmeti(jsonData)

    user_counts = defaultdict(lambda: {"firstName": "", "lastName": "", "count": 0})

    for predmet_id, predmet_data in result.items():
        for nositelj in predmet_data["nositelji"]:
            user_id = nositelj["userID"]
            user_counts[user_id]["firstName"] = nositelj["firstName"]
            user_counts[user_id]["lastName"] = nositelj["lastName"]
            user_counts[user_id]["count"] += 1

    sorted_user_counts = sorted(user_counts.items(), key=lambda x: x[1]['count'], reverse=True)

    print("Rezultati upita:", sorted_user_counts)


@measureTime("Kolegiji jednog nositelja (JSON)")
def execute_json2(jsonData):
    result = {}
    lastName = "Zaharija"
    
    def extract_predmeti(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "predmeti":
                    for predmet_id, predmet_data in value.items():
                        isvu = predmet_data.get("ISVU")
                        
                        nositelji = predmet_data.get("nositelji", {})
                        nositelji_list = []
                        if isinstance(nositelji, dict):
                            for nositelj_id, nositelj_data in nositelji.items():
                                nositelji_list.append({
                                    "userID": nositelj_data.get("userID"),
                                    "firstName": nositelj_data.get("firstName"),
                                    "lastName": nositelj_data.get("lastName")
                                })
                        
                        result[predmet_id] = {
                            "ISVU": isvu,
                            "naziv": predmet_data.get("naziv"),
                            "nositelji": nositelji_list
                        }
                else:
                    extract_predmeti(value)
        elif isinstance(data, list):
            for item in data:
                extract_predmeti(item)

    extract_predmeti(jsonData)

    unique_isvu = set()
    naziv_list = []

    for predmet_id, predmet_data in result.items():
        if predmet_data["ISVU"] not in unique_isvu:
            for nositelj in predmet_data["nositelji"]:
                if nositelj["lastName"] == lastName:
                    unique_isvu.add(predmet_data["ISVU"])
                    naziv_list.append(predmet_data["naziv"])
                    break

    print("Rezultati upita ",naziv_list)

@measureTime("Sati nastave po ECTS (JSON)")
def execute_json3(jsonData):
    result = {}

    def extract_predmeti(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "predmeti":
                    for predmet_id, predmet_data in value.items():
                        isvu = predmet_data.get("ISVU")
                        ects = predmet_data.get("ECTS")
                        
                        try:
                            ects = float(ects)
                        except (TypeError, ValueError):
                            ects = None
                        
                        satnica = predmet_data.get("satnica", {})
                        if isinstance(satnica, dict):
                            sum_satnica = sum(int(satnica.get(key, 0)) for key in satnica)
                        else:
                            sum_satnica = 0
                        
                        result[predmet_id] = {
                            "ISVU": isvu,
                            "ECTS": ects,
                            "sum_satnica": sum_satnica,
                            "satnica_per_ECTS": sum_satnica / ects if ects else None
                        }
                else:
                    extract_predmeti(value)
        elif isinstance(data, list):
            for item in data:
                extract_predmeti(item)

    extract_predmeti(jsonData)

    unique_isvu = set()
    unique_predmeti = []

    for predmet_id, predmet_data in result.items():
        if predmet_data["ISVU"] not in unique_isvu:
            unique_isvu.add(predmet_data["ISVU"])
            unique_predmeti.append(predmet_data)

    sorted_predmeti = sorted(unique_predmeti, key=lambda x: (x["satnica_per_ECTS"] is not None, x["satnica_per_ECTS"]), reverse=True)

    print(sorted_predmeti)

@measureTime("Kolegiji jednog studija (JSON)")
def execute_json4(jsonData):
    result = []
    target_akronim = "PD-I"

    for studij_key, studij_value in jsonData.items():
        for studij_name, studij in studij_value.items():
            if studij['Info']['akronim'] == target_akronim:
                for sem_key, sem_value in studij.items():
                    if sem_key.isdigit():
                        for group_type in ["obvezni", "izborni"]:
                            group_data = sem_value.get(group_type, {})
                            if isinstance(group_data, dict):
                                for group_key, group_value in group_data.items():
                                    groupID = group_value.get("groupID")
                                    for predmet_key, predmet_value in group_value.get("predmeti", {}).items():
                                        kolegij = {
                                            "semester": sem_value['semester'],
                                            "naziv": predmet_value.get("naziv"),
                                            "ECTS": predmet_value.get("ECTS"),
                                            "obvezan": 1 if group_type == "obvezni" else 0
                                        }
                                        result.append(kolegij)

    sorted_result = sorted(result, key=lambda x: (x["semester"], -x["obvezan"]))

    print(sorted_result)

@measureTime("Svi kolegiji po studiju i semestru (JSON)")
def execute_json5(jsonData):
    result = []

    for studij_key, studij_value in jsonData.items():
        for studij_name, studij in studij_value.items():
            for sem_key, sem_value in studij.items():
                if sem_key.isdigit():
                    for group_type in ["obvezni", "izborni"]:
                        group_data = sem_value.get(group_type, {})
                        if isinstance(group_data, dict):
                            for group_key, group_value in group_data.items():
                                groupID = group_value.get("groupID")
                                for predmet_key, predmet_value in group_value.get("predmeti", {}).items():
                                    kolegij = {
                                        "semester": sem_value['semester'],
                                        "naziv": predmet_value.get("naziv"),
                                        "ECTS": predmet_value.get("ECTS"),
                                        "obvezan": 1 if group_type == "obvezni" else 0,
                                        "studij": studij['Info']['studij']
                                    }
                                    result.append(kolegij)

    sorted_result = sorted(result, key=lambda x: (x["studij"], x["semester"], -x["obvezan"]))

    print(sorted_result)

execute_json1(jsonData)
execute_json2(jsonData)
execute_json3(jsonData)
execute_json4(jsonData)
execute_json5(jsonData)

def compare_execution_times(execution_times):
    sql_times = {k: v for k, v in execution_times.items() if not k.endswith("(JSON)")}
    json_times = {k: v for k, v in execution_times.items() if k.endswith("(JSON)")}

    print("\nUsporedba vremena izvršavanja SQL i JSON upita:")
    for sql_key, sql_time in sql_times.items():
        json_key = sql_key + " (JSON)"
        json_time = json_times.get(json_key, None)
        if json_time is not None:
            percentage_diff = ((json_time - sql_time) / sql_time) * 100
            if json_time < sql_time:
                print(f"{sql_key}: SQL = {sql_time:.6f}s, JSON = {json_time:.6f}s, JSON je {abs(percentage_diff):.2f}% brži od SQL-a")
            else:
                print(f"{sql_key}: SQL = {sql_time:.6f}s, JSON = {json_time:.6f}s, SQL je {abs(percentage_diff):.2f}% brži od JSON-a")

print("Vrijeme izvršavanja:", execution_times)

compare_execution_times(execution_times)
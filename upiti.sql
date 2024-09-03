-- Kolegiji po semestrima i studijima
Select k.naziv,k.ects,s.brojSemestra, sk.obvezan, st.naziv, st.modul, r.naziv from SemestarKolegij sk 
left join SemestarGodina sg on sk.semestarId=sg.id
left join KolegijGodina kg on kg.id=sk.kolegijId
left join Semestar s on s.id=sg.semestarId
left join Kolegij k on k.isvu=kg.kolegijId
left join Studij st on st.isvu=s.studijId
left join Razina r on r.id=st.razinaId
where sg.akademskaGodinaId=2023
order by r.naziv,st.naziv ,st.modul,s.brojSemestra, sk.obvezan desc

-- Popis kolegija za odabrani studij
Select k.naziv,k.ects,s.brojSemestra, sk.obvezan from SemestarKolegij sk 
left join SemestarGodina sg on sk.semestarId=sg.id
left join KolegijGodina kg on kg.id=sk.kolegijId
left join Semestar s on s.id=sg.semestarId
left join Kolegij k on k.isvu=kg.kolegijId
left join Studij st on st.isvu=s.studijId
where st.akronim='PD-I' and sg.akademskaGodinaId=2023 order by s.brojSemestra, sk.obvezan desc

-- Broj kolegija po profesoru
select d.ime,d.prezime, COUNT(d.id) as 'Broj kolegija' from Djelatnik d 
left join NositeljKolegij nk on nk.nositeljId=d.id
left join KolegijGodina kg on kg.id=nk.kolegijId
where kg.akademskaGodinaId=2023
group by d.id, d.ime, d.prezime
order by COUNT(d.id) desc

-- Kolegiji na kojima je djelatnik nositelj
select d.ime,d.prezime, k.naziv from Djelatnik d 
left join NositeljKolegij nk on nk.nositeljId=d.id
left join KolegijGodina kg on kg.id=nk.kolegijId
left join Kolegij k on k.isvu=kg.kolegijId
where kg.akademskaGodinaId=2023 and d.prezime='Zaharija'

-- Broj sati po ECTS bodu
select k.naziv, k.ects, SUM(kn.brojSati) as 'Broj sati', SUM(kn.brojSati)/k.ects as 'Broj sati po ECTS' from KolegijGodina kg
left join Kolegij k on k.isvu=kg.kolegijId
left join KolegijNastava kn on kn.kolegijId=kg.id
where kg.akademskaGodinaId=2023 and k.ects=5
group by k.naziv, k.ects
order by [Broj sati po ECTS] desc
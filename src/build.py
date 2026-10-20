# -*- coding: utf-8 -*-
"""Genera el horario (datos JSON -> HTML) y los .ics para Google Calendar."""
import json, datetime as dt, pathlib, hashlib

ROOT = pathlib.Path(__file__).parent


def E(s, e, c, t, sub=None, n=None, cond=None):
    d = {"s": s, "e": e, "c": c, "t": t}
    if sub: d["sub"] = sub
    if n: d["n"] = n
    if cond: d["cond"] = cond
    return d


RECARGA = "Recarga 20'"


def manana(wake="06:50", leave="07:20", arr="08:00", rutina="Ventilar, cama, desayuno", cond=None):
    return [E("06:30", wake, "sleep", "Sueño", cond=cond),
            E(wake, leave, "routine", rutina, cond=cond),
            E(leave, arr, "travel", "Moto → uni", cond=cond)]


def noche(bed="22:30", sleep="22:50"):
    return [E(bed, sleep, "bed", "Cama sin móvil"), E(sleep, "25:30", "sleep", "Sueño")]


def bonaigua_y_casa():
    return [E("13:00", "13:15", "travel", "→ Bonaigua"),
            E("13:15", "13:45", "spirit", "Misa · Bonaigua"),
            E("13:45", "14:25", "travel", "Moto → casa"),
            E("14:30", "15:15", "meal", "Comida · portátil cerrado"),
            E("15:15", "15:40", "recharge", RECARGA)]


FUT = {
    "21": [E("19:05", "19:40", "ocio", "Libre · vídeos aquí"),
           E("19:40", "20:10", "meal", "Cena ligera"),
           E("20:25", "22:30", "sport", "⚽ Fútbol 21h", n="Incluye el coche de ida y vuelta (25–30')."),
           E("22:30", "22:50", "bed", "Cama sin móvil"),
           E("22:50", "25:30", "sleep", "Sueño")],
    "22": [E("19:05", "20:15", "ocio", "Libre · vídeos aquí"),
           E("20:15", "20:45", "meal", "Cena"),
           E("21:25", "23:45", "sport", "⚽ Fútbol 22h", n="Incluye el coche de ida y vuelta (25–30')."),
           E("24:00", "25:30", "sleep", "Sueño", n="Unas 6 h 50 de sueño.")],
    "23": [E("19:05", "19:45", "ocio", "Libre"),
           E("19:45", "20:15", "meal", "Cena"),
           E("20:20", "21:45", "buffer", "Noche · repaso ligero (opcional)",
             n="Te gusta estudiar de noche: si vas fresco, aprovecha este rato."),
           E("22:25", "24:45", "sport", "⚽ Fútbol 23h", n="Llegas a casa a las 00:45."),
           E("25:00", "25:30", "sleep", "Sueño", n="Unas 5 h 50 de sueño. El martes va en modo mínimo.")],
}

# ---------------------------------------------------------------- SEMANA TIPO
tipo = [
    {"k": "lun", "fut": True, "ev": manana() + [
        E("08:00", "10:00", "class", "Electro · H 0.2", "electro"),
        E("10:15", "11:45", "study", "Biblio · Electro", "electro", "En caliente: lo de la clase de hoy y ejercicios."),
        E("12:00", "13:00", "study", "Biblio · MMCS", "mmcs", "Bloque corto: un solo tipo de ejercicio."),
    ] + bonaigua_y_casa() + [
        E("15:45", "17:15", "study", "Casa · OyG", "oyg", "Mañana tienes clase: llega con los ejercicios hechos."),
        E("17:35", "19:05", "study", "Casa · RM", "rm"),
    ]},
    {"k": "mar", "ev": manana() + [
        E("08:00", "10:00", "class", "RM · H 9.1", "rm"),
        E("10:00", "12:00", "class", "OyG · H 9.1", "oyg"),
        E("12:15", "13:45", "study", "Biblio · OptiSim", "optisim"),
        E("13:45", "14:30", "meal", "Táper en la uni"),
        E("14:45", "15:00", "travel", "→ RaceIn"),
        E("15:00", "20:00", "racein", "RaceIn · BCN"),
        E("20:00", "20:15", "travel", "→ Monterols"),
        E("20:15", "21:00", "spirit", "Monterols · formación"),
        E("21:00", "21:40", "travel", "Moto → casa"),
        E("21:45", "22:15", "meal", "Cena · portátil cerrado"),
    ] + noche()},
    {"k": "mie", "ev": manana() + [
        E("08:00", "10:00", "class", "Electro · H 0.2", "electro"),
        E("10:00", "12:00", "lab", "Lab Electro", "electro", cond="labE"),
        E("10:15", "11:45", "study", "Biblio · Electro", "electro", "Semana sin lab: este hueco es Electro.", cond="noLabE"),
        E("12:05", "13:00", "study", "Biblio · OptiSim", "optisim", "Bloque corto."),
    ] + bonaigua_y_casa() + [
        E("15:45", "17:15", "study", "Casa · MMCS", "mmcs"),
        E("17:25", "19:25", "sport", "Gym", n="Ir, entrenar 1h30–1h45 y ducharte allí."),
        E("19:30", "20:00", "ocio", "Libre · vídeos aquí"),
        E("20:00", "20:30", "meal", "Cena · portátil cerrado"),
        E("20:45", "22:00", "study", "Noche · TSM", "tsm", "Estudio nocturno, que te gusta. A las 22:00 se cierra."),
    ] + noche()},
    {"k": "jue", "ev": manana() + [
        E("08:00", "10:00", "class", "RM · H 9.1", "rm"),
        E("10:00", "12:00", "class", "OyG · H 9.2", "oyg"),
        E("12:15", "13:45", "study", "Biblio · Electro", "electro"),
        E("13:45", "14:30", "meal", "Táper en la uni"),
        E("14:30", "16:00", "study", "Biblio · MMCS", "mmcs"),
        E("16:20", "17:50", "study", "Biblio · RM", "rm"),
        E("18:00", "18:35", "buffer", "Margen · repaso flojo", n="Flashcards, hoja de errores o rezar 5'."),
        E("18:35", "19:00", "travel", "→ A"),
        E("19:00", "22:00", "a", "A ❤️", n="La dejas en el pádel a las 22."),
        E("22:00", "22:45", "travel", "Moto → casa"),
    ] + noche("22:45", "23:05")},
    {"k": "vie", "ev":
        manana(cond="optF") + [
            E("08:00", "10:00", "class", "OptiSim · H 5.1", "optisim", cond="optF"),
            # OptiSim sin lab de RM: a Premià como siempre
            E("10:00", "10:40", "travel", "→ Premià (o Bonaigua 5')", cond="optF+noLabR"),
            E("10:45", "11:50", "study", "Premià · OptiSim", "optisim", "Repasa lo del lab en casa de tu amigo antes de empezar.", cond="optF+noLabR"),
            # OptiSim + lab de RM: no te mueves de BCN
            E("10:00", "10:30", "free", "Bonaigua o repaso", cond="optF+labR"),
            E("10:30", "15:30", "racein", "RaceIn · online",
              n="Con los dos labs no te mueves de BCN: RaceIn online desde la biblio. Comes durante, como en Premià: táper o compra.", cond="optF+labR"),
            E("15:30", "15:50", "travel", "→ Lab RM", cond="optF+labR"),
        ] + [
            E("06:30", "07:30", "sleep", "Sueño", cond="noOptF"),
            E("07:30", "07:55", "routine", "Desayuno", cond="noOptF"),
            E("08:00", "09:45", "sport", "Gym", n="Sin OptiSim: gym mañanero.", cond="noOptF"),
            E("10:00", "11:30", "study", "Casa · OptiSim", "optisim", cond="noOptF+noLabR"),
            E("11:40", "11:55", "travel", "→ Premià", cond="noOptF+noLabR"),
            # sin OptiSim + lab de RM: RaceIn antes y bajas a BCN
            E("09:45", "10:00", "travel", "→ Premià", cond="noOptF+labR"),
            E("10:00", "15:00", "racein", "RaceIn · Premià",
              n="Empiezas antes y acabas antes para bajar al lab de RM. Comes allí.", cond="noOptF+labR"),
            E("15:00", "15:40", "travel", "Moto → uni", cond="noOptF+labR"),
        ] + [
            E("12:00", "17:00", "racein", "RaceIn · Premià", n="Comes en casa de tu amigo.", cond="noLabR"),
            E("17:00", "19:00", "free", "Tu hueco · viaje o estudio", cond="noLabR"),
            E("16:00", "18:00", "lab", "Lab RM", "rm", cond="labR"),
            E("18:00", "19:00", "free", "Tu hueco · viaje o estudio", cond="labR"),
            E("19:00", "24:00", "a", "A ❤️"),
            E("24:00", "25:00", "travel", "→ casa (1–2h)"),
        ]},
    {"k": "sab", "ev": [
        E("06:30", "08:30", "sleep", "Sueño", n="Duermes de 1:00 a 8:30."),
        E("08:30", "08:45", "routine", "Desayuno rápido"),
        E("08:45", "09:00", "travel", "→ Premià"),
        E("09:00", "14:00", "racein", "RaceIn · Premià"),
        E("14:00", "14:15", "travel", "→ casa"),
        E("14:30", "15:15", "meal", "Comida"),
        E("15:15", "15:40", "recharge", RECARGA, n="Hoy sí te la has ganado: dormiste poco."),
        E("16:00", "17:45", "sport", "Gym", n="El viernes hubo OptiSim: el gym pasa aquí.", cond="optF"),
        E("18:00", "19:30", "buffer", "Colchón semanal", cond="optF+noLabR"),
        E("18:00", "19:30", "study", "Casa · OptiSim", "optisim", "Semana con lab de RM: el viernes OptiSim se quedó sin bloque y va aquí.", cond="optF+labR"),
        E("19:30", "24:30", "ocio", "Libre", cond="optF"),
        E("16:00", "17:30", "buffer", "Colchón semanal", cond="noOptF+noLabR"),
        E("16:00", "17:30", "study", "Casa · OptiSim", "optisim", "Semana con lab de RM: el viernes OptiSim se quedó sin bloque y va aquí.", cond="noOptF+labR"),
        E("17:30", "24:30", "ocio", "Libre", cond="noOptF"),
        E("24:30", "25:30", "sleep", "Sueño"),
    ]},
    {"k": "dom", "ev": [
        E("06:30", "09:00", "sleep", "Sueño"),
        E("09:00", "09:45", "routine", "Arreglarte · desayunas después"),
        E("10:00", "10:45", "spirit", "Misa"),
        E("10:50", "11:20", "meal", "Desayuno"),
        E("11:40", "13:20", "sport", "Gym"),
        E("14:00", "15:00", "meal", "Comida en familia"),
        E("15:00", "17:00", "ocio", "Descanso de verdad"),
        E("17:00", "17:45", "cook", "Tápers de la semana", n="2 raciones: martes y jueves."),
        E("18:00", "18:30", "review", "Revisión semanal"),
        E("18:30", "20:00", "buffer", "Comodín · la que peor vaya", n="La asignatura que más se haya quedado atrás o un bloque caído."),
        E("20:30", "21:00", "meal", "Cena"),
    ] + noche()},
]

# ---------------------------------------------------------------- ESTA SEMANA (20–25 oct)
esta = [
    {"k": "mar", "date": "2026-10-20", "ev": manana() + [
        E("08:00", "10:00", "class", "RM · H 9.1", "rm"),
        E("10:00", "12:00", "class", "OyG · H 9.1", "oyg"),
        E("12:15", "13:45", "study", "Biblio · OptiSim", "optisim", "Haz inventario: qué temas entran y qué no sabes hacer."),
        E("13:45", "14:30", "meal", "Comida en la uni", n="Hoy no hay táper: compra algo. El primer batch es el domingo."),
        E("14:30", "16:00", "study", "Biblio · RM", "rm", "Inventario de temas + problemas tipo."),
        E("16:20", "17:50", "study", "Biblio · MMCS", "mmcs", "Inventario de temas + ejercicios."),
        E("18:05", "19:35", "study", "Biblio · Electro", "electro", "Si vas frito, versión mínima de 20'."),
        E("19:50", "20:15", "travel", "→ Monterols"),
        E("20:15", "21:00", "spirit", "Monterols · formación"),
        E("21:00", "21:40", "travel", "Moto → casa"),
        E("21:45", "22:15", "meal", "Cena · portátil cerrado"),
    ] + noche()},
    {"k": "mie", "date": "2026-10-21", "ev": manana() + [
        E("08:00", "10:00", "class", "Electro · H 0.2", "electro"),
        E("10:00", "12:00", "lab", "Lab Electro", "electro", cond="labE"),
        E("10:15", "11:45", "study", "Biblio · Electro", "electro", "Semana sin lab: este hueco es Electro.", cond="noLabE"),
        E("12:05", "13:00", "study", "Biblio · OptiSim", "optisim", "Bloque corto."),
    ] + bonaigua_y_casa() + [
        E("15:45", "17:15", "study", "Casa · RM", "rm"),
        E("17:25", "19:25", "sport", "Gym", n="Ir, entrenar 1h30–1h45 y ducharte allí."),
        E("19:30", "20:00", "ocio", "Libre · vídeos aquí"),
        E("20:00", "20:30", "meal", "Cena · portátil cerrado"),
        E("20:45", "22:00", "study", "Noche · MMCS", "mmcs", "A las 22:00 se cierra."),
    ] + noche()},
    {"k": "jue", "date": "2026-10-22", "ev": manana() + [
        E("08:00", "10:00", "class", "RM · H 9.1", "rm"),
        E("10:00", "12:00", "class", "OyG · H 9.2", "oyg"),
        E("12:15", "13:45", "study", "Biblio · MMCS", "mmcs"),
        E("13:45", "14:30", "meal", "Comida en la uni", n="Compra o llévate algo de casa."),
        E("14:30", "16:00", "study", "Biblio · OptiSim", "optisim"),
        E("16:20", "17:50", "study", "Biblio · Electro", "electro"),
        E("18:00", "18:35", "buffer", "Margen · fórmulas de RM"),
        E("18:35", "19:00", "travel", "→ A"),
        E("19:00", "22:00", "a", "A ❤️", n="La dejas en el pádel a las 22."),
        E("22:00", "22:45", "travel", "Moto → casa"),
    ] + noche("22:45", "23:05")},
    {"k": "vie", "date": "2026-10-23", "ev":
        manana(cond="optF") + [
            E("08:00", "10:00", "class", "OptiSim · H 5.1", "optisim", cond="optF"),
            E("10:15", "11:45", "study", "Biblio · OptiSim", "optisim", "Justo después del lab, en caliente.", cond="optF"),
            E("12:00", "13:15", "study", "Biblio · Electro", "electro", cond="optF+noLabR"),
            E("13:20", "14:00", "travel", "Moto → casa", cond="optF+noLabR"),
            E("14:15", "15:00", "meal", "Comida · portátil cerrado", cond="optF+noLabR"),
            E("15:00", "15:25", "recharge", RECARGA, cond="optF+noLabR"),
            E("15:30", "17:00", "study", "Casa · RM", "rm", cond="optF+noLabR"),
            E("17:00", "19:00", "free", "Tu hueco · viaje o estudio", cond="optF+noLabR"),
            # OptiSim + lab de RM: te quedas en BCN
            E("12:00", "13:30", "study", "Biblio · Electro", "electro", cond="optF+labR"),
            E("13:30", "14:15", "meal", "Comida en la uni (compra)", cond="optF+labR"),
            E("14:15", "15:45", "study", "Biblio · RM", "rm", "Prepara el lab y haz problemas tipo examen.", cond="optF+labR"),
            E("15:45", "16:00", "travel", "→ Lab RM", cond="optF+labR"),
        ] + [
            E("06:30", "07:30", "sleep", "Sueño", cond="noOptF"),
            E("07:30", "07:55", "routine", "Desayuno", cond="noOptF"),
            E("08:00", "09:45", "sport", "Gym", n="Sin OptiSim: gym mañanero.", cond="noOptF"),
            E("10:00", "11:30", "study", "Casa · OptiSim", "optisim", cond="noOptF"),
            E("11:50", "13:20", "study", "Casa · Electro", "electro", cond="noOptF"),
            E("13:30", "14:15", "meal", "Comida · portátil cerrado", cond="noOptF"),
            E("14:15", "14:40", "recharge", RECARGA, cond="noOptF+noLabR"),
            E("14:45", "16:15", "study", "Casa · RM", "rm", cond="noOptF+noLabR"),
            E("16:35", "17:35", "study", "Casa · MMCS", "mmcs", "Bloque corto.", cond="noOptF+noLabR"),
            E("17:35", "19:00", "free", "Tu hueco · viaje o estudio", cond="noOptF+noLabR"),
            # sin OptiSim + lab de RM: bajas a BCN después de comer
            E("14:20", "15:00", "travel", "Moto → uni", cond="noOptF+labR"),
            E("15:05", "15:50", "study", "Biblio · RM", "rm", "Repaso rápido antes del lab.", cond="noOptF+labR"),
        ] + [
            E("16:00", "18:00", "lab", "Lab RM", "rm", cond="labR"),
            E("18:00", "19:00", "free", "Tu hueco · viaje o estudio", cond="labR"),
        ] + [
            E("19:00", "24:00", "a", "A ❤️"),
            E("24:00", "25:00", "travel", "→ casa (1–2h)"),
        ]},
    {"k": "sab", "date": "2026-10-24", "ev": [
        E("06:30", "08:30", "sleep", "Sueño", n="Duermes de 1:00 a 8:30."),
        E("08:30", "09:00", "routine", "Desayuno"),
        E("09:15", "10:45", "study", "Casa · Electro", "electro", "Problemas tipo examen. Electro es tu prioridad número uno."),
        E("11:05", "12:35", "study", "Casa · RM", "rm"),
        E("12:35", "14:00", "ocio", "Libre"),
        E("14:00", "14:45", "meal", "Comida"),
        E("14:45", "15:10", "recharge", RECARGA),
        E("15:30", "17:00", "study", "Casa · MMCS", "mmcs"),
        E("17:20", "18:20", "study", "Casa · TSM", "tsm", "Toque semanal para que no se enfríe."),
        E("18:30", "20:15", "sport", "Gym", n="El viernes hubo OptiSim: el gym pasa aquí.", cond="optF"),
        E("20:15", "24:00", "ocio", "Libre", cond="optF"),
        E("18:20", "24:00", "ocio", "Libre", cond="noOptF"),
        E("24:00", "25:30", "sleep", "Sueño", n="Esta noche cambia la hora: duermes una hora más."),
    ]},
    {"k": "dom", "date": "2026-10-25", "ev": [
        E("06:30", "09:00", "sleep", "Sueño"),
        E("09:00", "09:45", "routine", "Arreglarte · desayunas después"),
        E("10:00", "10:45", "spirit", "Misa"),
        E("10:50", "11:20", "meal", "Desayuno"),
        E("11:40", "13:20", "sport", "Gym"),
        E("14:00", "15:00", "meal", "Comida en familia"),
        E("15:00", "16:00", "ocio", "Descanso"),
        E("16:00", "17:30", "study", "Casa · OptiSim", "optisim", "Simulacro de 1h15 cronometrado, como el examen, y repaso de la hoja de errores."),
        E("17:45", "18:30", "cook", "Tápers: 3 raciones", n="Para el martes, miércoles y jueves de parciales."),
        E("18:30", "19:00", "review", "Revisión: plan de parciales"),
        E("19:00", "20:15", "study", "Casa · RM", "rm", "Problemas tipo examen."),
        E("20:30", "21:00", "meal", "Cena"),
    ] + noche()},
]

# ---------------------------------------------------------------- PARCIALES (26 oct – 2 nov)
def manana_examen(wake="07:15", leave="07:45", arr="08:25"):
    return [E("06:30", wake, "sleep", "Sueño"),
            E(wake, leave, "routine", "Rutina y desayuno"),
            E(leave, arr, "travel", "Moto → uni")]


parciales = [
    {"k": "lun", "date": "2026-10-26", "fut": True, "ev": manana() + [
        E("08:00", "10:00", "class", "Electro · H 0.2 (si hay)", "electro"),
        E("10:15", "11:45", "study", "Biblio · OptiSim", "optisim", "Hoja de errores y los ejercicios que fallaste."),
        E("12:00", "13:00", "study", "Biblio · OptiSim", "optisim", "Los tipos de ejercicio que más caen."),
    ] + bonaigua_y_casa() + [
        E("15:45", "17:00", "study", "Casa · OptiSim", "optisim", "Segundo simulacro de 1h15."),
        E("17:20", "18:50", "study", "Casa · RM", "rm"),
    ]},
    {"k": "mar", "date": "2026-10-27", "ev": manana_examen() + [
        E("08:30", "10:00", "study", "Biblio · OptiSim", "optisim", "Repaso suave. Nada nuevo."),
        E("10:20", "11:30", "study", "Biblio · OptiSim", "optisim", "Formulario y 2 ejercicios fáciles para entrar en ritmo."),
        E("11:30", "12:00", "meal", "Algo de comer y desconectar"),
        E("12:30", "13:45", "exam", "Examen OptiSim", "optisim"),
        E("13:45", "14:30", "meal", "Táper"),
        E("14:30", "15:00", "recharge", "Paseo · no repases el examen"),
        E("15:00", "16:30", "study", "Biblio · RM", "rm", "Problemas tipo examen."),
        E("16:50", "18:20", "study", "Biblio · RM", "rm"),
        E("18:35", "19:35", "study", "Biblio · RM", "rm", "Formulario y hoja de errores."),
        E("19:50", "20:15", "travel", "→ Monterols"),
        E("20:15", "21:00", "spirit", "Monterols · formación"),
        E("21:00", "21:40", "travel", "Moto → casa"),
        E("21:45", "22:15", "meal", "Cena · portátil cerrado"),
    ] + noche()},
    {"k": "mie", "date": "2026-10-28", "ev": manana_examen() + [
        E("08:30", "10:00", "study", "Biblio · RM", "rm"),
        E("10:20", "11:50", "study", "Biblio · RM", "rm"),
        E("12:00", "13:00", "study", "Biblio · RM", "rm", "Repaso suave."),
        E("13:00", "13:15", "travel", "→ Bonaigua"),
        E("13:15", "13:45", "spirit", "Misa · Bonaigua"),
        E("13:45", "14:00", "travel", "→ uni"),
        E("14:00", "14:40", "meal", "Táper"),
        E("14:40", "15:10", "recharge", "Paseo · sin siesta"),
        E("15:10", "16:20", "study", "Biblio · RM", "rm", "Último repaso: formulario y hoja de errores."),
        E("16:40", "17:00", "travel", "Al aula"),
        E("17:00", "18:15", "exam", "Examen RM", "rm"),
        E("18:15", "18:55", "travel", "Moto → casa"),
        E("19:05", "20:35", "sport", "Gym corto", n="Para descargar después del examen: 1h15 y ducha."),
        E("20:45", "21:15", "meal", "Cena · portátil cerrado"),
        E("21:30", "22:15", "study", "Noche · MMCS", "mmcs", "Repaso ligero de 45'. Mañana examen."),
    ] + noche()},
    {"k": "jue", "date": "2026-10-29", "ev": manana_examen() + [
        E("08:30", "10:00", "study", "Biblio · MMCS", "mmcs", "Repaso suave. Nada nuevo."),
        E("10:20", "11:30", "study", "Biblio · MMCS", "mmcs", "Formulario y ejercicios fáciles."),
        E("11:30", "12:00", "meal", "Algo de comer y desconectar"),
        E("12:30", "13:45", "exam", "Examen MMCS", "mmcs"),
        E("13:45", "14:30", "meal", "Táper"),
        E("14:30", "15:00", "recharge", "Paseo"),
        E("15:00", "16:30", "study", "Biblio · Electro", "electro"),
        E("16:50", "18:20", "study", "Biblio · Electro", "electro", "Simulacro de 1h15."),
        E("18:35", "19:00", "travel", "→ A"),
        E("19:00", "22:00", "a", "A ❤️", n="Si quedáis. Mañana examen a las 9:30."),
        E("22:00", "22:45", "travel", "Moto → casa"),
    ] + noche("22:45", "23:05")},
    {"k": "vie", "date": "2026-10-30", "ev": [
        E("06:30", "07:00", "sleep", "Sueño"),
        E("07:00", "07:40", "routine", "Rutina y desayuno"),
        E("07:40", "08:20", "travel", "Moto → uni"),
        E("08:30", "09:15", "study", "Biblio · Electro", "electro", "Formulario y hoja de errores. Nada nuevo."),
        E("09:30", "10:45", "exam", "Examen Electro", "electro"),
        E("10:45", "11:15", "recharge", "Pausa · desconecta"),
        E("11:15", "12:45", "study", "Biblio · TSM", "tsm"),
        E("13:00", "13:45", "meal", "Comida (compra)"),
        E("14:00", "15:30", "study", "Biblio · OyG", "oyg"),
        E("15:50", "17:20", "study", "Biblio · TSM", "tsm"),
        E("17:40", "19:10", "study", "Biblio · OyG", "oyg"),
        E("19:15", "20:00", "meal", "Cena (compra)"),
        E("20:00", "21:30", "study", "Biblio · TSM", "tsm", "Simulacro de 1h15."),
        E("21:50", "23:30", "buffer", "Repaso ligero · hojas de errores",
          n="Desde las 22:00 solo repaso. Si no rindes, vete antes: dormir también es estudiar."),
        E("23:45", "24:25", "travel", "Moto → casa"),
        E("24:30", "25:30", "sleep", "Sueño"),
    ]},
    {"k": "sab", "date": "2026-10-31", "ev": [
        E("06:30", "08:30", "sleep", "Sueño"),
        E("08:30", "09:00", "routine", "Desayuno"),
        E("09:00", "09:40", "travel", "Moto → biblio BCN"),
        E("09:45", "11:15", "study", "Biblio · OyG", "oyg"),
        E("11:35", "13:05", "study", "Biblio · TSM", "tsm"),
        E("13:15", "14:00", "meal", "Comida (compra)"),
        E("14:15", "15:45", "study", "Biblio · OyG", "oyg", "Simulacro de 1h15."),
        E("16:05", "17:35", "study", "Biblio · TSM", "tsm"),
        E("17:55", "19:25", "study", "Biblio · OyG", "oyg"),
        E("19:30", "20:15", "meal", "Cena (compra)"),
        E("20:30", "22:00", "study", "Biblio · TSM", "tsm", "Simulacro de 1h15."),
        E("22:15", "23:30", "buffer", "Repaso ligero · hojas de errores", n="Si a media tarde vas KO, corta antes: el domingo también estudias."),
        E("23:45", "24:25", "travel", "Moto → casa"),
        E("24:30", "25:30", "sleep", "Sueño"),
    ]},
    {"k": "dom", "date": "2026-11-01", "ev": [
        E("06:30", "09:30", "sleep", "Sueño"),
        E("09:30", "10:40", "routine", "Arreglarte · desayunas después"),
        E("11:00", "11:45", "spirit", "Misa · Todos los Santos"),
        E("11:50", "12:20", "meal", "Desayuno"),
        E("12:40", "13:55", "sport", "Gym corto", n="1h15."),
        E("14:15", "15:15", "meal", "Comida en familia"),
        E("15:15", "16:15", "ocio", "Descanso"),
        E("16:15", "17:45", "study", "Casa · TSM", "tsm", "Lo que más cae y la hoja de errores."),
        E("18:05", "19:35", "study", "Casa · OyG", "oyg"),
        E("19:40", "20:00", "review", "Revisión · vuelve la semana tipo"),
        E("20:00", "20:30", "meal", "Cena"),
        E("20:45", "21:30", "study", "Noche · TSM", "tsm", "Repaso ligero del formulario."),
    ] + noche("22:15", "22:35")},
    {"k": "lun", "date": "2026-11-02", "ev": manana_examen() + [
        E("08:30", "09:15", "study", "Biblio · TSM", "tsm", "Repaso suave. Nada nuevo."),
        E("09:30", "10:45", "exam", "Examen TSM", "tsm"),
        E("10:45", "11:15", "recharge", "Pausa · desconecta"),
        E("11:15", "12:45", "study", "Biblio · OyG", "oyg"),
        E("13:00", "13:15", "travel", "→ Bonaigua"),
        E("13:15", "13:45", "spirit", "Misa · Bonaigua"),
        E("13:45", "14:00", "travel", "→ uni"),
        E("14:00", "14:40", "meal", "Comida (compra)"),
        E("14:40", "15:10", "recharge", "Paseo"),
        E("15:10", "16:40", "study", "Biblio · OyG", "oyg"),
        E("17:00", "18:00", "study", "Biblio · OyG", "oyg", "Repaso suave: formulario y errores."),
        E("18:15", "18:30", "travel", "Al aula"),
        E("18:30", "19:45", "exam", "Examen OyG", "oyg", "El último. Fin de parciales."),
        E("19:45", "20:25", "travel", "Moto → casa"),
        E("20:30", "21:00", "meal", "Cena"),
        E("21:00", "22:30", "ocio", "Libre · te lo has ganado", n="Fútbol: si es a las 21h no llegas. Si es más tarde, decides tú."),
    ] + noche()},
]

DAYNAMES = {"lun": ("Lunes", "Lun"), "mar": ("Martes", "Mar"), "mie": ("Miércoles", "Mié"),
            "jue": ("Jueves", "Jue"), "vie": ("Viernes", "Vie"), "sab": ("Sábado", "Sáb"), "dom": ("Domingo", "Dom")}

for lst in (tipo, esta, parciales):
    for d in lst:
        d["name"], d["short"] = DAYNAMES[d["k"]]

SUBJ = {"electro": "Electro", "mmcs": "MMCS", "optisim": "OptiSim", "rm": "RM", "tsm": "TSM", "oyg": "OyG"}

CATS = {
    "study": {"l": "Estudio", "min": "Plan B (45'): un solo tipo de ejercicio. Plan C (20'): rehaz un ejercicio de tu hoja de errores. Nunca cero."},
    "exam": {"l": "Examen", "min": "Llega 15' antes. La víspera y la mañana, nada nuevo: formulario y hoja de errores."},
    "class": {"l": "Clase", "min": ""},
    "lab": {"l": "Lab", "min": ""},
    "racein": {"l": "RaceIn", "min": "Fijo. Si hay urgencia, se puede hacer online."},
    "a": {"l": "A ❤️", "min": "Tu tiempo. No se toca."},
    "sport": {"l": "Deporte", "min": "Plan B: 45' de gym solo con lo básico. Plan C: 20' en casa (flexiones, sentadillas, plancha) o 30' andando."},
    "spirit": {"l": "Misa y formación", "min": "Plan B: entrar 5' de camino. Plan C: rezar en la cama a las 22:30."},
    "meal": {"l": "Comida", "min": "Portátil cerrado. El móvil vale, que no tiene YouTube."},
    "routine": {"l": "Rutina", "min": ""},
    "travel": {"l": "Viaje", "min": "En moto no se estudia: cuenta como descanso."},
    "sleep": {"l": "Sueño", "min": "No se toca. Si una noche es corta, al día siguiente solo bloques de biblio y nada de estudio nocturno."},
    "recharge": {"l": "Recarga", "min": "Siesta exprés con alarma en el sofá y el móvil fuera de la habitación, o un paseo. Nunca después de las 15:45. Cero vídeos."},
    "buffer": {"l": "Colchón", "min": "Aquí recuperas lo que se cayó. Si no se cayó nada, adelanta la asignatura que peor lleves."},
    "review": {"l": "Revisión", "min": "25 minutos con la lista de la revisión del domingo. Una sola cosa que cambiar."},
    "cook": {"l": "Tápers", "min": "Una receta, varias raciones. El plan de tápers está más abajo."},
    "free": {"l": "Tu hueco", "min": "Lo decides tú: viaje o estudio."},
    "ocio": {"l": "Libre", "min": "Libre de verdad. Los vídeos van aquí, no antes."},
    "bed": {"l": "Cama sin móvil", "min": "Móvil a cargar fuera de la habitación. Libro, rezar o guitarra. Dormido a las 22:50."},
}

DATA = {
    "subjects": SUBJ,
    "cats": CATS,
    "fut": FUT,
    "views": {
        "esta": {"label": "Esta semana", "range": "20–25 oct", "days": esta, "lab": True, "opt": True, "futCtl": False},
        "parciales": {"label": "Parciales", "range": "26 oct – 2 nov", "days": parciales, "lab": False, "opt": False, "futCtl": True},
        "tipo": {"label": "Semana tipo", "range": "desde el 3 nov", "days": tipo, "lab": True, "opt": True, "futCtl": True},
    },
}


# ---------------------------------------------------------------- comprobaciones
def tmin(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m


def okmap(labE, optF, labR):
    return {"labE": labE, "noLabE": not labE, "optF": optF, "noOptF": not optF, "labR": labR, "noLabR": not labR}


def cond_ok(e, ok):
    c = e.get("cond")
    return (not c) or all(ok[p] for p in c.split("+"))


def check(view, days):
    variants = [okmap(a, b, c) for a in (True, False) for b in (True, False) for c in (True, False)]
    for d in days:
        for ok in variants:
            v = ok
            futs = FUT.keys() if d.get("fut") else [None]
            for f in futs:
                evs = [e for e in d["ev"] if cond_ok(e, ok)]
                if f: evs = evs + FUT[f]
                evs = sorted(evs, key=lambda e: tmin(e["s"]))
                for a, b in zip(evs, evs[1:]):
                    assert tmin(a["e"]) <= tmin(b["s"]), (view, d["k"], d.get("date"), v, f, a["t"], b["t"])
                for e in evs:
                    assert tmin(e["s"]) < tmin(e["e"]), (view, d["k"], e)
                    assert 390 <= tmin(e["s"]) and tmin(e["e"]) <= 1530, (view, d["k"], e)


for name, v in DATA["views"].items():
    check(name, v["days"])


def study_minutes(days, labE, optF, labR=False, fut="21"):
    ok = okmap(labE, optF, labR)
    tot, buf = {}, 0
    for d in days:
        evs = [e for e in d["ev"] if cond_ok(e, ok)]
        if d.get("fut"): evs += FUT[fut]
        for e in evs:
            m = tmin(e["e"]) - tmin(e["s"])
            if e["c"] == "study": tot[e["sub"]] = tot.get(e["sub"], 0) + m
            if e["c"] == "buffer": buf += m
    return tot, buf


for name in ("tipo", "esta", "parciales"):
    for labE in (False, True):
        for optF in (False, True):
          for labR in (False, True):
            t, b = study_minutes(DATA["views"][name]["days"], labE, optF, labR)
            print(name, "lab" if labE else "nolab", "opt" if optF else "noopt", "rm" if labR else "norm",
                  {k: round(v / 60, 2) for k, v in t.items()}, "total", round(sum(t.values()) / 60, 2), "colchón", round(b / 60, 2))

# ---------------------------------------------------------------- HTML
tpl = (ROOT / "template.html").read_text(encoding="utf-8")
payload = json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")
(ROOT / "horario.html").write_text(tpl.replace("__PLAN_DATA__", payload), encoding="utf-8")

# ---------------------------------------------------------------- ICS
EXPORT = {"study", "exam", "sport", "spirit", "recharge", "buffer", "review", "cook", "bed"}
CONDTXT = {"labE": "hay lab", "noLabE": "no hay lab", "optF": "hay OptiSim", "noOptF": "no hay OptiSim",
           "labR": "hay lab de RM", "noLabR": "no hay lab de RM"}


class _Suffix(dict):
    def get(self, c, default=""):
        return " (si " + " y ".join(CONDTXT[p] for p in c.split("+")) + ")" if c else default


SUFFIX = _Suffix()
VTZ = """BEGIN:VTIMEZONE
TZID:Europe/Madrid
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE"""


def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    out, cur, n = [], "", 0
    for ch in line:
        b = len(ch.encode("utf-8"))
        if n + b > 74:
            out.append(cur)
            cur, n = " " + ch, 1 + b
        else:
            cur += ch
            n += b
    out.append(cur)
    return "\r\n".join(out)


def stamp(date, t):
    h, m = map(int, t.split(":"))
    d = dt.date.fromisoformat(date) + dt.timedelta(days=h // 24)
    return f"{d:%Y%m%d}T{h % 24:02d}{m:02d}00"


def vevent(e, date, rrule=None):
    if e["c"] not in EXPORT or e["t"].startswith("Monterols"):
        return None
    title = e["t"] + SUFFIX.get(e.get("cond"), "")
    desc = []
    if e.get("n"): desc.append(e["n"])
    mn = CATS[e["c"]]["min"]
    if mn: desc.append(("Si no llegas: " if e["c"] in ("study", "sport", "spirit") else "") + mn)
    uid = hashlib.sha1(f"{date}{e['s']}{title}".encode()).hexdigest()[:20] + "@horario-pol"
    trig = {"bed": "-PT5M", "exam": "-PT60M"}.get(e["c"], "PT0M")
    L = ["BEGIN:VEVENT", f"UID:{uid}", "DTSTAMP:20261019T220000Z",
         f"DTSTART;TZID=Europe/Madrid:{stamp(date, e['s'])}",
         f"DTEND;TZID=Europe/Madrid:{stamp(date, e['e'])}",
         f"SUMMARY:{esc(title)}"]
    if rrule: L.append(rrule)
    if desc: L.append("DESCRIPTION:" + esc("\n".join(desc)))
    L += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(title)}", f"TRIGGER:{trig}", "END:VALARM", "END:VEVENT"]
    return "\r\n".join(fold(x) for x in L)


def calendar(name, events):
    head = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Horario Pol//ES", "CALSCALE:GREGORIAN",
            f"X-WR-CALNAME:{name}", "X-WR-TIMEZONE:Europe/Madrid"]
    body = "\r\n".join(head) + "\r\n" + VTZ.replace("\n", "\r\n") + "\r\n" + "\r\n".join(events) + "\r\nEND:VCALENDAR\r\n"
    return body


ev1 = []
for d in esta + parciales:
    for e in d["ev"]:
        v = vevent(e, d["date"])
        if v: ev1.append(v)
(ROOT / "plan-parciales.ics").write_text(calendar("Plan estudio · parciales", ev1), encoding="utf-8", newline="")

FIRST = {"mar": "2026-11-03", "mie": "2026-11-04", "jue": "2026-11-05", "vie": "2026-11-06",
         "sab": "2026-11-07", "dom": "2026-11-08", "lun": "2026-11-09"}
RR = "RRULE:FREQ=WEEKLY;UNTIL=20261220T225959Z"
ev2 = []
for d in tipo:
    for e in d["ev"]:
        v = vevent(e, FIRST[d["k"]], RR)
        if v: ev2.append(v)
(ROOT / "semana-tipo.ics").write_text(calendar("Plan estudio · semana tipo", ev2), encoding="utf-8", newline="")
print("eventos ics:", len(ev1), len(ev2))


# ---------------------------------------------------------------- WEB-APP (GitHub Pages)
from PIL import Image, ImageDraw

SITE = ROOT / "site"
SITE.mkdir(exist_ok=True)
SITE_URL = "https://negrillos.github.io/horario/"


def draw_icon(size, bg="#000000", fg="#F2F2F2", scale=4):
    """Icono de calendario minimalista: contorno, línea de cabecera y dos anillas."""
    S = 1024 * scale
    k = lambda v: int(round(v * scale))
    im = Image.new("RGB", (S, S), bg)
    d = ImageDraw.Draw(im)
    sw = k(40)
    x0, y0, x1, y1 = k(262), k(296), k(762), k(776)
    d.rounded_rectangle([x0, y0, x1, y1], radius=k(96), outline=fg, width=sw)
    d.rectangle([x0, k(428) - sw // 2, x1, k(428) + sw // 2], fill=fg)
    for cx in (k(412), k(612)):
        d.rounded_rectangle([cx - sw // 2, k(232), cx + sw // 2, k(360)], radius=sw // 2, fill=fg)
    return im.resize((size, size), Image.LANCZOS)


ICON_V = "5"  # súbelo cada vez que cambie el icono: el iPhone guarda los iconos por nombre de archivo
for old in SITE.glob("*.png"):
    old.unlink()
for name, size in ((f"apple-touch-icon-{ICON_V}.png", 180), (f"icon-192-{ICON_V}.png", 192), (f"icon-512-{ICON_V}.png", 512)):
    draw_icon(size).save(SITE / name)

COLORS = {  # [claro, oscuro], los mismos que la página
    "electro": ["#B48100", "#E2B13A"], "mmcs": ["#2866CC", "#5C95F2"], "optisim": ["#08847A", "#2DB7A9"],
    "rm": ["#5848CC", "#8E82F4"], "tsm": ["#468220", "#7EBA4E"], "oyg": ["#AE3487", "#DD6AB6"],
    "racein": ["#D95A20", "#F07F47"], "sport": ["#CB382B", "#F06457"], "a": ["#D64B76", "#F27C9F"],
    "spirit": ["#82725D", "#B5A68F"], "neutral": ["#7A8590", "#8E99A5"],
}
plan = dict(DATA)
plan["colors"] = COLORS
plan["site"] = SITE_URL
(SITE / "plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

head_part, body_part = tpl.split("</style>", 1)
head_part = head_part.replace("<title>Horario a prueba de fallos</title>", "<title>Horario</title>")
head_part = head_part.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
index = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Horario">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#F1F3F6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E1216" media="(prefers-color-scheme: dark)">
<link rel="apple-touch-icon" href="apple-touch-icon-{ICON_V}.png">
<link rel="icon" href="icon-192-{ICON_V}.png">
<link rel="manifest" href="manifest.webmanifest">
{head_part}
/* base de la web-app (lo que en Claude pone el propio visor) */
:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
html{{background:var(--bg);-webkit-text-size-adjust:100%}}
body{{margin:0;-webkit-tap-highlight-color:transparent}}
img{{max-width:100%}}
</style>
</head>
<body>
{body_part.replace("__PLAN_DATA__", payload)}
<script>
if ('serviceWorker' in navigator) {{ navigator.serviceWorker.register('sw.js').catch(function(){{}}); }}
</script>
</body>
</html>
"""
(SITE / "index.html").write_text(index, encoding="utf-8")

manifest = {
    "name": "Horario", "short_name": "Horario", "lang": "es",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#000000", "theme_color": "#0E1216",
    "icons": [{"src": f"icon-192-{ICON_V}.png", "sizes": "192x192", "type": "image/png"},
              {"src": f"icon-512-{ICON_V}.png", "sizes": "512x512", "type": "image/png"}],
}
(SITE / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")

(SITE / "sw.js").write_text("""// Guarda la app para que abra sin internet. Con internet, siempre trae la última versión.
const CACHE = 'horario-v6';
const ASSETS = ['./', './index.html', './plan.json', './manifest.webmanifest', './apple-touch-icon-ICONV.png', './icon-192-ICONV.png', './icon-512-ICONV.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS))); self.skipWaiting(); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    // lo de tu web siempre se pide fresco (sin la caché de 10 min de GitHub); si no hay internet, la copia guardada
    fetch(new URL(e.request.url).origin === location.origin ? new Request(e.request.url, { cache: 'no-cache' }) : e.request).then(r => {
      if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return r;
    }).catch(() => caches.match(e.request, { ignoreSearch: true }).then(m => m || caches.match('./index.html')))
  );
});
""".replace("ICONV", ICON_V), encoding="utf-8")

(SITE / "README.md").write_text("# Horario\n\nMi horario semanal. Ábrelo en Safari y «Añadir a pantalla de inicio».\n\n" + SITE_URL + "\n", encoding="utf-8")
print("site:", sorted(p.name for p in SITE.iterdir()))

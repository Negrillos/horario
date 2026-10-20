// Horario · widget de Scriptable
// Grande: tu día entero. Mediano y pequeño: lo que toca ahora y lo siguiente.
// Al tocar el widget (con «Al interactuar: Ejecutar script») se abre el menú para cambiar lab, OptiSim y fútbol.

const SITE = "https://negrillos.github.io/horario/";
const DATA_URL = SITE + "plan.json";
const HIDE = ["sleep", "routine", "travel"];
const DAYS = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
const KEYS = ["dom", "lun", "mar", "mie", "jue", "vie", "sab"];
const MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

const fm = FileManager.local();
const CACHE = fm.joinPath(fm.documentsDirectory(), "horario-plan.json");
const KEY = "horario-ajustes";
const DEF = { labE: false, optF: true, labR: false, fut: "21" };

const C = (l, d, a) => Color.dynamic(new Color(l, a === undefined ? 1 : a), new Color(d, a === undefined ? 1 : a));
const BG = C("#F1F3F6", "#0E1216");
const FG = C("#121820", "#E5EAEF");
const MUTED = C("#59646F", "#93A0AC");
const FAINT = C("#9AA4AE", "#5A6672");

// ---------- ajustes ----------
function loadSettings() {
  try {
    if (Keychain.contains(KEY)) return Object.assign({}, DEF, JSON.parse(Keychain.get(KEY)));
  } catch (e) {}
  return Object.assign({}, DEF);
}
function saveSettings(s) { Keychain.set(KEY, JSON.stringify(s)); }
function summary(s) {
  return "Lab de Electro: " + (s.labE ? "sí" : "no") + "\nOptiSim viernes: " + (s.optF ? "sí" : "no") +
    "\nLab de RM: " + (s.labR ? "sí" : "no") + "\nFútbol: " + s.fut + "h";
}

// ---------- datos ----------
async function loadPlan() {
  try {
    const req = new Request(DATA_URL + "?t=" + Date.now());
    req.timeoutInterval = 8;
    const plan = await req.loadJSON();
    if (plan && plan.views) { fm.writeString(CACHE, JSON.stringify(plan)); return plan; }
  } catch (e) {}
  if (fm.fileExists(CACHE)) return JSON.parse(fm.readString(CACHE));
  return null;
}

const pad = n => String(n).padStart(2, "0");
const ymd = d => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
const toMin = t => { const p = t.split(":").map(Number); return p[0] * 60 + p[1]; };
const fmt = t => { const p = t.split(":").map(Number); return (p[0] % 24) + ":" + pad(p[1]); };

function pickDay(plan, date) {
  const ds = ymd(date);
  for (const vk of ["esta", "parciales"]) {
    const v = plan.views[vk];
    const d = v && v.days.find(x => x.date === ds);
    if (d) return d;
  }
  return plan.views.tipo.days.find(x => x.k === KEYS[date.getDay()]);
}

function condOk(c, s) {
  if (!c) return true;
  const ok = { labE: s.labE, noLabE: !s.labE, optF: s.optF, noOptF: !s.optF, labR: s.labR, noLabR: !s.labR };
  return c.split("+").every(p => ok[p]);
}

function colorOf(e, plan, alpha) {
  const key = e.sub ? e.sub : (plan.colors[e.c] ? e.c : "neutral");
  const p = plan.colors[key] || plan.colors.neutral;
  return C(p[0], p[1], alpha);
}

function left(mins) {
  if (mins < 60) return mins + "'";
  const h = Math.floor(mins / 60), m = mins % 60;
  return h + " h" + (m ? " " + pad(m) : "");
}

// ---------- widget ----------
function buildWidget(plan, s, family) {
  const w = new ListWidget();
  w.backgroundColor = BG;
  const small = family === "small";
  const big = family === "large" || family === "extraLarge";
  w.setPadding(small ? 12 : 14, small ? 12 : 14, small ? 12 : 12, small ? 12 : 14);

  if (!plan) {
    const t = w.addText("Sin datos todavía. Abre Scriptable con internet una vez.");
    t.font = Font.systemFont(12); t.textColor = FG;
    return w;
  }

  // de 0:00 a 5:00 sigue contando como el día anterior
  const now = new Date();
  const base = new Date(now);
  let nowMin = now.getHours() * 60 + now.getMinutes();
  if (now.getHours() < 5) { base.setDate(base.getDate() - 1); nowMin += 1440; }

  const day = pickDay(plan, base);
  let evs = day.ev.filter(e => condOk(e.cond, s)).concat(day.fut ? plan.fut[s.fut] : []);
  evs.sort((a, b) => toMin(a.s) - toMin(b.s));
  evs = evs.filter(e => HIDE.indexOf(e.c) === -1);

  const cur = evs.findIndex(e => toMin(e.s) <= nowMin && nowMin < toMin(e.e));
  const nxt = evs.findIndex(e => toMin(e.s) > nowMin);

  // cabecera
  const head = w.addStack();
  head.layoutHorizontally(); head.centerAlignContent();
  const title = head.addText(small ? DAYS[base.getDay()] : DAYS[base.getDay()] + " " + base.getDate() + " " + MONTHS[base.getMonth()]);
  title.font = Font.boldSystemFont(small ? 14 : 16); title.textColor = FG; title.lineLimit = 1;
  head.addSpacer();
  let status = "";
  if (cur >= 0) status = "quedan " + left(toMin(evs[cur].e) - nowMin);
  else if (nxt >= 0) status = "luego " + fmt(evs[nxt].s);
  else status = "fin del día";
  if (!small) {
    const st = head.addText(status);
    st.font = Font.mediumMonospacedSystemFont(11); st.textColor = MUTED;
  }
  w.addSpacer(small ? 6 : 8);

  // qué filas caben
  const max = big ? 15 : (small ? 3 : 5);
  let start = 0;
  if (evs.length > max) {
    const anchor = cur >= 0 ? cur : (nxt >= 0 ? nxt : evs.length);
    start = small ? Math.min(anchor, evs.length - max) : Math.max(0, Math.min(anchor - 1, evs.length - max));
    start = Math.max(0, start);
  }
  const rows = evs.slice(start, start + max);
  const fs = small ? 11 : 12;

  rows.forEach((e, i) => {
    const idx = start + i;
    const isCur = idx === cur;
    const isPast = toMin(e.e) <= nowMin;
    const r = w.addStack();
    r.layoutHorizontally(); r.centerAlignContent();
    r.setPadding(2, 4, 2, 6); r.cornerRadius = 5;
    if (isCur) r.backgroundColor = colorOf(e, plan, 0.2);

    const tc = r.addStack(); tc.size = new Size(small ? 38 : 44, 0);
    const t = tc.addText(fmt(e.s));
    t.lineLimit = 1; t.minimumScaleFactor = 0.7;
    t.font = isCur ? Font.boldMonospacedSystemFont(fs - 1) : Font.regularMonospacedSystemFont(fs - 1);
    t.textColor = isPast ? FAINT : MUTED;
    tc.addSpacer();

    const bar = r.addStack(); bar.size = new Size(3, fs + 2); bar.cornerRadius = 1.5;
    bar.backgroundColor = isPast ? FAINT : colorOf(e, plan);
    r.addSpacer(6);

    const name = r.addText(e.c === "exam" ? e.t.toUpperCase() : e.t);
    name.font = (isCur || e.c === "exam") ? Font.semiboldSystemFont(fs) : Font.systemFont(fs);
    name.textColor = isPast ? FAINT : FG;
    name.lineLimit = 1; name.minimumScaleFactor = 0.8;

    if (isCur && !small) {
      r.addSpacer();
      const end = r.addText("→ " + fmt(e.e));
      end.font = Font.mediumMonospacedSystemFont(fs - 2); end.textColor = MUTED;
    }
  });

  const before = start, after = evs.length - start - rows.length;
  if ((before || after) && !small) {
    w.addSpacer(3);
    const more = w.addText((before ? "↑ " + before + " antes" : "") + (before && after ? " · " : "") + (after ? "↓ " + after + " después" : ""));
    more.font = Font.regularMonospacedSystemFont(10); more.textColor = FAINT;
  }
  w.addSpacer();

  // refrescar al cambiar de bloque (iOS decide el momento exacto)
  const bounds = evs.map(e => toMin(e.s)).concat(evs.map(e => toMin(e.e))).filter(m => m > nowMin);
  const nextB = bounds.length ? Math.min.apply(null, bounds) : nowMin + 60;
  w.refreshAfterDate = new Date(Date.now() + Math.min(nextB - nowMin, 30) * 60000);
  return w;
}

// ---------- menú en la app ----------
async function settingsMenu(s) {
  while (true) {
    const a = new Alert();
    a.title = "Horario · esta semana";
    a.message = "Toca para cambiar. El widget usa esto.";
    a.addAction("Lab de Electro (miércoles): " + (s.labE ? "Sí" : "No"));
    a.addAction("OptiSim (viernes): " + (s.optF ? "Sí" : "No"));
    a.addAction("Lab de RM (viernes): " + (s.labR ? "Sí" : "No"));
    a.addAction("Fútbol del lunes: " + s.fut + "h");
    a.addAction("Ver el widget");
    a.addCancelAction("Listo");
    const i = await a.presentSheet();
    if (i === 0) s.labE = !s.labE;
    else if (i === 1) s.optF = !s.optF;
    else if (i === 2) s.labR = !s.labR;
    else if (i === 3) s.fut = s.fut === "21" ? "22" : (s.fut === "22" ? "23" : "21");
    else { saveSettings(s); return i === 4; }
    saveSettings(s);
  }
}

// ---------- main ----------
const settings = loadSettings();
const q = args.queryParameters || {};
const fromApp = ["labE", "optF", "labR", "fut"].some(k => q[k] !== undefined);
const plan = await loadPlan();

if (config.runsInWidget) {
  Script.setWidget(buildWidget(plan, settings, config.widgetFamily));
} else if (fromApp) {
  if (q.labE !== undefined) settings.labE = q.labE === "1";
  if (q.optF !== undefined) settings.optF = q.optF === "1";
  if (q.labR !== undefined) settings.labR = q.labR === "1";
  if (q.fut === "21" || q.fut === "22" || q.fut === "23") settings.fut = q.fut;
  saveSettings(settings);
  const a = new Alert();
  a.title = "Widget actualizado";
  a.message = summary(settings) + "\n\nEl widget se refresca en unos minutos.";
  a.addAction("OK");
  await a.presentAlert();
} else {
  const preview = await settingsMenu(settings);
  if (preview) await buildWidget(plan, settings, "large").presentLarge();
}
Script.complete();

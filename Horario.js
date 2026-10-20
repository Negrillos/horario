// Horario · widget de Scriptable
// Este script es solo un cargador: cada vez que se ejecuta descarga la última versión
// del widget desde tu web, así los cambios llegan solos y no tienes que volver a pegar nada.
// Sin internet usa la última copia guardada.

const CODE_URL = "https://negrillos.github.io/horario/widget.js";
const fm = FileManager.local();
const saved = fm.joinPath(fm.documentsDirectory(), "horario-widget.js");

let code = null;
try {
  const req = new Request(CODE_URL + "?t=" + Date.now());
  req.timeoutInterval = 8;
  const txt = await req.loadString();
  if (txt && txt.indexOf("ListWidget") !== -1) { code = txt; fm.writeString(saved, txt); }
} catch (e) {}
if (!code && fm.fileExists(saved)) code = fm.readString(saved);

try {
  if (!code) throw new Error("No he podido descargar el widget. Abre Scriptable con internet una vez.");
  const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
  await new AsyncFunction(code)();
} catch (e) {
  const w = new ListWidget();
  const t = w.addText("Horario: " + e.message);
  t.font = Font.systemFont(12);
  if (config.runsInWidget) Script.setWidget(w); else await w.presentLarge();
  Script.complete();
}

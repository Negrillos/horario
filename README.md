# Horario

Mi horario semanal. Ábrelo en Safari y «Añadir a pantalla de inicio».

https://negrillos.github.io/horario/

## Cómo se actualiza

- Los bloques del horario están en `src/build.py`. La página se monta con `src/template.html`.
- Para regenerar: `python3 src/build.py` y copiar `src/site/*` a la raíz del repo.
- `Horario.js` es el cargador que va en Scriptable; descarga `widget.js` y `plan.json` de esta web.

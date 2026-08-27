# Plan de producto: una web a la que apetezca volver

Este plan amplía el MVP hacia una experiencia de exploración pública, inspirada en productos de datos ciudadanos como Wikibarrio. La prioridad es ofrecer preguntas concretas, datos comparables y descubrimientos compartibles sin convertir la portada en un catálogo técnico.

## Principios

- Cada pantalla debe responder a una pregunta comprensible: “¿en qué se gasta?”, “¿qué pesa más?”, “¿cómo se compara?” o “¿de dónde sale esta cifra?”.
- Las cifras impactantes aparecen primero; la metodología queda a un clic, pero nunca se oculta.
- AGE, CCAA, entidades locales, contratos y subvenciones son magnitudes separadas. No se suman sin una consolidación oficial.
- Una cifra sin periodo, unidad y fuente no entra en la interfaz.
- El producto debe ser útil aunque el visitante solo permanezca un minuto, y profundo si decide seguir explorando.

## Entregas previstas

### 1. Descubre en 60 segundos

Panel de tarjetas con preguntas y cifras reales: “¿qué partida pesa más?”, “¿cuánto se ha pagado?”, “¿qué comunidad registra más gasto?” y “¿cuántos contratos están disponibles?”. Cada tarjeta enlaza a la vista que explica el dato.

### 2. Comparador que se entiende

Comparar dos CCAA, ejercicios o partidas con unidad y periodo visibles. Añadir evolución cuando haya al menos dos observaciones compatibles; nunca interpolar ni rellenar ausencias con cero.

La primera entrega incluye comparación de dos CCAA y un ranking ordenado por gasto no financiero reconocido. El ranking advierte que no mide riqueza, población ni necesidad.

### 3. Fichas de territorio y municipio

Ficha estable para CCAA, provincia y municipio con presupuesto, ejecución, población, gasto por habitante y enlaces a la fuente. El gasto por habitante solo se calcula con territorio, ejercicio y población compatibles.

### 4. Sigue el dinero

Recorrido administración → programa/partida → contrato o ayuda → empresa/receptor. Solo se dibuja una relación cuando existe una clave o relación publicada; si no, se ofrece como “datos relacionados”, no como causalidad.

La vista de empresas ya ofrece el primer salto contrato → adjudicatario mediante los identificadores publicados en PLACSP.

La API ya dispone de una ficha individual con los contratos vinculados; queda pendiente incorporarla a la interacción visible de la vista.

La ficha ya se abre al seleccionar una empresa y permite seguir cada contrato hasta su registro oficial en PLACSP.

También resume cuántos organismos contratantes aparecen en sus contratos, con una advertencia explícita de que la relación procede de registros publicados.

La ficha de convocatoria BDNS ya está disponible en la API con el presupuesto oficial conservado desde el registro auditado. Las concesiones siguen sin mostrarse hasta disponer de un resultado filtrado y verificable.

La ficha ya se abre dentro de la interfaz al seleccionar una convocatoria y enlaza a su fuente oficial.

La pantalla conserva una separación explícita entre convocatoria y concesión: no muestra beneficiarios mientras el dataset de concesiones no esté cargado.

La API ya consulta concesiones en vivo por código BDNS y conserva el resultado vacío como un estado verificable, no como una ausencia ambigua.

Las fichas de empresa y convocatoria son ahora enlaces reproducibles: al abrir su URL se recupera automáticamente el segundo nivel de detalle.

La ficha BDNS incorpora el bloque de concesiones consultado en vivo; los beneficiarios solo aparecen si la API oficial los devuelve para esa convocatoria.

### 5. Historias y alertas descriptivas

Historias breves sobre cambios, concentración, contratos menores, ejecución y diferencias territoriales. Son indicadores descriptivos, no acusaciones: cada una muestra denominador, fecha, regla y enlace al dataset.

Entrega incorporada: el buscador global también localiza adjudicatarios por nombre o identificador y abre su ficha interna, donde se ven contratos, organismos vinculados e importe adjudicado.

### 6. Base de datos navegable

Explorador con filtros, jerarquías, exportación y URLs compartibles. Incluir cobertura, fecha de actualización y estado de validación en cada dataset.

## Orden de trabajo

1. Descubre en 60 segundos.
2. Comparador e históricos compatibles.
3. Fichas territoriales y geografía INE.
4. Explorador jerárquico y exportaciones ampliadas.
5. Relaciones verificadas de “Sigue el dinero”.
6. Historias, alertas y operación.

## Métrica de éxito

Un visitante debe poder obtener una respuesta útil en menos de un minuto, abrir el desglose de una cifra y compartir exactamente esa lectura mediante una URL. La profundidad se medirá por exploraciones reproducibles, no por cantidad de titulares.

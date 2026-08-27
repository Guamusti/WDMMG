# Metodología

Dinero Público no es una fuente oficial: transforma y enlaza datos publicados por organismos oficiales. Conservamos el registro de origen, URL, versión, fecha de recuperación y ejecución de ingesta.

No se fusionan empresas por parecido textual. El orden de matching es identificador oficial, regla determinista y, solo después, candidato probabilístico pendiente de revisión. No llamamos corrupción, fraude o favoritismo a indicadores descriptivos.

La consolidación de transferencias solo se aplica cuando la fuente aporta una relación verificable o una metodología oficial; en caso contrario se muestran magnitudes brutas separadas.

## Cómo leer la portada

La rueda de políticas usa el gasto realizado de la Cuenta General del Estado 2024, en euros, y muestra cada importe como proporción del total de esa tabla. “Resto de políticas” no es una estimación: es la suma de las políticas oficiales que no se han destacado individualmente; sus subpartidas se conservan en `data/processed/igae/functional-policies-2024.json`.

La ejecución mensual AGE que aparece en la sección posterior es otra magnitud y otro periodo. Sus ratios se calculan sobre el crédito definitivo del mes disponible. No se suman a la rueda funcional ni a contratos o subvenciones.

## Reglas de separación

| Dataset | Qué representa | Qué no representa |
|---|---|---|
| Presupuesto y ejecución IGAE | Crédito, obligaciones y pagos contabilizados | Una lista de contratos o ayudas individuales |
| Clasificación funcional | Finalidad del gasto consolidado del ejercicio | El destino de cada contrato concreto |
| PLACSP | Licitaciones, lotes y datos publicados del expediente | Pagos efectuados |
| BDNS | Convocatorias y concesiones de ayudas | Obligaciones presupuestarias agregadas |

Un euro solo se presenta dentro de la magnitud y el denominador de su fuente. No se suman contratos o subvenciones al gasto ejecutado y no se atribuye una licitación a una política funcional sin una relación oficial explícita.

## Estado de cobertura

La aplicación muestra la fecha, el periodo y la fuente de cada dataset cuando están disponibles. “Pendiente”, “parcial” y “no disponible” son estados de cobertura, no ceros. Si una fuente no publica el nivel inferior, la interfaz lo indica en lugar de rellenarlo con una estimación.

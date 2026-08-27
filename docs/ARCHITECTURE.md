# Arquitectura

El MVP separa cuatro capas:

1. Fuentes oficiales y payloads raw.
2. ETL reproducible con registros de ejecución.
3. PostgreSQL normalizado, con dimensiones presupuestarias y entidades canónicas.
4. API server-side y frontend React; el navegador nunca recibe el universo completo.

La primera administración piloto es la AGE. PLACSP y BDNS se incorporan como registros relacionados, no como gasto ejecutado: sus importes se muestran con definiciones propias y nunca se suman al presupuesto.

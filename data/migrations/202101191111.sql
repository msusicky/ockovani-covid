-- !!!already part of db_create!!!

alter table public.kapacita alter column datum_ziskani set default now();
ALTER TABLE import_log ADD COLUMN status character varying COLLATE pg_catalog."default" NOT NULL DEFAULT 'N/A';

CREATE ROLE ockovani WITH
	LOGIN
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	INHERIT
	NOREPLICATION
	CONNECTION LIMIT -1
	PASSWORD 'xxxxxx';
	
CREATE DATABASE ockovani
    WITH 
    OWNER = ockovani
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;
	
-- Table: public.dny

-- DROP TABLE public.dny;

CREATE TABLE public.dny
(
    den_id serial NOT NULL,
    datum date NOT NULL,
    CONSTRAINT dny_pkey PRIMARY KEY (den_id)
)

TABLESPACE pg_default;

ALTER TABLE public.dny
    OWNER to ockovani;

COMMENT ON TABLE public.dny
    IS 'Tabulka s jednotlivymi dny ny ockovani';
	
-- Table: public.import_log

-- DROP TABLE public.import_log;

CREATE TABLE public.import_log
(
    import_id bigserial NOT NULL ,
    spusteni timestamp without time zone NOT NULL,
	status character varying COLLATE pg_catalog."default" NOT NULL DEFAULT 'N/A',
    CONSTRAINT import_log_pkey PRIMARY KEY (import_id)
)

TABLESPACE pg_default;

ALTER TABLE public.import_log
    OWNER to ockovani;

-- Table: public.kapacita

-- DROP TABLE public.kapacita;

CREATE TABLE public.kapacita
(
    misto_id bigint NOT NULL,
    datum date NOT NULL,
    raw_data json,
    pocet_mist integer,
    datum_ziskani timestamp without time zone DEFAULT NOW(),
    import_id bigint NOT NULL,
    CONSTRAINT kapacita_pkey PRIMARY KEY (misto_id, import_id, datum)
);

ALTER TABLE public.kapacita
    OWNER to ockovani;

COMMENT ON TABLE public.kapacita
    IS 'Tabulka se zjistenymi kapacitami';

-- Table: public.ockovaci_misto

-- DROP TABLE public.ockovaci_misto;

CREATE TABLE public.ockovaci_misto
(
    misto_id bigserial NOT NULL,
    nazev character varying COLLATE pg_catalog."default" NOT NULL,
    service_id integer NOT NULL,
	operation_id integer NOT NULL,
    place_id integer NOT NULL,
    mesto character varying COLLATE pg_catalog."default",
    CONSTRAINT ockovaci_misto_pkey PRIMARY KEY (misto_id)
)

TABLESPACE pg_default;

ALTER TABLE public.ockovaci_misto
    OWNER to ockovani;

	
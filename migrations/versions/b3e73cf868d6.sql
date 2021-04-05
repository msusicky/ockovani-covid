CREATE TABLE public.ockovani_registrace_part
(
    datum date NOT NULL,
    ockovaci_misto_id character varying COLLATE pg_catalog."default" NOT NULL,
    vekova_skupina character varying COLLATE pg_catalog."default" NOT NULL,
    povolani character varying COLLATE pg_catalog."default" NOT NULL,
    stat character varying COLLATE pg_catalog."default" NOT NULL,
    rezervace boolean NOT NULL,
    datum_rezervace date NOT NULL,
    pocet integer,
    import_id integer NOT NULL,
    CONSTRAINT ockovani_registrace_part_pkey PRIMARY KEY (datum, ockovaci_misto_id, vekova_skupina, povolani, stat, rezervace, datum_rezervace, import_id),
    CONSTRAINT ockovani_registrace_part_import_id_fkey FOREIGN KEY (import_id)
        REFERENCES public.importy (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT ockovani_registrace_part_ockovaci_misto_id_fkey FOREIGN KEY (ockovaci_misto_id)
        REFERENCES public.ockovaci_mista (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)PARTITION BY hash(import_id);
CREATE TABLE ockovani_registrace_part_0 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 0);
CREATE TABLE ockovani_registrace_part_1 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 1);
CREATE TABLE ockovani_registrace_part_2 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 2);
CREATE TABLE ockovani_registrace_part_3 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 3);
CREATE TABLE ockovani_registrace_part_4 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 4);	
CREATE TABLE ockovani_registrace_part_5 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 5);	
CREATE TABLE ockovani_registrace_part_6 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 6);	
CREATE TABLE ockovani_registrace_part_7 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 7);	
CREATE TABLE ockovani_registrace_part_8 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 8);	
CREATE TABLE ockovani_registrace_part_9 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 9);	
CREATE TABLE ockovani_registrace_part_10 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 10);	
CREATE TABLE ockovani_registrace_part_11 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 11);	
CREATE TABLE ockovani_registrace_part_12 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 12);	
CREATE TABLE ockovani_registrace_part_13 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 13);	
CREATE TABLE ockovani_registrace_part_14 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 14);	
CREATE TABLE ockovani_registrace_part_15 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 15);	
CREATE TABLE ockovani_registrace_part_16 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 16);	
CREATE TABLE ockovani_registrace_part_17 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 17);	
CREATE TABLE ockovani_registrace_part_18 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 18);	
CREATE TABLE ockovani_registrace_part_19 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 19);	
CREATE TABLE ockovani_registrace_part_20 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 20);	
CREATE TABLE ockovani_registrace_part_21 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 21);	
CREATE TABLE ockovani_registrace_part_22 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 22);	
CREATE TABLE ockovani_registrace_part_23 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 23);	
CREATE TABLE ockovani_registrace_part_24 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 24);	
CREATE TABLE ockovani_registrace_part_25 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 25);	
CREATE TABLE ockovani_registrace_part_26 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 26);	
CREATE TABLE ockovani_registrace_part_27 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 27);	
CREATE TABLE ockovani_registrace_part_28 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 28);	
CREATE TABLE ockovani_registrace_part_29 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 29);	
CREATE TABLE ockovani_registrace_part_30 PARTITION OF ockovani_registrace_part FOR VALUES WITH (MODULUS 31, REMAINDER 30);	
insert into ockovani_registrace_part select * from ockovani_registrace;
alter table public.ockovani_registrace rename to ockovani_registrace_old;
alter table public.ockovani_registrace_part rename to ockovani_registrace;
create index idx_o_r_ockovaci_misto_id on ockovani_registrace (ockovaci_misto_id);
INSERT INTO public.ockovaci_misto (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice TGM Hodonín', 411869, 5985, 3177, 'Hodonín', 'Jihomoravský');
INSERT INTO public.ockovaci_misto (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Prachatice, a.s.', 411731, 5956, 3089, 'Prachatice', 'Jihočeský');
INSERT INTO public.ockovaci_misto (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('AGEL Středomoravská nemocniční a.s. - Přerov', 411776, 5995, 3202, 'Přerov', 'Olomoucký');
INSERT INTO public.ockovaci_misto (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Slaný', 411743, 5967, 3122, 'Slaný', 'Středočeský');
INSERT INTO public.ockovaci_misto (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Strakonice, a.s. - infekční ambulance', 411737, 5961, 3104, 'Strakonice', 'Jihočeský');

CREATE TABLE public.ockovaci_misto_tmp
(
    misto_id bigserial NOT NULL,
    nazev character varying COLLATE pg_catalog."default" NOT NULL,
    service_id integer NOT NULL,
	operation_id integer NOT NULL,
    place_id integer NOT NULL,
    covtest_id character varying COLLATE pg_catalog."default",
    mesto character varying COLLATE pg_catalog."default",
    kraj character varying COLLATE pg_catalog."default",
    CONSTRAINT ockovaci_misto_tmp_pkey PRIMARY KEY (misto_id)
)

TABLESPACE pg_default;

ALTER TABLE public.ockovaci_misto_tmp
    OWNER to ockovani;

INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Rudolfa a Stefanie Benešov, a.s.', 411677, 5899, 2981, 'Benešov', 'Středočeský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Hornická nemocnice s poliklinikou spol. s.r.o.', 411812, 6020, 3287, 'Bílina', 'Ústecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Bílovecká nemocnice, a.s.', 411766, 5988, 3186, 'Bílovec', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Bohumínská městská nemocnice  a.s.', 411840, 6049, 3345, 'Bohumín', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Zdravotní ústav se sídlem v Ostravě - Brno', 411789, 5889, 3231, 'Brno', 'Jihomoravský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Fakultní nemocnice u sv. Anny v Brně', 411653, 5869, 2911, 'Brno', 'Jihomoravský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('BVV velkokapacitní očkovací centrum', 411667, 5885, 2948, 'Brno', 'Jihomoravský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice s poliklinikou Česká Lípa a.s.', 411747, 5971, 3134, 'Česká Lípa', 'Liberecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Očkovací centrum Výstaviště České Budějovice (pavilon T1, vstup od Tesca)', 411685, 5910, 2996, 'České Budějovice', 'Jihočeský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('VITA s.r.o', 411802, 6010, 3259, 'Duchcov', 'Ústecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice ve Frýdku-Místku, p.o.', 411745, 5969, 3128, 'Frýdek-Místek', 'Moravskoslezský', 'bf00fe5a-e365-461c-9007-3d9329705ffe');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Moje Ambulance a.s. Frýdek - Místek', 411884, 6104, 3440, 'Frýdek-Místek', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice s poliklinikou Havířov, p.o.', 411820, 6026, 3301, 'Havířov', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Havlíčkův Brod', 411803, 6012, 3262, 'Havlíčkův Brod', 'Vysočina', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice TGM Hodonín', 411869, 5985, 3177, 'Hodonín', 'Jihomoravský', '995902bc-6243-419d-962e-fbe99d97bb2d');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Fakultní nemocnice Hradec Králové', 411675, 5898, 2976, 'Hradec Králové', 'Královéhradecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Hranice a.s.', 411721, 5949, 3073, 'Hranice', 'Olomoucký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Hustopeče, p.o.', 411804, 6013, 3268, 'Hustopeče', 'Jihomoravský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Karlovarská krajská nemocnice a.s. - Cheb', 411828, 5866, 3312, 'Cheb', 'Karlovarský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Krajská zdravotní, a.s. - Nemocnice Chomutov, o.z.', 411847, 6056, 3368, 'Chomutov', 'Ústecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Jablonec nad Nisou, p. o.', 411708, 5936, 3036, 'Jablonec nad Nisou', 'Liberecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Jihlava', 411659, 5875, 2929, 'Jihlava', 'Vysočina', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Masarykova městská nemocnice a.s. (Jilemnice)', 411819, 5926, 3061, 'Jilemnice', 'Liberecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Karlovarská krajská nemocnice a.s.', 411650, 5866, 2902, 'Karlovy Vary', 'Karlovarský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice s poliklinikou Karviná-Ráj', 411827, 6030, 3310, 'Karviná', 'Moravskoslezský', '1668a0ae-d1db-4811-aa21-d961e3ffb6ee');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Karvinská hornická nemocnice a.s.', 411858, 6066, 3389, 'Karviná', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Oblastní nemocnice Kladno', 411661, 5877, 2935, 'Kladno', 'Středočeský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Oblastní nemocnice Kolín', 411660, 5876, 2932, 'Kolín', 'Středočeský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('SZZ Krnov', 411878, 6093, 3432, 'Krnov', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Kroměřížská nemocnice a.s.', 411816, 6023, 3296, 'Kroměříž', 'Zlínský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Kutná Hora', 411720, 5947, 3067, 'Kutná Hora', 'Středočeský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Krajská nemocnice Liberec a.s.', 411651, 5867, 2905, 'Liberec', 'Liberecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Litoměřice a.s.', 411722, 5948, 3070, 'Litoměřice', 'Ústecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Krajská zdravotní, a.s. - Nemocnice Most, o.z.', 411845, 6054, 3362, 'Most', 'Ústecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Neratovice', 411734, 5958, 3095, 'Neratovice', 'Středočeský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Nové Město na Moravě', 411728, 5953, 3080, 'Nové Město na Moravě', 'Vysočina', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice AGEL Nový Jičín a.s.', 411774, 5993, 3199, 'Nový Jičín', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Fakultní nemocnice Olomouc', 411652, 5868, 2908, 'Olomouc', 'Olomoucký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Vojenská nemocnice Olomouc', 411664, 5880, 2944, 'Olomouc', 'Olomoucký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Slezská nemocnice v Opavě', 411795, 6003, 3243, 'Opava', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('EUC Klinika Ostrava', 411697, 5925, 3021, 'Ostrava', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Zdravotní ústav se sídlem v Ostravě - Ostrava', 411788, 5889, 3230, 'Ostrava', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Městská nemocnice Ostrava, p.o.', 411801, 6009, 3256, 'Ostrava', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Fakultní nemocnice Ostrava', 411670, 5893, 2951, 'Ostrava', 'Moravskoslezský', '52fb0fed-283c-4e83-93d0-4bffa2d8c38f');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Moje Ambulance a.s. Ostrava - Poruba', 411885, 6103, 3441, 'Ostrava', 'Moravskoslezský', 'f53c2d14-2570-49cd-a03f-5595e647a4d9');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Fakultní Nemocnice Plzeň', 411649, 5865, 2899, 'Plzeň', 'Plzeňský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Fakultní nemocnice Královské Vinohrady', 411674, 5894, 2969, 'Praha', 'Praha', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Fakultní Thomayerova nemocnice', 411518, 5895, 2972, 'Praha', 'Praha', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Fakultní nemocnice v Motole', 411655, 5871, 2917, 'Praha', 'Praha', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice na Homolce', 411657, 5873, 2923, 'Praha', 'Praha', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Ústřední vojenská nemocnice - Očkovací centrum, pavilon L', 411839, 5892, 3341, 'Praha', 'Praha', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Fakultní nemocnice Bulovka', 411671, 5890, 2953, 'Praha', 'Praha', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Ústřední vojenská nemocnice - Ambulance ORT, pavilon A1', 411669, 5892, 2954, 'Praha', 'Praha', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Vakcinační centrum IKEM', 411654, 5870, 2914, 'Praha', 'Praha', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Státní zdravotní ústav', 411760, 5983, 3171, 'Praha', 'Praha', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Prachatice, a.s.', 411731, 5956, 3089, 'Prachatice', 'Jihočeský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('AGEL Středomoravská nemocniční a.s. - Přerov', 411776, 5995, 3202, 'Přerov', 'Olomoucký', '60c02833-61a2-438b-acac-19d6c91fa5a3');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Rokycanská nemocnice', 411758, 5981, 3165, 'Rokycany', 'Plzeňský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('MEDITERRA - Sedlčany s.r.o.', 411738, 6073, 3405, 'Sedlčany', 'Středočeský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Slaný', 411743, 5967, 3122, 'Slaný', 'Středočeský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Sokolov', 411798, 6007, 3250, 'Sokolov', 'Karlovarský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Stodská nemocnice', 411763, 5986, 3180, 'Stod', 'Plzeňský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Strakonice, a.s. - infekční ambulance', 411737, 5961, 3104, 'Strakonice', 'Jihočeský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Sušická nemocnice', 411761, 5984, 3174, 'Sušice', 'Plzeňský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Oblastní nemocnice Trutnov a.s.', 411756, 5979, 3152, 'Trutnov', 'Královéhradecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Nemocnice Třinec, p.o.', 411841, 6050, 3350, 'Třinec', 'Moravskoslezský', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Uherskohradišťská nemocnice a.s.', 411762, 5985, 3177, 'Uherské Hradiště', 'Zlínský', 'e0c2a0cf-b0e1-4ad2-8cee-0c0c4cb5adf9');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Masarykova nemocnice Ústí nad Labem', 411656, 5872, 2920, 'Ústí nad Labem', 'Ústecký', null);
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj, covtest_id) VALUES ('Vsetínská nemocnice', 411768, 5991, 3191, 'Vsetín', 'Zlínský', null);

ALTER TABLE public.ockovaci_misto ADD COLUMN covtest_id character varying COLLATE pg_catalog."default";

UPDATE public.ockovaci_misto m SET covtest_id = t.covtest_id FROM public.ockovaci_misto_tmp t WHERE m.nazev = t.nazev;

DROP TABLE public.ockovaci_misto_tmp;

ALTER TABLE public.kapacita ADD COLUMN kapacita_id bigserial NOT NULL;
ALTER TABLE public.kapacita ADD COLUMN covtest_id character varying COLLATE pg_catalog."default";
ALTER TABLE public.kapacita ALTER COLUMN misto_id DROP NOT NULL;
ALTER TABLE public.kapacita DROP CONSTRAINT kapacita_pkey;
ALTER TABLE public.kapacita ADD CONSTRAINT kapacita_pkey PRIMARY KEY (kapacita_id);
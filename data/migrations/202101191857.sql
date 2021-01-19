CREATE TABLE public.ockovaci_misto_tmp
(
    misto_id bigserial NOT NULL,
    nazev character varying COLLATE pg_catalog."default" NOT NULL,
    service_id integer NOT NULL,
	operation_id integer NOT NULL,
    place_id integer NOT NULL,
    mesto character varying COLLATE pg_catalog."default",
    kraj character varying COLLATE pg_catalog."default",
    CONSTRAINT ockovaci_misto_tmp_pkey PRIMARY KEY (misto_id)
)

TABLESPACE pg_default;

ALTER TABLE public.ockovaci_misto_tmp
    OWNER to ockovani;

INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Rudolfa a Stefanie Benešov, a.s.', 411677, 5899, 2981, 'Benešov', 'Středočeský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Hornická nemocnice s poliklinikou spol. s.r.o.', 411812, 6020, 3287, 'Bílina', 'Ústecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Bílovecká nemocnice, a.s.', 411766, 5988, 3186, 'Bílovec', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Bohumínská městská nemocnice  a.s.', 411840, 6049, 3345, 'Bohumín', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Zdravotní ústav se sídlem v Ostravě - Brno', 411789, 5889, 3231, 'Brno', 'Jihomoravský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Fakultní nemocnice u sv. Anny v Brně', 411653, 5869, 2911, 'Brno', 'Jihomoravský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('BVV velkokapacitní očkovací centrum', 411667, 5885, 2948, 'Brno', 'Jihomoravský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice s poliklinikou Česká Lípa a.s.', 411747, 5971, 3134, 'Česká Lípa', 'Liberecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Očkovací centrum Výstaviště České Budějovice (pavilon T1, vstup od Tesca)', 411685, 5910, 2996, 'České Budějovice', 'Jihočeský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('VITA s.r.o', 411802, 6010, 3259, 'Duchcov', 'Ústecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice ve Frýdku-Místku, p.o.', 411745, 5969, 3128, 'Frýdek-Místek', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Moje Ambulance a.s. Frýdek - Místek', 411884, 6104, 3440, 'Frýdek-Místek', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice s poliklinikou Havířov, p.o.', 411820, 6026, 3301, 'Havířov', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Havlíčkův Brod', 411803, 6012, 3262, 'Havlíčkův Brod', 'Vysočina');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Fakultní nemocnice Hradec Králové', 411675, 5898, 2976, 'Hradec Králové', 'Královéhradecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Hranice a.s.', 411721, 5949, 3073, 'Hranice', 'Olomoucký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Hustopeče, p.o.', 411804, 6013, 3268, 'Hustopeče', 'Jihomoravský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Karlovarská krajská nemocnice a.s. - Cheb', 411828, 5866, 3312, 'Cheb', 'Karlovarský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Krajská zdravotní, a.s. - Nemocnice Chomutov, o.z.', 411847, 6056, 3368, 'Chomutov', 'Ústecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Jablonec nad Nisou, p. o.', 411708, 5936, 3036, 'Jablonec nad Nisou', 'Liberecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Jihlava', 411659, 5875, 2929, 'Jihlava', 'Vysočina');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Masarykova městská nemocnice a.s. (Jilemnice)', 411819, 5926, 3061, 'Jilemnice', 'Liberecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Karlovarská krajská nemocnice a.s.', 411650, 5866, 2902, 'Karlovy Vary', 'Karlovarský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice s poliklinikou Karviná-Ráj', 411827, 6030, 3310, 'Karviná', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Karvinská hornická nemocnice a.s.', 411858, 6066, 3389, 'Karviná', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Oblastní nemocnice Kladno', 411661, 5877, 2935, 'Kladno', 'Středočeský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Oblastní nemocnice Kolín', 411660, 5876, 2932, 'Kolín', 'Středočeský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('SZZ Krnov', 411878, 6093, 3432, 'Krnov', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Kroměřížská nemocnice a.s.', 411816, 6023, 3296, 'Kroměříž', 'Zlínský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Kutná Hora', 411720, 5947, 3067, 'Kutná Hora', 'Středočeský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Krajská nemocnice Liberec a.s.', 411651, 5867, 2905, 'Liberec', 'Liberecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Litoměřice a.s.', 411722, 5948, 3070, 'Litoměřice', 'Ústecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Krajská zdravotní, a.s. - Nemocnice Most, o.z.', 411845, 6054, 3362, 'Most', 'Ústecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Neratovice', 411734, 5958, 3095, 'Neratovice', 'Středočeský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Nové Město na Moravě', 411728, 5953, 3080, 'Nové Město na Moravě', 'Vysočina');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice AGEL Nový Jičín a.s.', 411774, 5993, 3199, 'Nový Jičín', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Fakultní nemocnice Olomouc', 411652, 5868, 2908, 'Olomouc', 'Olomoucký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Vojenská nemocnice Olomouc', 411664, 5880, 2944, 'Olomouc', 'Olomoucký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Slezská nemocnice v Opavě', 411795, 6003, 3243, 'Opava', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('EUC Klinika Ostrava', 411697, 5925, 3021, 'Ostrava', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Zdravotní ústav se sídlem v Ostravě - Ostrava', 411788, 5889, 3230, 'Ostrava', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Městská nemocnice Ostrava, p.o.', 411801, 6009, 3256, 'Ostrava', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Fakultní nemocnice Ostrava', 411670, 5893, 2951, 'Ostrava', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Moje Ambulance a.s. Ostrava - Poruba', 411885, 6103, 3441, 'Ostrava', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Fakultní Nemocnice Plzeň', 411649, 5865, 2899, 'Plzeň', 'Plzeňský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Fakultní nemocnice Královské Vinohrady', 411674, 5894, 2969, 'Praha', 'Praha');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Fakultní Thomayerova nemocnice', 411518, 5895, 2972, 'Praha', 'Praha');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Fakultní nemocnice v Motole', 411655, 5871, 2917, 'Praha', 'Praha');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice na Homolce', 411657, 5873, 2923, 'Praha', 'Praha');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Ústřední vojenská nemocnice - Očkovací centrum, pavilon L', 411839, 5892, 3341, 'Praha', 'Praha');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Fakultní nemocnice Bulovka', 411671, 5890, 2953, 'Praha', 'Praha');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Ústřední vojenská nemocnice - Ambulance ORT, pavilon A1', 411669, 5892, 2954, 'Praha', 'Praha');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Vakcinační centrum IKEM', 411654, 5870, 2914, 'Praha', 'Praha');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Státní zdravotní ústav', 411760, 5983, 3171, 'Praha', 'Praha');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Rokycanská nemocnice', 411758, 5981, 3165, 'Rokycany', 'Plzeňský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('MEDITERRA - Sedlčany s.r.o.', 411738, 6073, 3405, 'Sedlčany', 'Středočeský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Sokolov', 411798, 6007, 3250, 'Sokolov', 'Karlovarský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Stodská nemocnice', 411763, 5986, 3180, 'Stod', 'Plzeňský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Sušická nemocnice', 411761, 5984, 3174, 'Sušice', 'Plzeňský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Oblastní nemocnice Trutnov a.s.', 411756, 5979, 3152, 'Trutnov', 'Královéhradecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Nemocnice Třinec, p.o.', 411841, 6050, 3350, 'Třinec', 'Moravskoslezský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Uherskohradišťská nemocnice a.s.', 411762, 5985, 3177, 'Uherské Hradiště', 'Zlínský');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Masarykova nemocnice Ústí nad Labem', 411656, 5872, 2920, 'Ústí nad Labem', 'Ústecký');
INSERT INTO public.ockovaci_misto_tmp (nazev, service_id, operation_id, place_id, mesto, kraj) VALUES ('Vsetínská nemocnice', 411768, 5991, 3191, 'Vsetín', 'Zlínský');

ALTER TABLE public.ockovaci_misto ADD COLUMN kraj character varying COLLATE pg_catalog."default";

UPDATE public.ockovaci_misto m SET m.kraj = t.kraj FROM public.ockovaci_misto_tmp t WHERE m.nazev = t.nazev;

DROP TABLE public.ockovaci_misto_tmp;


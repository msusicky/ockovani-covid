# Volná místa na COVID-19 očkování
Za systémem stojí Jan Staněk (http://jstanek.cz/), Marek Sušický (marek(at)susicky.net) a přátele, kteří poskytli cenné připomínky.

Během marné snahy zajistit očkovací místa pro příbuzné jsme si všimli toho, že neexistuje žádný přehled volných míst. Ještě v lednu jsme začali tvořit aplikaci, ale narazili na neexistenci dat. Pak došly vakcíny a nedávalo smysl systém spouštět. Nyní je situace taková, že mnoho lidí čeká na vakcinaci, ale pokud nejsou na tom správném místě, budou čekat dál. Na jiných místech už ale lidé 80+ "došli". S naší mapou se lidé mohou přeregistrovat, dostat vakcinu rychleji a zefektivnit celý proces očkování. Prosím kohokoliv, kdo může přispět ke zveřejnění oficiálních dat o volných kapacitách a distribuci vakcín, aby tak učinil.

Web: https://msusicky.github.io/ockovani-covid/

## Napsali o nás
* https://denikn.cz/569269/kde-maji-volna-mista-programatori-po-nocich-vymysleli-aplikaci-ktera-muze-zkratit-cekani-na-vakcinu
* https://www.zive.cz/clanky/kdyz-to-neudelal-stat-poradili-si-programatori-sami-vytvorili-aplikaci-s-prehledem-volnych-mist-pro-ockovani/sc-3-a-208719/default.aspx
* https://domaci.ihned.cz/c1-66889710-programator-rozjel-web-ktery-ukaze-kde-je-volno-na-ockovani-ve-skladech-lezi-250-tisic-davek-vakcin-rika

## Poznámky k fungování
Pro získávání dat využívá metody scrapingu. Vzhledem k tomu, že jsou data zveřejňována na githubu, **prosím scraper nespouštějte na vlastním prostředí a nezpůsobujte tak zbytečnou další zátěž rezervačnímu systému!**

Aplikace se skládá z modulu fetcher, pak samotného webu a skriptu, který web stáhne a publikuje na github pages. Tento krok je realizován proto, že nechceme vystavovat veřejně aplikační server a chceme přenést zátěž na prostředky Githubu. Navíc jde o statické stránky, u kterých není problém obsloužit mnoho tisíc lidí současně.


# How to run it [ENG]

## Installation

### Virtual environment

#### Create venv
`python3 -m venv venv`

#### Activate venv
`source venv/bin/activate`

#### Install requirements
`pip install -r requirements.txt`

### Configuration
* Fill connection string in `config.py`
* Setup `config.ini` according to the `config.ini.template`

### Flask application
```
export FLASK_ENV=development
flask db upgrade
flask run
```

## Update
1. update config.ini
1. activate venv `source venv/bin/activate`
1. execute database migration if needed `flask db upgrade`   
1. fetch data `flask fetch-all &`
1. restart or start webserver if needed `flask run --host=0.0.0.0 --port=5001 &`
1. publish website and CSV's `bash tools/manual_publish.sh`
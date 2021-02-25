# Volná místa na COVID-19 očkování
Za systémem stojí Jan Staněk (http://jstanek.cz/), Marek Sušický (marek(at)susicky.net) a přátele, kteří poskytli cenné připomínky.

Během marné snahy zajistit očkovací místa pro příbuzné jsme si všimli toho, že neexistuje žádný přehled volných míst. Ještě v lednu jsme začali tvořit aplikaci, ale narazili na neexistenci dat. Pak došly vakcíny a nedávalo smysl systém spouštět. Nyní je situace taková, že mnoho lidí čeká na vakcinaci, ale pokud nejsou na tom správném místě, budou čekat dál. Na jiných místech už ale lidé 80+ "došli". S naší mapou se lidé mohou přeregistrovat, dostat vakcinu rychleji a zefektivnit celý proces očkování. Prosím kohokoliv, kdo může přispět ke zveřejnění oficiálních dat o volných kapacitách a distribuci vakcín, aby tak učinil.

## Napsali o nás
https://denikn.cz/569269/kde-maji-volna-mista-programatori-po-nocich-vymysleli-aplikaci-ktera-muze-zkratit-cekani-na-vakcinu

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

### 
```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

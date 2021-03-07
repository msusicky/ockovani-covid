[![deploy-acceptance](https://github.com/msusicky/ockovani-covid/actions/workflows/deploy-acceptance.yml/badge.svg)](https://github.com/msusicky/ockovani-covid/actions/workflows/deploy-acceptance.yml)
[![deploy-production](https://github.com/msusicky/ockovani-covid/actions/workflows/deploy-production.yml/badge.svg)](https://github.com/msusicky/ockovani-covid/actions/workflows/deploy-production.yml)
[![update-data](https://github.com/msusicky/ockovani-covid/actions/workflows/update-data.yml/badge.svg)](https://github.com/msusicky/ockovani-covid/actions/workflows/update-data.yml)
[![update-web](https://github.com/msusicky/ockovani-covid/actions/workflows/update-web.yml/badge.svg)](https://github.com/msusicky/ockovani-covid/actions/workflows/update-web.yml)

# COVID-19 data o očkování
Za systémem stojí Jan Staněk (http://jstanek.cz/), Marek Sušický (marek(at)susicky.net) a přátele, kteří poskytli cenné připomínky.

## Čtěte!
Tento web poskytuje data, která zobrazují statistiky jednotlivých očkovacích míst. Systém je komplikovaný a pro správná rozhodnutí je nezbytné si přečíst, jak funguje. Nezávazně doporučujeme sledovat, kolik je na daném místě registrovaných lidí, kteří mají a nemají termín, kolik je volných slotů na očkování a kolik  vakcín přibližně dostává dané místo. Nedává smysl měnit často registraci, změnou registrace se dostáváte na poslední místo ve stejné věkové kategorii na novém místě.

## Starý popis webu - před dostupností opendat od UZIS
Během marné snahy zajistit očkovací místa pro příbuzné jsme si všimli toho, že neexistuje žádný přehled volných míst. Ještě v lednu jsme začali tvořit aplikaci, ale narazili na neexistenci dat. Pak došly vakcíny a nedávalo smysl systém spouštět. Nyní je situace taková, že mnoho lidí čeká na vakcinaci, ale pokud nejsou na tom správném místě, budou čekat dál. Na jiných místech už ale lidé 80+ "došli". S naší mapou se lidé mohou přeregistrovat, dostat vakcinu rychleji a zefektivnit celý proces očkování. Prosím kohokoliv, kdo může přispět ke zveřejnění oficiálních dat o volných kapacitách a distribuci vakcín, aby tak učinil.

Web: https://ockovani.opendatalab.cz

## Napsali o nás
* https://denikn.cz/569269/kde-maji-volna-mista-programatori-po-nocich-vymysleli-aplikaci-ktera-muze-zkratit-cekani-na-vakcinu
* https://www.zive.cz/clanky/kdyz-to-neudelal-stat-poradili-si-programatori-sami-vytvorili-aplikaci-s-prehledem-volnych-mist-pro-ockovani/sc-3-a-208719/default.aspx
* https://domaci.ihned.cz/c1-66889710-programator-rozjel-web-ktery-ukaze-kde-je-volno-na-ockovani-ve-skladech-lezi-250-tisic-davek-vakcin-rika

## Poznámky k fungování
Pro získávání dat využívala metody scrapingu. Nyní využíváme oficiálních dat od UZIS.

Aplikace se skládá z modulu fetcher, pak samotného webu a skriptu, který web stáhne a publikuje na github pages. Tento krok je realizován proto, že nechceme vystavovat veřejně aplikační server a chceme přenést zátěž na prostředky Githubu. Navíc jde o statické stránky, u kterých není problém obsloužit mnoho tisíc lidí současně.


# How to run it [ENG]

## Quick start with docker-compose
To start the server without fetching recent data use `docker-compose up`.

The development server (default flask one for the moment) will start at port `5000`,
you can access the deployment at `http://localhost:5000/`.

If you want to fetch recent data please set the FETCH_DATA environment variable: 

`FETCH_DATA=true docker-compose up`

## Installation without docker-compose
1. create virtual environment
    
    `python3 -m venv venv`

1. activate virtual environment 
    
    `source venv/bin/activate`

1. install requirements

    `pip install -r requirements.txt`

1. setup `config.py` according to the `config.sample.py` template

1. setup Flask environment
    
    `export FLASK_ENV=development`

1. execute database migrations
    
    `flask db upgrade`

1. start Flask webserver
    
    `flask run`

## Update web
_Old manual way, now it's done automatically using GitHub Actions._

1. activate venv
 
    `source venv/bin/activate`

1. execute database migration if needed

    `flask db upgrade`

1. fetch data
    
    `flask fetch-opendata`

1. restart or start webserver if needed

    `systemctl start ockovani-prd.service`

1. publish website

    `bash tools/manual_publish.sh`

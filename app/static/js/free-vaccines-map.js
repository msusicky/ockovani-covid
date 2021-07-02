let table = [], columns = [], debug = [], counter = 0, max = 0, m, layer;
const progressBar = document.getElementById('progress-bar');
drawMap();

function drawMap() {
    let tableContent = document.getElementById('centers-table').innerHTML;

    // process html table to js
    const regexp = /<tr.*?>([\s\S]*?)<\/tr>/g;
    let match, i = 0;
    while ((match = regexp.exec(tableContent)) !== null) {
        if (i > 0) table.push([])
        const regexp2 = /<t[hd].*?>([\s\S]*?)<\/t[hd]>/g;
        let match2, j = 0;
        while ((match2 = regexp2.exec(match[1])) !== null) {
            let cleanText = match2[1].trim().replace(/<br>/g, ', ').replace(/^, /g, '').replace(/<.*?>/g, '');

            if (j == 7 || j == 8) {
                cleanText = cleanText
                    .replace(/\b([a-zA-Z][a-zA-Z0-9.-]+@[a-zA-Z.-]+)\b/g, '<a href="mailto:$1">$1</a>')
                    .replace(/(\b|\+\d\d\d\s?)(\d\d\d)\s?(\d\d\d)\s?(\d\d\d)\b/g, '<a href="tel:$1$2$3$4">$1 $2 $3 $4</a>')
                    .replace(/\b(https?:\/\/)?(www\.[A-Za-z.-]+?\.cz(\/.*?)?)\b/g, '<a href="http://$2">$2</a>')
            }

            if (i > 0) table[table.length - 1].push(cleanText)
            else if (i == 0) columns.push(cleanText)
            j++;
        }
        i++;
    }

    // fix duplicates
    table.forEach(row => {
        if (row[0]) {
            let sameAddress = table.find(r => (r[6] == row[6] && r[4] == row[4] && r[3] == row[3]))
            if (sameAddress != row) {
                row.forEach((item, k) => {
                    if (item != sameAddress[k] || k == 1) {
                        sameAddress[k] += ' / ' + item;
                    }
                });
                row[0] = false;
            }
        }
    });

    // remove empty or "deleted" rows
    table = table.filter(r => r[0]);

    // prepare map
    var center = SMap.Coords.fromWGS84(15.5, 49.8);
    m = new SMap(JAK.gel('map'), center, 7);
    m.addDefaultLayer(SMap.DEF_BASE).enable();
    m.addDefaultControls();
    m.getSignals().addListener(window, 'map-focus', () => m.removeCard());

    // prepare layer
    layer = new SMap.Layer.Marker();
    m.addLayer(layer);
    layer.enable();

    // draw points
    table.forEach((row, i) => {
        setTimeout(() => {
            new SMap.Geocoder(row[6] + ', ' + row[4], (geocoder) => {
                let order = [6, 4, 2, 1, 7, 8, 0];
                let bodyHtml = '';
                order.forEach(n => {
                    bodyHtml += row[n] ? `<strong>${columns[n]}:</strong> ${row[n]}<br>` : ''
                })

                if (!geocoder.getResults()[0].results.length) {
                    // document.getElementById('not-found').innerHTML += `<div class="not-found-item"><strong>${row[5]}</strong><br>${bodyHtml}</div>`
                    // document.getElementById('not-found-heading').style.display = 'block';
                } else {
                    let result = geocoder.getResults()[0].results[0];
                    debug.push([row[6], row[4], result.label]);
                    let card = new SMap.Card();
                    card.getHeader().innerHTML = `<strong>${row[5]}</strong>`;
                    card.getBody().innerHTML = bodyHtml
                        + `<a class="btn btn-success mt-2 mr-2" title="Zobrazit na Mapy.cz" href="https://mapy.cz/?source=${result.source}&id=${result.id}">Mapy.cz</a>`
                        + `<a class="btn btn-secondary mt-2" title="Zobrazit v Mapách Google" href="https://www.google.com/maps/place/${result.coords.y} ${result.coords.x}">Mapy Google</a>`;
                    card.getFooter().style.display = 'none';
                    card.getContainer().style.padding = 0;
                    let options = { title: row[5] };
                    let marker = new SMap.Marker(result.coords, false, options);
                    marker.decorate(SMap.Marker.Feature.Card, card);
                    layer.addMarker(marker);
                }

                counter--;
                let progressPercent = (max - counter) / max * 100;
                progressBar.style.width = `${progressPercent}%`;
                progressBar.setAttribute('aria-valuenow', progressPercent);
                if (counter == 0) { document.getElementById('progress').style.opacity = 0; }
            }, { count: 1 });
        }, i * 150);
        counter++;
    });

    max = counter;
}


function myLocation() {
    if (!navigator.geolocation) {
        alert('Váš prohlížeč nepodporuje funkci Moje poloha.');
    } else {
        navigator.geolocation.getCurrentPosition((pos) => {
            if (layer && m) {
                let myLocationCoords = SMap.Coords.fromWGS84(pos.coords.longitude, pos.coords.latitude);
                let marker = new SMap.Marker(myLocationCoords, false, { title: 'Vaše poloha' });
                let card = new SMap.Card();
                card.getBody().innerHTML = 'Vaše poloha';
                card.getHeader().style.display = 'none';
                card.getFooter().style.display = 'none';
                card.getContainer().style.padding = 0;
                marker.decorate(SMap.Marker.Feature.Card, card);
                layer.addMarker(marker);
                m.setCenterZoom(myLocationCoords, 10, true);
            }
        }, console.error);
    }
}

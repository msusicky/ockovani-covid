// To have the possibility to send links with opened tab
$(document).ready(() => {
    let url = location.href.replace(/\/$/, "");

    if (location.hash) {
        const hash = url.split("#");
        $('#cards a[href="#' + hash[1] + '"]').tab("show");
        url = location.href.replace(/\/#/, "#");
        history.replaceState(null, null, url);
        setTimeout(() => {
            $(window).scrollTop(0);
        }, 400);
    }

    $('a[data-toggle="tab"]').on("click", function () {
        let newUrl;
        const hash = $(this).attr("href");
        if (hash == "#") {
            newUrl = url.split("#")[0];
        } else {
            newUrl = url.split("#")[0] + hash;
        }
        newUrl += "";
        history.replaceState(null, null, newUrl);
    });
});

<!-- Color palette -->
const palette = [
    '#1f77b4',  // muted blue
    '#ff7f0e',  // safety orange
    '#2ca02c',  // cooked asparagus green
    '#d62728',  // brick red
    '#9467bd',  // muted purple
    '#8c564b',  // chestnut brown
    '#e377c2',  // raspberry yogurt pink
    '#7f7f7f',  // middle gray
    '#bcbd22',  // curry yellow-green
    '#17becf'   // blue-teal
];
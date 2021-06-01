// To have the possibility to send links with opened tab
$(function(){
  var hash = window.location.hash;
  hash && $('ul.nav a[href="' + hash + '"]').tab('show');

  $('.nav-tabs a').click(function (e) {
    $(this).tab('show');
    var scrollmem = $('body').scrollTop() || $('html').scrollTop();
    window.location.hash = this.hash;
    $('html,body').scrollTop(scrollmem);
  });
});


// Sortable tables
$(function () {
    $('.col-sortable').click(function () {
        var tbody = $(this).parents('table').eq(0).find('tbody').eq(0)
        var rows = tbody.find('tr').toArray().sort(comparer($(this).index()))
        this.asc = !this.asc
        if (!this.asc) {
            rows = rows.reverse()
        }
        for (let i = 0, j = 0; i < rows.length; i++) {
            tbody.append(rows[i])
            if (rows[i].style.display !== 'none')
                rows[i].style.backgroundColor = !!(j++ & 1) ? "rgba(0,0,0,0)" : "rgba(0,0,0,.05)"
        }
    })

    function comparer(index) {
        return function (a, b) {
            var valA = getCellValue(a, index), valB = getCellValue(b, index)
            return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
        }
    }

    function getCellValue(row, index) {
        return $(row).children('td').eq(index)[0].dataset.value
    }
});

// Tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip({boundary: 'window'})
})

// Color palette
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
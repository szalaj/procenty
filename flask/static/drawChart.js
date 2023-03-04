
var dane_wykres = fin_data['dane']['raty'];
var dane_wykres2 = fin_data['dane2']['raty'];

var parseDate = d3.timeParse("%Y-%m-%d");



dane_wykres.forEach(function (d) {
  d.dzien = parseDate(d.dzien)
  d.K_po = parseFloat(d.K_po)

});


dane_wykres2.forEach(function (d) {
  d.dzien = parseDate(d.dzien)
  d.K_po = parseFloat(d.K_po)

});

var width_docs = document.getElementById('wykres').clientWidth;

var margin = { top: 60, right: 30, bottom: 70, left: 80 },
  width = width_docs - margin.left - margin.right,
  height = 450 - margin.top - margin.bottom;

var svg = d3.select("#wykres")
  .append("svg")
  .attr("class", "svg-holder")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .attr("style", "border:1px solid black;")
  .style('background', "white")
  .append("g")
  .attr("transform",
    "translate(" + margin.left + "," + margin.top + ")");


var xscale = d3.scaleTime()
  .domain(d3.extent(dane_wykres, d => d.dzien))
  .range([0, width]);




var xAxis = svg.append("g")
  .attr("class", "xAxis")
  .attr("transform", "translate(0," + height + ")")

xAxis.call(d3.axisBottom(xscale).tickFormat(d3.timeFormat('%Y-%m-%d')))
  .selectAll("text")
  .attr("transform", "translate(-10,0)rotate(-45)")
  .style("text-anchor", "end")
  .style("font-size", "13px");



var grids = svg.append('g')
  .selectAll('line')
  .data(xscale.ticks())
  .enter().append('line')
  .attr('class', 'gridline')
  .attr('x1', d => xscale(d))
  .attr('x2', d => xscale(d))
  .attr('y1', 0)
  .attr('y2', height)
  .attr('stroke', 'black')



var maxYvalue = d3.max(dane_wykres, function (d) { return d.K_po });
var minYvalue = d3.min(dane_wykres, function (d) { return d.K_po });



var yscale = d3.scaleLinear()
  .domain([minYvalue, maxYvalue])
  .range([height, 0]);




formatMoney = function (d) { return d3.format(".0f")(d) + " zł"; }


svg.append("g")
  .attr("class", "yAxis")
  .call(d3.axisLeft(yscale).tickFormat(formatMoney))
  .style("font-size", "13px");








var kreska = svg.append("path")
  .datum(dane_wykres)
  .attr("class", "kreska")
  .attr("d", d3.line()
    .x(function (d) { return xscale(d.dzien) })
    .y(function (d) { return yscale(d.K_po) })
  )

  var kreska2 = svg.append("path")
  .datum(dane_wykres2)
  .attr("class", "kreska2")
  .attr("d", d3.line()
    .x(function (d) { return xscale(d.dzien) })
    .y(function (d) { return yscale(d.K_po) })
  )

  svg.append("line")
.attr("x1", xscale(data_zamrozenia))
.attr("y1", yscale(maxYvalue))
.attr("x2", xscale(data_zamrozenia))
.attr("y2", yscale(minYvalue))
.attr("stroke", "black")
.attr("stroke-width", 3)


svg.append("text")
  .attr("class", "text-tytul")
  .attr("x", 0)
  .attr("y", -24)
  .text("Kapitał do spłaty")



function resize() {
  width_docs = document.getElementById('wykres').clientWidth;

  d3.select('#wykres svg')
    .attr('width', width_docs)

  xscale.range([0, width_docs - margin.left - margin.right]);


  xAxis.call(d3.axisBottom(xscale).tickFormat(d3.timeFormat('%Y-%m-%d')))

  grids.attr("x1", function (d) { return xscale(d) })
  grids.attr("x2", function (d) { return xscale(d) })

  kreska.attr("d", d3.line()
    .x(function (d) { return xscale(d.dzien) })
    .y(function (d) { return yscale(d.K_po) })
  )

  kreska2.attr("d", d3.line()
    .x(function (d) { return xscale(d.dzien) })
    .y(function (d) { return yscale(d.K_po) })
  )

}

window.addEventListener('resize', resize);
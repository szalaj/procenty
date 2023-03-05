
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

var width_docs = document.getElementById('wykres_kapital').clientWidth;

var margin = { top: 60, right: 30, bottom: 70, left: 80 },
  width = width_docs - margin.left - margin.right,
  height = 450 - margin.top - margin.bottom;

var svg = d3.select("#wykres_kapital")
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






var svg2 = d3.select("#wykres_raty")
  .append("svg")
  .attr("class", "svg-holder")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .attr("style", "border:1px solid black;")
  .style('background', "white")
  .append("g")
  .attr("transform",
    "translate(" + margin.left + "," + margin.top + ")");


    var xAxis3 = svg2.append("g")
  .attr("class", "xAxis")
  .attr("transform", "translate(0," + height + ")")

xAxis3.call(d3.axisBottom(xscale).tickFormat(d3.timeFormat('%Y-%m-%d')))
  .selectAll("text")
  .attr("transform", "translate(-10,0)rotate(-45)")
  .style("text-anchor", "end")
  .style("font-size", "13px");

  var grids2 = svg2.append('g')
  .selectAll('line')
  .data(xscale.ticks())
  .enter().append('line')
  .attr('class', 'gridline')
  .attr('x1', d => xscale(d))
  .attr('x2', d => xscale(d))
  .attr('y1', 0)
  .attr('y2', height)
  .attr('stroke', 'black')
  

    var maxYvalue2 = d3.max(dane_wykres, function (d) { return d.rata });
    var minYvalue2 = d3.min(dane_wykres, function (d) { return d.rata });
    
    
    
    var yscale2 = d3.scaleLinear()
      .domain([0, maxYvalue2])
      .range([height, 0]);
    


      svg2.append("g")
      .attr("class", "yAxis")
      .call(d3.axisLeft(yscale2).tickFormat(formatMoney))
      .style("font-size", "13px");

    // var mybars = svg2.selectAll(".mybar").data(dane_wykres)

    // mybars
    //   .enter()
    //   .append("circle")
    //   .attr("cx", function (d) { return xscale(d.dzien); })
    //   .attr("cy", function (d) { return yscale2(d.rata); })
    //   .attr("r", 2)
    //   .attr("class", "mybar");


      var kreska3 = svg2.append("path")
      .datum(dane_wykres)
      .attr("class", "kreska")
      .attr("d", d3.line()
        .x(function (d) { return xscale(d.dzien) })
        .y(function (d) { return yscale2(d.rata) })
      )


      
  var kreska4 = svg2.append("path")
  .datum(dane_wykres2)
  .attr("class", "kreska2")
  .attr("d", d3.line()
    .x(function (d) { return xscale(d.dzien) })
    .y(function (d) { return yscale2(d.rata) })
  )


  
svg2.append("text")
.attr("class", "text-tytul")
.attr("x", 0)
.attr("y", -24)
.text("Raty")



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
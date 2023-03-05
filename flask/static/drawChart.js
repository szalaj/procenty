
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

var svg_kapital = d3.select("#wykres_kapital")
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




var xAxis = svg_kapital.append("g")
  .attr("class", "xAxis")
  .attr("transform", "translate(0," + height + ")")

xAxis.call(d3.axisBottom(xscale).tickFormat(d3.timeFormat('%Y-%m-%d')))
  .selectAll("text")
  .attr("transform", "translate(-10,0)rotate(-45)")
  .style("text-anchor", "end")
  .style("font-size", "13px");



var grids_kapital = svg_kapital.append('g')
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



var yscale_kapital = d3.scaleLinear()
  .domain([minYvalue, maxYvalue])
  .range([height, 0]);




formatMoney = function (d) { return d3.format(".0f")(d) + " zł"; }


svg_kapital.append("g")
  .attr("class", "yAxis")
  .call(d3.axisLeft(yscale_kapital).tickFormat(formatMoney))
  .style("font-size", "13px");








var kreska_kapital_real = svg_kapital.append("path")
  .datum(dane_wykres)
  .attr("class", "kreska")
  .attr("d", d3.line()
    .x(function (d) { return xscale(d.dzien) })
    .y(function (d) { return yscale_kapital(d.K_po) })
  )

  var kreska_kapital_zamr = svg_kapital.append("path")
  .datum(dane_wykres2)
  .attr("class", "kreska2")
  .attr("d", d3.line()
    .x(function (d) { return xscale(d.dzien) })
    .y(function (d) { return yscale_kapital(d.K_po) })
  )

  svg_kapital.append("line")
.attr("x1", xscale(data_zamrozenia))
.attr("y1", yscale_kapital(maxYvalue))
.attr("x2", xscale(data_zamrozenia))
.attr("y2", yscale_kapital(minYvalue))
.attr("stroke", "black")
.attr("stroke-width", 3)


svg_kapital.append("text")
  .attr("class", "text-tytul")
  .attr("x", 0)
  .attr("y", -24)
  .text("Kapitał do spłaty")






var svg_raty = d3.select("#wykres_raty")
  .append("svg")
  .attr("class", "svg-holder")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .attr("style", "border:1px solid black;")
  .style('background', "white")
  .append("g")
  .attr("transform",
    "translate(" + margin.left + "," + margin.top + ")");


    var xAxis_raty = svg_raty.append("g")
  .attr("class", "xAxis")
  .attr("transform", "translate(0," + height + ")")

  xAxis_raty.call(d3.axisBottom(xscale).tickFormat(d3.timeFormat('%Y-%m-%d')))
    .selectAll("text")
    .attr("transform", "translate(-10,0)rotate(-45)")
    .style("text-anchor", "end")
    .style("font-size", "13px");

  var grids_raty = svg_raty.append('g')
  .selectAll('line')
  .data(xscale.ticks())
  .enter().append('line')
  .attr('class', 'gridline')
  .attr('x1', d => xscale(d))
  .attr('x2', d => xscale(d))
  .attr('y1', 0)
  .attr('y2', height)
  .attr('stroke', 'black')
  

    var maxYvalue_raty = d3.max(dane_wykres, function (d) { return d.rata });
    
    
    
    
    var yscale_raty = d3.scaleLinear()
      .domain([0, maxYvalue_raty])
      .range([height, 0]);
    


      svg_raty.append("g")
      .attr("class", "yAxis")
      .call(d3.axisLeft(yscale_raty).tickFormat(formatMoney))
      .style("font-size", "13px");

    // var mybars = svg_raty.selectAll(".mybar").data(dane_wykres)

    // mybars
    //   .enter()
    //   .append("circle")
    //   .attr("cx", function (d) { return xscale(d.dzien); })
    //   .attr("cy", function (d) { return yscale_raty(d.rata); })
    //   .attr("r", 2)
    //   .attr("class", "mybar");


      var kreska_raty_real = svg_raty.append("path")
      .datum(dane_wykres)
      .attr("class", "kreska")
      .attr("d", d3.line()
        .x(function (d) { return xscale(d.dzien) })
        .y(function (d) { return yscale_raty(d.rata) })
      )


      
  var kreska_raty_zamr = svg_raty.append("path")
  .datum(dane_wykres2)
  .attr("class", "kreska2")
  .attr("d", d3.line()
    .x(function (d) { return xscale(d.dzien) })
    .y(function (d) { return yscale_raty(d.rata) })
  )


  
svg_raty.append("text")
.attr("class", "text-tytul")
.attr("x", 0)
.attr("y", -24)
.text("Raty")



    function resize() {
      width_docs = document.getElementById('wykres_kapital').clientWidth;
    
      d3.select('#wykres_kapital svg')
        .attr('width', width_docs)

        d3.select('#wykres_raty svg')
        .attr('width', width_docs)
    
      xscale.range([0, width_docs - margin.left - margin.right]);
    
    
      xAxis.call(d3.axisBottom(xscale).tickFormat(d3.timeFormat('%Y-%m-%d')))
    
      grids_kapital.attr("x1", function (d) { return xscale(d) })
      grids_kapital.attr("x2", function (d) { return xscale(d) })

      grids_raty.attr("x1", function (d) { return xscale(d) })
      grids_raty.attr("x2", function (d) { return xscale(d) })
    
      kreska_kapital_real.attr("d", d3.line()
        .x(function (d) { return xscale(d.dzien) })
        .y(function (d) { return yscale_kapital(d.K_po) })
      )
    
      kreska_kapital_zamr.attr("d", d3.line()
        .x(function (d) { return xscale(d.dzien) })
        .y(function (d) { return yscale_kapital(d.K_po) })
      )

          
      kreska_raty_real.attr("d", d3.line()
        .x(function (d) { return xscale(d.dzien) })
        .y(function (d) { return yscale_raty(d.rata) })
      )
    
      kreska_raty_zamr.attr("d", d3.line()
        .x(function (d) { return xscale(d.dzien) })
        .y(function (d) { return yscale_raty(d.rata) })
      )
    
    }
    
    window.addEventListener('resize', resize);
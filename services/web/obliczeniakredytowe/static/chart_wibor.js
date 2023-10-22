function create_chart_wibor(margin, width, height, wibor, oprocentowanie)
{

  var parseDateWibor = d3.timeParse("%Y-%m-%d");
  
  wibor.forEach(function (d) {
    d.dzien = parseDateWibor(d.date)
    d.wartosc = parseFloat(d.value)
  });

  oprocentowanie.forEach(function (d) {
    d.dzien = parseDateWibor(d.dzien)
    d.wartosc = parseFloat(d.proc)
  });


// Position the div element above the SVG container
var svgwibor = d3.select('#ryswibor')
  .append("svg")
  .attr("class", "svg-holder")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .attr("style", "border:1px solid black;")
  .style('background', "white")
  .append("g")
  .attr("transform",
    "translate(" + margin.left + "," + margin.top + ")");

var xscalewibor = d3.scaleTime()
    .domain(d3.extent(wibor, d => d.dzien))
    .range([0, width]);


var xAxisWibor = svgwibor.append("g")
    .attr("class", "xAxis")
    .attr("transform", "translate(0," + height + ")")

xAxisWibor.call(d3.axisBottom(xscalewibor).tickFormat(d3.timeFormat('%Y-%m')))
  .selectAll("text")
  .attr("transform", "translate(-10,0)rotate(-45)")
  .style("text-anchor", "end")
  .style("font-size", "13px");

var gridswibor = svgwibor.append('g')
    .selectAll('line')
    .data(xscalewibor.ticks())
    .enter().append('line')
    .attr('class', 'gridline')
    .attr('x1', d => xscalewibor(d))
    .attr('x2', d => xscalewibor(d))
    .attr('y1', 0)
    .attr('y2', height)



var maxYvalueW = d3.max(wibor.concat(oprocentowanie), function (d) { return d.wartosc });
var minYvalueW = d3.min(wibor.concat(oprocentowanie), function (d) { return d.wartosc });

var yscalewibor = d3.scaleLinear()
  .domain([minYvalueW, maxYvalueW])
  .range([height, 0]);

  svgwibor.append('g')
  .selectAll('line')
  .data(yscalewibor.ticks())
  .enter().append('line')
  .attr('class', 'gridline')
  .attr('x1', 0)
  .attr('x2', width)
  .attr('y1', d=>yscalewibor(d))
  .attr('y2', d=>yscalewibor(d))

  svgwibor.append("g")
  .attr("class", "yAxis")
  .call(d3.axisLeft(yscalewibor))
  .style("font-size", "13px");


  svgwibor.append("path")
  .datum(wibor)
  .attr("class", "kreska")
  .attr("d", d3.line()
    .x(function (d) { return xscalewibor(d.dzien) })
    .y(function (d) { return yscalewibor(d.wartosc) })
  )



  svgwibor.append("path")
  .datum(oprocentowanie)
  .attr("class", "kreska-czerwona")
  .attr("d", d3.line()
    .x(function (d) { return xscalewibor(d.dzien) })
    .y(function (d) { return yscalewibor(d.wartosc) })
  )








}

export { create_chart_wibor };
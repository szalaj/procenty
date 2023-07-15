function create_chart_nadplaty(margin, width, height, nadplaty)
{


    var parseDateWibor = d3.timeParse("%Y-%m-%d");

  
    nadplaty.forEach(function (d) {
      d.dzien = parseDateWibor(d.dzien)
      d.kwota = parseFloat(d.kwota)
    });
// Position the div element above the SVG container
var svgnadplaty = d3.select("#rysNadplaty")
  .append("svg")
  .attr("class", "svg-holder")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .attr("style", "border:1px solid black;")
  .style('background', "white")
  .append("g")
  .attr("transform",
    "translate(" + margin.left + "," + margin.top + ")");

var xscalenadplaty = d3.scaleTime()
    .domain(d3.extent(nadplaty, d => d.dzien))
    .range([0, width]);


var xAxisnadplaty= svgnadplaty.append("g")
    .attr("class", "xAxis")
    .attr("transform", "translate(0," + height + ")")

xAxisnadplaty.call(d3.axisBottom(xscalenadplaty).tickFormat(d3.timeFormat('%Y-%m')))
  .selectAll("text")
  .attr("transform", "translate(-10,0)rotate(-45)")
  .style("text-anchor", "end")
  .style("font-size", "13px");

var gridsnadplaty = svgnadplaty.append('g')
    .selectAll('line')
    .data(xscalenadplaty.ticks())
    .enter().append('line')
    .attr('class', 'gridline')
    .attr('x1', d => xscalenadplaty(d))
    .attr('x2', d => xscalenadplaty(d))
    .attr('y1', 0)
    .attr('y2', height)


var maxYvalueI = d3.max(nadplaty, function (d) { return d.kwota });

var yscalenadplaty = d3.scaleLinear()
  .domain([0, maxYvalueI])
  .range([height, 0]);

  var gridsHnadplaty = svgnadplaty.append('g')
  .selectAll('line')
  .data(yscalenadplaty.ticks())
  .enter().append('line')
  .attr('class', 'gridline')
  .attr('x1', 0)
  .attr('x2', width)
  .attr('y1', d=>yscalenadplaty(d))
  .attr('y2', d=>yscalenadplaty(d))

  var formatMoney = function (d) { return d3.format(".0f")(d) + " zł"; }
  
  
  svgnadplaty.append("g")
  .attr("class", "yAxis")
  .call(d3.axisLeft(yscalenadplaty).tickFormat(formatMoney))
  .style("font-size", "13px");



 
  svgnadplaty.selectAll("circle nadplata")
  .data(nadplaty)
  .enter()
  .append("circle")
  .attr("class", "nadplata")
  .attr("cx", d => xscalenadplaty(d.dzien))
  .attr("cy", d => yscalenadplaty(d.kwota))
  .attr("r", "3");


  







}

export { create_chart_nadplaty };
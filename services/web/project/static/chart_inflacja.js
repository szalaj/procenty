function create_chart_inflacja(margin, width, height, inflacja)
{


    var parseDateWibor = d3.timeParse("%Y-%m-%d");

  
    inflacja.forEach(function (d) {
      d.miesiac = parseDateWibor(d.date)
      d.wartosc = parseFloat(d.value)
    });
// Position the div element above the SVG container
var svginflacja = d3.select("#rysInflacja")
  .append("svg")
  .attr("class", "svg-holder")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .attr("style", "border:1px solid black;")
  .style('background', "white")
  .append("g")
  .attr("transform",
    "translate(" + margin.left + "," + margin.top + ")");

var xscaleinflacja = d3.scaleTime()
    .domain(d3.extent(inflacja, d => d.miesiac))
    .range([0, width]);


var xAxisInflacja= svginflacja.append("g")
    .attr("class", "xAxis")
    .attr("transform", "translate(0," + height + ")")

xAxisInflacja.call(d3.axisBottom(xscaleinflacja).tickFormat(d3.timeFormat('%Y-%m')))
  .selectAll("text")
  .attr("transform", "translate(-10,0)rotate(-45)")
  .style("text-anchor", "end")
  .style("font-size", "13px");

var gridsinflacja = svginflacja.append('g')
    .selectAll('line')
    .data(xscaleinflacja.ticks())
    .enter().append('line')
    .attr('class', 'gridline')
    .attr('x1', d => xscaleinflacja(d))
    .attr('x2', d => xscaleinflacja(d))
    .attr('y1', 0)
    .attr('y2', height)


var maxYvalueI = d3.max(inflacja, function (d) { return d.wartosc });
var minYvalueI = d3.min(inflacja, function (d) { return d.wartosc });

var yscaleinflacja = d3.scaleLinear()
  .domain([minYvalueI, maxYvalueI])
  .range([height, 0]);

  var gridsHinflacja = svginflacja.append('g')
  .selectAll('line')
  .data(yscaleinflacja.ticks())
  .enter().append('line')
  .attr('class', 'gridline')
  .attr('x1', 0)
  .attr('x2', width)
  .attr('y1', d=>yscaleinflacja(d))
  .attr('y2', d=>yscaleinflacja(d))

  svginflacja.append("g")
  .attr("class", "yAxis")
  .call(d3.axisLeft(yscaleinflacja))
  .style("font-size", "13px");


  var kreska_inflacja= svginflacja.append("path")
  .datum(inflacja)
  .attr("class", "kreska")
  .attr("d", d3.line()
    .x(function (d) { return xscaleinflacja(d.miesiac) })
    .y(function (d) { return yscaleinflacja(d.wartosc) })
  )


  







}

export { create_chart_inflacja };
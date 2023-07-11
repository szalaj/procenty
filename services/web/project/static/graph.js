function create_graph(margin, width, height, values, real_raty, real_wartosc_nieruchomosc, parseDate)
{
    console.log('aha')

    var svg_real = d3.select("#wykres_real")
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
    .domain(d3.extent(values, d => d.miesiac))
    .range([0, width]);
  
  
  
  
  var xAxis = svg_real.append("g")
    .attr("class", "xAxis")
    .attr("transform", "translate(0," + height + ")")
  
  xAxis.call(d3.axisBottom(xscale).tickFormat(d3.timeFormat('%Y-%m-%d')))
    .selectAll("text")
    .attr("transform", "translate(-10,0)rotate(-45)")
    .style("text-anchor", "end")
    .style("font-size", "13px");
  
  
  
  var grids_real = svg_real.append('g')
    .selectAll('line')
    .data(xscale.ticks())
    .enter().append('line')
    .attr('class', 'gridline')
    .attr('x1', d => xscale(d))
    .attr('x2', d => xscale(d))
    .attr('y1', 0)
    .attr('y2', height)
    .attr('stroke', 'black')
  
  
  
  var maxYvalue = d3.max(real_raty, function (d) { return d.wartosc });
  
  

  
  var yscale_real = d3.scaleLinear()
    .domain([0, maxYvalue])
    .range([height, 0]);
  
  
  
  
  var formatMoney = function (d) { return d3.format(".0f")(d) + " zł"; }
  
  
  svg_real.append("g")
    .attr("class", "yAxis")
    .call(d3.axisLeft(yscale_real).tickFormat(formatMoney))
    .style("font-size", "13px");
  
  
  
var kreska_real = svg_real.selectAll("circle")
    .data(real_raty)
    .enter()
    .append("circle")
    .attr("cx", d => xscale(d.miesiac))
    .attr("cy", d => yscale_real(d.wartosc))
    .attr("r", "2");

  
  var maxYvalue = d3.max(values.map(a => a.cumsum).concat(real_wartosc_nieruchomosc.map(a=>a.wartosc)))*1.1;
 
  
  
  
  
  var yscale_real_cumsum = d3.scaleLinear()
    .domain([0, maxYvalue])
    .range([height, 0]);
  
  
  
  
  formatMoney = function (d) { return d3.format(".0f")(d) + " zł"; }
  
  
  svg_real.append("g")
    .attr("class", "yAxis")
    .call(d3.axisLeft(yscale_real_cumsum).tickFormat(formatMoney))
    .style("font-size", "13px")
    .attr("transform", "translate(" + width + ", 0)")
  
  
  
    var kreska_real_cumsum = svg_real.append("path")
    .datum(values)
    .attr("class", "blue")
    .attr("d", d3.line()
      .x(function (d) { return xscale(d.miesiac) })
      .y(function (d) { return yscale_real_cumsum(d.cumsum) })
    )
  
    real_wartosc_nieruchomosc.forEach(function (d) {
    d.miesiac = parseDate(d.miesiac)
    d.wartosc = parseFloat(d.wartosc)
  
    
  });
  
    var kreska_real_nier= svg_real.append("path")
    .datum(real_wartosc_nieruchomosc)
    .attr("class", "red")
    .attr("d", d3.line()
      .x(function (d) { return xscale(d.miesiac) })
      .y(function (d) { return yscale_real_cumsum(d.wartosc) })
    )
  

};

export { create_graph };
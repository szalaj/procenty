function create_chart_koszty(margin, width, height, real_koszty, nom_koszty, real_raty, nom_raty, real_wartosc_nieruchomosc, nom_wartosc_nieruchomosc)
{

  margin['top'] = 140;
  margin['bottom'] = 90;
  height = 1000 - margin.top - margin.bottom;


  var parseDate = d3.timeParse("%Y-%m");

  real_koszty.sort(function (x, y) {
    return d3.ascending(x.miesiac, y.miesiac);
  })

  nom_koszty.sort(function (x, y) {
    return d3.ascending(x.dzien, y.dzien);
  })

  var cumsum = 0;

  real_koszty.forEach(function (d) {
    d.miesiac = parseDate(d.miesiac)
    d.wartosc = parseFloat(d.wartosc)
    cumsum = cumsum + d.wartosc;
    d.cumsum = cumsum;

  });

  var cumsum_nom = 0
  nom_koszty.forEach(function (d) {
    d.miesiac = parseDate(d.dzien)
    d.wartosc = parseFloat(d.wartosc)
    cumsum_nom = cumsum_nom + d.wartosc;
    d.cumsum_nom = cumsum_nom;

  });






  real_raty.forEach(function (d) {
    d.miesiac = parseDate(d.miesiac)
    d.wartosc = parseFloat(d.wartosc)


  });

  nom_raty.forEach(function (d) {
    d.miesiac = parseDate(d.dzien)
    d.wartosc = parseFloat(d.wartosc)


  });
  console.log('raty')
  console.log(nom_raty)
  console.log(real_raty)
    

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
    .domain(d3.extent(real_koszty, d => d.miesiac))
    .range([0, width]);
  
  
  
  
  var xAxis = svg_real.append("g")
    .attr("class", "xAxis")
    .attr("transform", "translate(0," + height + ")")
  
  xAxis.call(d3.axisBottom(xscale).tickFormat(d3.timeFormat('%Y-%m-%d')))
    .selectAll("text")
    .attr("transform", "translate(-10,0)rotate(-45)")
    .style("text-anchor", "end")
    .style("font-size", "13px");
  
  
  
  svg_real.append('g')
    .selectAll('line')
    .data(xscale.ticks())
    .enter().append('line')
    .attr('class', 'gridline')
    .attr('x1', d => xscale(d))
    .attr('x2', d => xscale(d))
    .attr('y1', 0)
    .attr('y2', height)
    .attr('stroke', 'black')
  
  
  
  var maxYvalue = d3.max(real_raty.map(a => a.wartosc).concat(nom_raty.map(a=>a.wartosc)))*1.1;
  

  var yscale_real = d3.scaleLinear()
    .domain([0, maxYvalue])
    .range([height, 0]);
  
  
  var formatMoney = function (d) { return d3.format(".0f")(d) + " zł"; }
  
  
  svg_real.append("g")
    .attr("class", "yAxis")
    .call(d3.axisLeft(yscale_real).tickFormat(formatMoney))
    .style("font-size", "13px");
  
  
  
    svg_real.selectAll("circle real")
    .data(real_raty)
    .enter()
    .append("circle")
    .attr("class", "real")
    .attr("cx", d => xscale(d.miesiac))
    .attr("cy", d => yscale_real(d.wartosc))
    .attr("r", "2");

    svg_real.selectAll("circle nom")
    .data(nom_raty)
    .enter()
    .append("circle")
    .attr("class", "nom")
    .attr("cx", d => xscale(d.miesiac))
    .attr("cy", d => yscale_real(d.wartosc))
    .attr("r", "2");

    // legend
    svg_real.append("circle").attr("class", "real")
    .attr("cx", "20")
    .attr("cy", "-120")
    .attr("r", "4");

    svg_real.append("text")
    .attr("x", "30")
    .attr("y", "-117")
    .text("- realna wysokość miesięcznej raty")

    svg_real.append("circle").attr("class", "nom")
    .attr("cx", "20")
    .attr("cy", "-100")
    .attr("r", "4");

    svg_real.append("text")
    .attr("x", "30")
    .attr("y", "-97")
    .text("- nominalna wysokość miesięcznej raty")

  
  var maxYvalue = d3.max(real_koszty.map(a => a.cumsum).concat(real_wartosc_nieruchomosc.map(a=>a.wartosc)).concat(nom_wartosc_nieruchomosc.map(a=>a.wartosc)))*1.1;
 
  
  var yscale_real_cumsum = d3.scaleLinear()
    .domain([0, maxYvalue])
    .range([height, 0]);
  
  
  
  
  formatMoney = function (d) { return d3.format(".0f")(d) + " zł"; }
  
  
  svg_real.append("g")
    .attr("class", "yAxis")
    .call(d3.axisLeft(yscale_real_cumsum).tickFormat(formatMoney))
    .style("font-size", "13px")
    .attr("transform", "translate(" + width + ", 0)")
  
  
  
  svg_real.append("path")
    .datum(real_koszty)
    .attr("class", "blue")
    .attr("d", d3.line()
      .x(function (d) { return xscale(d.miesiac) })
      .y(function (d) { return yscale_real_cumsum(d.cumsum) })
    )
  
    svg_real.append("path")
    .datum(nom_koszty)
    .attr("class", "blue-dot")
    .attr("d", d3.line()
      .x(function (d) { return xscale(d.miesiac) })
      .y(function (d) { return yscale_real_cumsum(d.cumsum_nom) })
    )

    //legend
    svg_real.append("line")
    .attr("class", "blue")
    .attr("x1", 15)
    .attr("y1", -80)
    .attr("x2", 25)
    .attr("y2", -80)

    svg_real.append("text")
    .attr("x", "30")
    .attr("y", "-77")
    .text("- realne całkowite koszty kredytu")

    svg_real.append("line")
    .attr("class", "blue-dot")
    .attr("x1", 10)
    .attr("y1", -60)
    .attr("x2", 25)
    .attr("y2", -60)

    svg_real.append("text")
    .attr("x", "30")
    .attr("y", "-57")
    .text("- nominalne całkowite koszty kredytu")

    svg_real.append("line")
    .attr("class", "red")
    .attr("x1", 15)
    .attr("y1", -40)
    .attr("x2", 25)
    .attr("y2", -40)

    svg_real.append("text")
    .attr("x", "30")
    .attr("y", "-37")
    .text("- realna wartość nieruchomości")

    svg_real.append("line")
    .attr("class", "red-dot")
    .attr("x1",10)
    .attr("y1", -20)
    .attr("x2", 25)
    .attr("y2", -20)

    svg_real.append("text")
    .attr("x", "30")
    .attr("y", "-17")
    .text("- nominalna wartość nieruchomości")

    real_wartosc_nieruchomosc.forEach(function (d) {
    d.miesiac = parseDate(d.miesiac)
    d.wartosc = parseFloat(d.wartosc)
  
    
  });

    nom_wartosc_nieruchomosc.forEach(function (d) {
    d.miesiac = parseDate(d.dzien)
    d.wartosc = parseFloat(d.wartosc)
  
    
  });

  console.log(nom_wartosc_nieruchomosc)
  
    svg_real.append("path")
    .datum(real_wartosc_nieruchomosc)
    .attr("class", "red")
    .attr("d", d3.line()
      .x(function (d) { return xscale(d.miesiac) })
      .y(function (d) { return yscale_real_cumsum(d.wartosc) })
    )

    svg_real.append("path")
    .datum(nom_wartosc_nieruchomosc)
    .attr("class", "red-dot")
    .attr("d", d3.line()
      .x(function (d) { return xscale(d.miesiac) })
      .y(function (d) { return yscale_real_cumsum(d.wartosc) })
    )
  

};

export { create_chart_koszty };
function create_chart_kapital(margin, width, height, nom_kpo, nom_cena_kosztowa, real_kpo, real_cena_kosztowa)
{

  margin['top'] = 120;
  margin['bottom'] = 80
  margin['left'] = 100;
  height = 720 - margin.top - margin.bottom;


  var parseDate = d3.timeParse("%Y-%m");

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
    .domain(d3.extent(nom_kpo, d => d.dzien))
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


  
    var maxYvalue = d3.max(nom_kpo.map(a => a.K_po).concat(real_kpo.map(a=>a.K_po)).concat(nom_cena_kosztowa.map(a=>a.wartosc)))*1.1;
  


  var yscale_kapital = d3.scaleLinear()
    .domain([0, maxYvalue])
    .range([height, 0]);




  var formatMoney = function (d) { return d3.format(".0f")(d) + " zł"; }


  svg_kapital.append("g")
    .attr("class", "yAxis")
    .call(d3.axisLeft(yscale_kapital).tickFormat(formatMoney))
    .style("font-size", "13px");


  //kapil nominal
    svg_kapital.append("path")
    .datum(nom_kpo)
    .attr("class", "kreska-dot")
    .attr("d", d3.line()
      .x(function (d) { return xscale(d.dzien) })
      .y(function (d) { return yscale_kapital(d.K_po) })
    )

      //kapil nominal
      svg_kapital.append("path")
      .datum(nom_cena_kosztowa)
      .attr("class", "red-dot")
      .attr("d", d3.line()
        .x(function (d) { return xscale(d.miesiac) })
        .y(function (d) { return yscale_kapital(d.wartosc) })
      )

  //kapial real
    svg_kapital.append("path")
    .datum(real_kpo)
    .attr("class", "kreska")
    .attr("d", d3.line()
      .x(function (d) { return xscale(d.dzien) })
      .y(function (d) { return yscale_kapital(d.K_po) })
    )

      //kapial real
      svg_kapital.append("path")
      .datum(real_cena_kosztowa)
      .attr("class", "red")
      .attr("d", d3.line()
        .x(function (d) { return xscale(d.miesiac) })
        .y(function (d) { return yscale_kapital(d.wartosc) })
      )
    

      //legend
      svg_kapital.append("line")
      .attr("class", "kreska")
      .attr("x1", 15)
      .attr("y1", -100)
      .attr("x2", 25)
      .attr("y2", -100)
  
      svg_kapital.append("text")
      .attr("x", "30")
      .attr("y", "-97")
      .text("- realna wartość kapitału do spłaty")
  
      svg_kapital.append("line")
      .attr("class", "kreska-dot")
      .attr("x1", 5)
      .attr("y1", -80)
      .attr("x2", 20)
      .attr("y2", -80)
  
      svg_kapital.append("text")
      .attr("x", "30")
      .attr("y", "-77")
      .text("- nominalna wartość kapitału do spłaty")



      svg_kapital.append("line")
      .attr("class", "red")
      .attr("x1", 15)
      .attr("y1", -60)
      .attr("x2", 25)
      .attr("y2", -60)
  
      svg_kapital.append("text")
      .attr("x", "30")
      .attr("y", "-57")
      .text("- realna cena kosztowa")
  
      svg_kapital.append("line")
      .attr("class", "red-dot")
      .attr("x1", 5)
      .attr("y1", -40)
      .attr("x2", 20)
      .attr("y2", -40)
  
      svg_kapital.append("text")
      .attr("x", "30")
      .attr("y", "-37")
      .text("- nominalna cena kosztowa")






}

export { create_chart_kapital };
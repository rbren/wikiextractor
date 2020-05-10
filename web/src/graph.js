
var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 100 - margin.top - margin.bottom;

function draw(data) {
  const values = data.map(d => d.encoded[0]);
  const min = d3.min(values);
  const max = d3.max(values);

  var svg = d3.select("svg");
  svg.selectAll("*").remove();
  svg
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var x = d3.scaleLinear()
    .range([0, width])
    .domain(d3.extent(values));

  var y = d3.scaleLinear()
    .range([height, 0])
    .domain([0, 1]);

  svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x));

  svg.append("g")
      .attr("class", "y axis")
      .call(d3.axisLeft(y));

  var x = d3.scaleLinear()
    .domain([min - 1, max + 1])
    .range([ 0, width ]);
  var y = d3.scaleLinear()
    .domain([0, 1])
    .range([ height, 0]);

  var dragHandler = d3.drag()
      .on("drag", function(d) {
        const point = x.invert(d3.event.x);
        d.fixed = d.encoded = [point];
        d3.select(this)
          .attr("cx", d => x(d.encoded[0]))
          .style("fill", d => d.fixed ? 'red' : "#69b3a2")
      });

  var points = svg.append('g')
    .selectAll("circle")
    .data(data)
    .enter()
    .append("circle")
      .attr("cx", d => x(d.encoded[0]))
      .attr("cy", d => y(.5))
      .attr("r", 3)
      .style("fill", d => d.fixed ? 'red' : "#69b3a2")
      .on("mouseover", (d) => {
        $('.article-title').html(`<a href="https://en.wikipedia.org/?curid=${d.id}" target="_blank">${d.title}</a>`);
      })
  dragHandler(points);
}

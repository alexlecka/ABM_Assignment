var HistogramModule = function(bins, canvas_width, canvas_height) {
    // Create the tag:
    var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
    canvas_tag += "style='border:1px dotted'></canvas>";
    // Append it to #elements:
    var canvas = $(canvas_tag)[0];
    $("#elements").append(canvas);
    // Create the context and the drawing controller:
    var context = canvas.getContext("2d");

    // Prep the chart properties and series:
    var datasets = [{
        label: "Data",
        fillColor: "rgba(151,187,205,0.5)",
        strokeColor: "rgba(151,187,205,0.8)",
        highlightFill: "rgba(151,187,205,0.75)",
        highlightStroke: "rgba(151,187,205,1)",
        data: []
    }];

    // Add a zero value for each bin
    for (var i in bins)
        datasets[0].data.push(0);

    var data = {
        labels: bins,
        datasets: datasets
    };

    var options = {
        scaleBeginsAtZero: true
    };

    // Create the chart object
    var chart = new Chart(context, {type: 'bar', data: data, options: options});

   this.render = function(data) {
        datasets[0].data = data;
        chart.update();
    };

    this.reset = function() {
        chart.destroy();
        chart = new Chart(context, {type: 'bar', data: data, options: options});
    };
};

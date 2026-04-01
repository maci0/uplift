// Chart.js center text plugin for doughnut charts
(function() {
    Chart.pluginService.register({
        afterDraw: function (chart) {
            if (chart.config.options.elements && chart.config.options.elements.center) {
                var helpers = Chart.helpers;
                var centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
                var centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;

                var ctx = chart.chart.ctx;
                ctx.save();
                var fontSize = helpers.getValueOrDefault(chart.config.options.elements.center.fontSize, Chart.defaults.global.defaultFontSize);
                var fontStyle = helpers.getValueOrDefault(chart.config.options.elements.center.fontStyle, Chart.defaults.global.defaultFontStyle);
                var fontFamily = helpers.getValueOrDefault(chart.config.options.elements.center.fontFamily, Chart.defaults.global.defaultFontFamily);
                var font = helpers.fontString(fontSize, fontStyle, fontFamily);
                ctx.font = font;
                ctx.fillStyle = helpers.getValueOrDefault(chart.config.options.elements.center.fontColor, Chart.defaults.global.defaultFontColor);
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(chart.config.options.elements.center.text, centerX, centerY);
                ctx.restore();
            }
        }
    });
})();

function initCharts() {
    var charts = document.querySelectorAll(".tile-score-chart");
    charts.forEach(function(chart) {
        constructChart(chart);
    });
}

function constructChart(chartEl) {
    var percentage = parseFloat(chartEl.getAttribute("data-percentage")) || 0;
    var customColor;
    if (percentage < 40)
        customColor = "#db3279";
    else if (percentage < 80)
        customColor = "#e59728";
    else
        customColor = "#79db32";

    new Chart(chartEl, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [percentage, (100 - percentage)],
                backgroundColor: [customColor, "#e8eff8"]
            }]
        },
        options: {
            animation: { animateScale: false, animateRotate: false },
            tooltips: { enabled: false },
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1,
            legend: { display: false },
            elements: {
                center: {
                    text: percentage.toFixed(2) + "%",
                    fontColor: "#000",
                    fontFamily: "'Inter', sans-serif",
                    fontSize: 20,
                    fontStyle: 'normal'
                }
            }
        }
    });
}

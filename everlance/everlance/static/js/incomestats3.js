const renderChart3 = (data) => {
    var ctx = document.getElementById("myChart3").getContext("2d");
    const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];
    
    var myChart = new Chart(ctx, {
        type: "line",
        data: {
        labels: monthLabels,
        datasets: [
            {
            label: 'This year',
            data: data, 
            backgroundColor: [
                'rgb(254, 99, 130)'
            ],
            borderColor: [
                'rgb(254, 99, 130)'
            ],
            borderWidth: 1,
            },
        ],
        },
        options: {
        legend: { // Add legend configuration
            display: true, // Hide legend (optional)
            text:'This year'
        },
        scales: { // Access scale configurations
            xAxes: [{ // Configure x-axis (horizontal bars)
            ticks: {
                // fontColor: 'rgb(0, 0, 255)' // Set x-axis label color
            }
            }],
            yAxes: [{ // Configure y-axis (categories)
            ticks: {
                // color: 'rgb(255, 255, 255)' // Set y-axis label color
            }
            }]
        }
        },
    });
    };
    
    
    const getChartData3 = () => {
    fetch("/income/income_yearwise_summary")
        .then((res) => res.json())
        .then((results) => {
        console.log("results", results);
        const monthwise_data = results;
        const [labels, data] = [
            Object.keys(monthwise_data),
            Object.values(monthwise_data),
        ];
        renderChart3(data);
        });
    };
    
    window.onload = getChartData3();
    
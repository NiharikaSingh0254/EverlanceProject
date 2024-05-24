const renderChart2 = (data) => {
    var ctx = document.getElementById("myChart2").getContext("2d");
    const weekLabels = ['Mon','Tues','Wed','Thurs','Fri','Sat','Sun']
    
    var myChart = new Chart(ctx, {
        type: "line",
        data: {
        labels: weekLabels,
        datasets: [
            {
            label: 'This week',
            data: data, 
            backgroundColor: [
                'rgb(24, 189, 156)'
            ],
            borderColor: [
                'rgb(24, 189, 156)'
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
    
    
    const getChartData2 = () => {
    fetch("/expense_weekwise_summary")
        .then((res) => res.json())
        .then((results) => {
        console.log("results", results);
        const weekwise_data = results;
        const [labels, data] = [
            Object.keys(weekwise_data),
            Object.values(weekwise_data),
        ];
        renderChart2(data);
        });
    };
    
    window.onload = getChartData2();
    
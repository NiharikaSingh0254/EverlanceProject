const generateRandomColor = () => {
    return `rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, 0.2)`;
  };
  const renderChart = (data, labels) => {
    var ctx = document.getElementById("myChart").getContext("2d");
  
    // Sort data and labels together based on data values (descending order)
    const sortedData = data.slice().sort((a, b) => b - a); // Sort data in descending order
    const sortedLabels = labels.slice(); // Create a copy of labels
    for (let i = 0; i < labels.length; i++) {
      const dataIndex = data.indexOf(sortedData[i]); // Find index of current data value in original data
      sortedLabels[i] = labels[dataIndex]; // Update labels based on sorted data indices
    }
  
    var myChart = new Chart(ctx, {
      type: "horizontalBar",
      data: {
        labels: sortedLabels.slice(0, 5),
        datasets: [
          {
            label: ' ',
            data: sortedData.slice(0, 5), // Use the sorted data
            backgroundColor: [
              'rgba(255, 99, 132, 0.7)', // Light Coral
              'rgba(54, 162, 235, 0.7)', // Light Blue
              'rgba(255, 205, 86, 0.7)', // Light Yellow
              'rgba(75, 192, 192, 0.7)', // Light Sea Green
              'rgba(153, 102, 255, 0.7)', // Light Purple
              'rgba(255, 159, 64, 0.7)', // Orange
              'rgba(34, 139, 34, 0.7)', // Forest Green
              'rgba(205, 80, 80, 0.7)', // Salmon
              'rgba(0, 128, 128, 0.7)', // Teal
              'rgba(128, 0, 128, 0.7)', // Purple
              'rgba(255, 192, 203, 0.7)', // Pink
              'rgba(144, 238, 144, 0.7)', // Light Green
              'rgba(238, 149, 114, 0.7)', // Light Coral
            ],
            borderColor: [
              'rgba(255, 99, 132, 0.7)', // Light Coral
              'rgba(54, 162, 235, 0.7)', // Light Blue
              'rgba(255, 205, 86, 0.7)', // Light Yellow
              'rgba(75, 192, 192, 0.7)', // Light Sea Green
              'rgba(153, 102, 255, 0.7)', // Light Purple
              'rgba(255, 159, 64, 0.7)', // Orange
              'rgba(34, 139, 34, 0.7)', // Forest Green
              'rgba(205, 80, 80, 0.7)', // Salmon
              'rgba(0, 128, 128, 0.7)', // Teal
              'rgba(128, 0, 128, 0.7)', // Purple
              'rgba(255, 192, 203, 0.7)', // Pink
              'rgba(144, 238, 144, 0.7)', // Light Green
              'rgba(238, 149, 114, 0.7)', // Light Coral
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        legend: { // Add legend configuration
          display: false, // Hide legend (optional)
        },
        scales: { // Access scale configurations
          xAxes: [{ // Configure x-axis (horizontal bars)
            ticks: {
              color: 'rgb(0, 0, 255)' // Set x-axis label color
            }
          }],
          yAxes: [{ // Configure y-axis (categories)
            ticks: {
              color: 'rgb(255, 255, 255)' // Set y-axis label color
            }
          }]
        }
      },
    });
  };
  
  
  const getChartData = () => {
    console.log("fetching");
    fetch("/income/income_sources_data")
      .then((res) => res.json())
      .then((results) => {
        console.log("results", results);
        const source_data = results.income_source_data;
        const [labels, data] = [
          Object.keys(source_data),
          Object.values(source_data),
        ];
  
        renderChart(data, labels);
      });
  };
  
  window.onload = getChartData();
  
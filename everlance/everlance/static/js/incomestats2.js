const getHumanMonth = (m) => {
    const [_, month, __] = new Date(new Date().getFullYear(), m - 1, 1)
      .toDateString()
      .split(" ");
    return month;
};
  
const updateThisMonthUI = (data = {}, type = "income") => {
    const currentMonth = new Date().toISOString().slice(0, 7); // Get current month in yyyy-mm format
    console.log("Current month:", currentMonth);
    console.log("Data object:");
    console.log(data);

    // Check if the current month's data is present in the API response
    if (data && data.monthwise_income_data && data.monthwise_income_data[currentMonth]) {
    const currentMonthData = data.monthwise_income_data[currentMonth];
    console.log("Current month data:", currentMonthData);
    const monthTotal = currentMonthData.reduce((total, item) => total + item.amount, 0);
    console.log("Total income for the current month:", monthTotal);
    const monthClass = type === "expenses" ? ".expense-this-month" : ".income-this-month";
    const valueClass = type === "expenses" ? ".expense-this-month-value" : ".income-this-month-value";
    document.querySelector(monthClass).textContent = getHumanMonth(currentMonth);
    document.querySelector(valueClass).textContent = monthTotal;
    } else {
    console.error("No data found for the current month:", currentMonth);
    }
};

  
const formatStats = (data = {}) => {
    console.log("Income Monthwise Data:", data.monthwise_income_data);

    // Check if the data object contains the necessary property
    if (!data || !data.months || !data.monthwise_income_data) {
    console.error("No income month-wise data available");
    return;
    }

    // Extract month-wise income data
    const monthWiseIncomeData = data.monthwise_income_data;

    // Process each month's income data
    Object.entries(monthWiseIncomeData).forEach(([month, incomeArray]) => {
    const totalIncome = incomeArray.reduce((acc, income) => acc + income.amount, 0);
    updateThisMonthUI({ [month]: totalIncome }, "income");
    });

    // Update top month UI (assuming you don't need top month for income data, remove this line)
    // updateTopMonthsUI(data.topMonth, type);
};

const getMonthName = (monthNumber) => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];
    return months[monthNumber - 1];
};

const setGraphs = (incomeData) => { // Only income data as argument
    try {
        if ( !incomeData || !incomeData.months || !incomeData.monthwise_income_data) {
          console.error("Data is missing or incomplete for graph generation.");
          return;
        }
    
        // Get unique years from income data
        const incomeYears = [...new Set(incomeData.months.map(month => month.split('-')[0]))];
    
        // Get month names (for X-axis labels)
        const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];
    
        // Prepare data structure for datasets by year
        const datasets = {};
    
        const generateRandomColor = () => {
          return `rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, 0.2)`;
        };
    
        // Populate datasets with income data by year (similar logic)
        incomeYears.forEach(year => {
          datasets[year] = { // Create dataset for each year in income data
            label: year,
            data: new Array(12).fill(0), // Initialize with zeros for all months
            backgroundColor: generateRandomColor(),
            borderColor: generateRandomColor().replace("0.2", "1"),
            borderWidth: 1
          };
      
          incomeData.months.forEach((month, index) => {
            const [currentYear, monthNumber] = month.split('-');
            if (currentYear === year) {
              datasets[year].data[parseInt(monthNumber) - 1] = incomeData.monthwise_income_data[month]
                ? incomeData.monthwise_income_data[month].reduce((acc, income) => acc + income.amount, 0)
                : 0;
            }
          });
        });
    
        // Update the charts
        const updateCharts = (ctx, type, labels) => {
          const chartData = {
            labels,
            datasets: Object.values(datasets) // Convert object to array for Chart.js
          };
    
          new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
              scales: {
                x: {
                  title: {
                    display: true,
                    text: 'Month'
                  }
                },
                y: {
                  beginAtZero: true
                }
              },
              plugins: {
                legend: {
                  display: true
                }
              }
            }
          });
        };
    
        // Update income chart
        const ctxIncome = document.getElementById('incomeChart').getContext('2d');
        updateCharts(ctxIncome, 'income', monthLabels);
    
    } catch (error) {
        console.error("Error setting graphs:", error);
    }
};
    
    

const fetchData = () => {
    const incomePromise = fetch("/income/income_summary_rest")
      .then((res) => res.json())
      .catch((e) => {
        console.error("Error fetching income summary data:", e);
        throw e; // Re-throw the error for further handling
      });
  
    // Use the correct Promise constructor
    incomePromise.then((incomeData) => {
      console.log("Income Summary Data:", incomeData);
      setGraphs(incomeData);
    })
    .catch((errs) => console.error("Error fetching data:", errs));
};
  
window.onload = () => fetchData();
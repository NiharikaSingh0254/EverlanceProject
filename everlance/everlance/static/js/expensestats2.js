const getHumanMonth = (m) => {
    const [_, month, __] = new Date(new Date().getFullYear(), m - 1, 1)
      .toDateString()
      .split(" ");
    return month;
  };
  
  const updateTopMonthsUI = (topMonth, type) => {
    console.log("topMonth:", topMonth);
    const monthKey = Object.keys(topMonth)[0];
    const monthValue = Object.values(topMonth)[0];
    if (monthKey && monthValue) {
      const humanMonth = getHumanMonth(monthKey);
      const monthClass = type === "expenses" ? ".expense-top-month" : ".income-top-month";
      const valueClass = type === "expenses" ? ".expense-top-month-value" : ".income-top-month-value";
      document.querySelector(monthClass).textContent = humanMonth;
      document.querySelector(valueClass).textContent = monthValue;
    } else {
      console.error("No top month data available for:", type);
    }
  };
  
  const updateThisMonthUI = (data = {}, type = "expenses") => {
    const currentMonth = new Date().toISOString().slice(0, 7); // Get current month in yyyy-mm format
    console.log("Current month:", currentMonth);
    console.log("Data object:");
    console.log(data);
  
    // Check if the current month's data is present in the API response
    if (data && data.monthwise_expense_data && data.monthwise_expense_data[currentMonth]) {
      const currentMonthData = data.monthwise_expense_data[currentMonth];
      console.log("Current month data:", currentMonthData);
      const monthTotal = currentMonthData.reduce((total, item) => total + item.amount, 0);
      console.log("Total expense for the current month:", monthTotal);
      const monthClass = type === "expenses" ? ".expense-this-month" : ".income-this-month";
      const valueClass = type === "expenses" ? ".expense-this-month-value" : ".income-this-month-value";
      document.querySelector(monthClass).textContent = getHumanMonth(currentMonth);
      document.querySelector(valueClass).textContent = monthTotal;
    } else {
      console.error("No data found for the current month:", currentMonth);
    }
  };
  
  
  const formatStats = (data = {}, type = "expenses") => {
    console.log("Expense Monthwise Data:", data.monthwise_expense_data);
  
    // Check if the data object contains the necessary properties
    if (!data || !data.months || !data.monthwise_expense_data) {
      console.error("No month-wise data available");
      return;
    }
  
    // Extract month-wise expense data
    const monthWiseExpenseData = data.monthwise_expense_data;
  
    // Process each month's expense data
    Object.entries(monthWiseExpenseData).forEach(([month, expenses]) => {
      const totalAmount = expenses.reduce((acc, expense) => acc + expense.amount, 0);
      updateThisMonthUI({ [month]: totalAmount }, type);
    });
  
    // Update top month UI
    updateTopMonthsUI(data.topMonth, type);
  };
  
  const getMonthName = (monthNumber) => {
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    return months[monthNumber - 1];
  };
  
  const setGraphs = (expenseData) => {
    try {
      if (!expenseData || !expenseData.months ||
        !expenseData.monthwise_expense_data ) {
        console.error("Data is missing or incomplete for graph generation.");
        return;
      }
  
      // Get unique years from expense and income data
      const expenseYears = [...new Set(expenseData.months.map(month => month.split('-')[0]))];
  
      // Get month names (for X-axis labels)
      const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'];
  
      // Prepare data structure for datasets by year
      const datasets = {};
  
      const generateRandomColor = () => {
        return `rgba(${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, ${Math.floor(Math.random() * 256)}, 0.2)`;
      };
  
      // Populate datasets with expense data by year
      expenseYears.forEach(year => {
        datasets[year] = {
          label: year,
          // Initialize data with zeros for all 12 months
          data: new Array(12).fill(0), 
          backgroundColor: generateRandomColor(), // Assign a random color for each year
          borderColor: generateRandomColor().replace("0.2", "1"), // Darker border
          borderWidth: 1
        };
  
        expenseData.months.forEach((month, index) => {
          const [currentYear, monthNumber] = month.split('-');
          if (currentYear === year) {
            // Calculate total expense for the month (or set to 0 if no data)
            datasets[year].data[parseInt(monthNumber) - 1] = expenseData.monthwise_expense_data[month]
              ? expenseData.monthwise_expense_data[month].reduce((acc, expense) => acc + expense.amount, 0)
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
  
      // Update expense chart
      const ctxExpense = document.getElementById('expenseChart').getContext('2d');
      updateCharts(ctxExpense, 'expense', monthLabels);
  
    } catch (error) {
      console.error("Error setting graphs:", error);
    }
  };
  
  const fetchData = () => {
    const expensePromise = fetch("/expense_summary_rest")
      .then((res) => res.json())
      .catch((e) => {
        console.error("Error fetching expense summary data:", e);
        throw e; // Re-throw the error for further handling
      });
  
    // Use the correct Promise constructor
    expensePromise.then((expenseData) => {
      console.log("Expense Summary Data:", expenseData);
      setGraphs(expenseData);
    })
    .catch((errs) => console.error("Error fetching data:", errs));
  };
  window.onload = () => fetchData();
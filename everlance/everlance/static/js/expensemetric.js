const getMetricData = () => {
    console.log("hello")
    //expenses
    fetch("/metric_card_view")
        .then((res) => res.json())
        .then((results) => {
            console.log("metricresults", results);
            const expenses_by_day = results.daily_expenses;
            const expenses_by_week = results.weekly_expenses;
            const expenses_by_month = results.monthly_expenses;
            const expenses_by_year = results.yearly_expenses;
            document.getElementById('daily').innerHTML = expenses_by_day;
            document.getElementById('weekly').innerHTML = expenses_by_week;
            document.getElementById('monthly').innerHTML = expenses_by_month;
            document.getElementById('yearly').innerHTML = expenses_by_year;
        })
        .catch((error) => {
            console.error('Error fetching the metric data:', error);
        });

    fetch("/metric_card_view2")
    .then((res) => res.json())
    .then((results) => {
        console.log("results", results);
        const total_expenses_by_day = results.total_daily_expenses;
        const total_expenses_by_week = results.total_weekly_expenses;
        const total_expenses_by_month = results.monthly_totals;
        const total_expenses_by_year = results.total_yearly_expenses;
        document.getElementById('totaldaily').innerHTML = total_expenses_by_day;
        document.getElementById('totalweekly').innerHTML = total_expenses_by_week;
        document.getElementById('totalmonthly').innerHTML = total_expenses_by_month;
        document.getElementById('totalyearly').innerHTML = total_expenses_by_year;
    })
    .catch((error) => {
        console.error('Error fetching the metric data:', error);
    });
};
window.onload = getMetricData();  
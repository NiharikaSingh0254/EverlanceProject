const getMetricData2 = () => {

    //income
    fetch("/income/metric_card_view_income")
        .then((res) => res.json())
        .then((results) => {
            console.log("results", results);
            const incomes_by_day = results.daily_incomes;
            const incomes_by_week = results.weekly_incomes;
            const incomes_by_month = results.monthly_incomes;
            const incomes_by_year = results.yearly_incomes;
            document.getElementById('incomedaily').innerHTML = incomes_by_day;
            document.getElementById('incomeweekly').innerHTML = incomes_by_week;
            document.getElementById('incomemonthly').innerHTML = incomes_by_month;
            document.getElementById('incomeyearly').innerHTML = incomes_by_year;
        })
        .catch((error) => {
            console.error('Error fetching the metric data:', error);
        });

    fetch("/income/metric_card_view2_income")
    .then((res) => res.json())
    .then((results) => {
        console.log("results", results);
        const total_incomes_by_day = results.total_daily_incomes;
        const total_incomes_by_week = results.total_weekly_incomes;
        const total_incomes_by_month = results.monthly_totals;
        const total_incomes_by_year = results.total_yearly_incomes;
        document.getElementById('incometotaldaily').innerHTML = total_incomes_by_day;
        document.getElementById('incometotalweekly').innerHTML = total_incomes_by_week;
        document.getElementById('incometotalmonthly').innerHTML = total_incomes_by_month;
        document.getElementById('incometotalyearly').innerHTML = total_incomes_by_year;
    })
    .catch((error) => {
        console.error('Error fetching the metric data:', error);
    });
};

window.onload = getMetricData2();  
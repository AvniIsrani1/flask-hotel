document.addEventListener('DOMContentLoaded', function(){
    var start = startdate_url || ''; 
    var end = enddate_url || '';


    let starting_date = flatpickr("#startdate", {
        dateFormat: "F d, Y", 
        minDate: "today",  
        maxDate: new Date().fp_incr(365*2),
        prevArrow:'PREV',
        nextArrow:'NEXT', 
        onChange: function(dates, datestr, instance) {
            let startdate = dates[0]; 
            if (startdate) {
                document.querySelector("#enddate")._flatpickr.set('minDate', startdate);
            }
            calcNights();
        }
    });
    let ending_date = flatpickr("#enddate", {
        dateFormat: "F d, Y", 
        minDate: "today",  
        maxDate: new Date().fp_incr(365*2),
        prevArrow:'PREV',
        nextArrow:'NEXT',
        onChange: function(dates, datestr, instance) {
            calcNights();
        }
    });

    if(start){
        starting_date.setDate(start)
    }
    if(end){
        ending_date.setDate(end);
    }
    
    function calcNights() {
        const startdate = document.querySelector("#startdate")._flatpickr.selectedDates[0];
        const enddate = document.querySelector("#enddate")._flatpickr.selectedDates[0];
        if(startdate && enddate) {
            days = (enddate-startdate)/(1000*60*60*24) + 1;
            nights = days - 1;
            document.getElementById('nights').innerText=`${days} DAY${days==1?'': 'S'}, ${days-1} NIGHT${days-1==1?'' : 'S'}`;
        }
    };
    calcNights();
});


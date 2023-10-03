/*jshint esversion: 6 */
/*global console*/
import {
    format,
    add,
    eachDayOfInterval,
    startOfWeek,
    startOfMonth,
    endOfWeek,
    endOfMonth,
    isSameMonth,
    isSameDay

} from "https://cdn.skypack.dev/date-fns@2.29.3";

function setLoader(stat){
    if(stat){
        document.getElementById('loader').style.display='block';
        document.getElementsByClassName('loader')[0].style.display='block';
        return 0;
    }else{
        document.getElementById('loader').style.display='none';
        document.getElementsByClassName('loader')[0].style.display='none';
    }
}
//? Selecting UI elements
const UIDatePickerBtn = document.querySelector('.date-picker-button');
const UIDatePicker = document.querySelector('.date-picker');
const UICurrentMonth = document.querySelector('.current-month');
const UIDays = document.querySelectorAll('.date');
const previous_btn=document.getElementById('prev');
const next_btn=document.getElementById('nxt');

//? Setting Global Variables
const today = new Date();
let currentDate = today;
let selectedDate;

//? Setting defaults on page load
setBtnDate(currentDate);
UICurrentMonth.innerText = format(currentDate, 'MMMM - yyyy');

//? event listners
UIDatePickerBtn.addEventListener("click", (e) => {
    "use strict";
    // TOGGLE THE DATE PICKER MENU
    UIDatePicker.classList.toggle("show");
    showCalenderDays(currentDate);
});
UIDatePicker.addEventListener('click', (e) => {
    "use strict";
    if(e.target.matches('.prev-month-button')){
        currentDate = add(currentDate, {months: -1});
        UICurrentMonth.innerText = format(currentDate, 'MMMM - yyyy');
        showCalenderDays(currentDate);
    }
    if(e.target.matches('.next-month-button')){
        currentDate = add(currentDate, {months: 1});
        UICurrentMonth.innerText = format(currentDate, 'MMMM - yyyy');
        showCalenderDays(currentDate);
    }

});
function cat_date(date){
    window.location.href='/'+format(date, 'yyyy-dd-MM');
}

//? Helping Functions
function setBtnDate(date){
    "use strict";
    currentDate=date
    UIDatePickerBtn.innerText = format(date, 'MMMM do, yyyy')
    selectedDate = date;
}
let send_flag=true;
const xhttp=new XMLHttpRequest();
async function showCalenderDays(date){
    "use strict";
    let days = []

    days = eachDayOfInterval(
        {
            start: startOfWeek(startOfMonth(date)) ,
            end: endOfWeek(endOfMonth(date))
        });
    //! Creating the buttons for each day instead of adding text to the existing HTML is better do it later.
    for(let i = 0; i < days.length; i++){
        if(UIDays[i] == undefined) return;
            UIDays[i].classList.remove('date-picker-other-month-date');
            UIDays[i].disabled=false;
        UIDays[i].innerText = format(days[i], 'd');
        UIDays[i].addEventListener('click', () => {
            setBtnDate(days[i]);
            cat_date(days[i]);
            UIDatePicker.classList.remove('show');
        });
        if(isSameDay(days[i], selectedDate)){
            UIDays[i].classList.add('selected');
        }else{
            UIDays[i].classList.remove('selected');
        }

    }
    send_flag=true;
}

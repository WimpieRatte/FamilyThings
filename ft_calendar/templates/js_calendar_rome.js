/* Calendar powered by Rome */
let current_date = new Date();
var calendar = rome(document.getElementById('rome-calendar'), 
{ 
    "time": false,
    "styles": {
        "back": "rd-back",
        "container": "rd-container bg-body-tertiary rounded rounded-4 text-center p-2 d-block h-100",
        "date": "rd-date",
        "dayBody": "rd-days-body bg-dark d-block rounded rounded-3",
        "dayBodyElem": "rd-day-body", /*"rd-day-body",*/
        "dayConcealed": "rd-day-concealed",
        "dayDisabled": "rd-day-disabled",
        "dayHead": "rd-days-head",
        "dayHeadElem": "rd-day-head",
        "dayRow": "rd-days-row",
        "dayTable": "pt-1 d-block",
        "month": "rd-month font-monospace",
        "next": "rd-next",
        "positioned": "rd-container-attachment",
        "selectedDay": "rd-day-selected",
        "selectedTime": "rd-time-selected",
        "time": "rd-time",
        "timeList": "rd-time-list",
        "timeOption": "rd-time-option"
    },
    "weekStart": current_date.getDay()
});

var calendarEntries = []

let AJAXData = {csrfmiddlewaretoken: '{{ csrf_token }}'};
$.when( basicAJAX(type="POST", url=`{% url 'calendar:get' %}`, data=AJAXData) )
    .done(function( accompData ) {
        calendarEntries = accompData["entries"]

        // Convert all date strings to native JS Date objects
        calendarEntries.forEach(function(entry) {
            entry["date"] = new Date(entry["date"])
        });
    })

function resetDayButtons(event){
    let buttons = document.querySelectorAll(".rd-day-body");
    let dateToCheck = calendar.getDate();

    buttons.forEach(function(button) {
        entry = calendarEntries.filter((element) => 
        element["date"].getDate() == Number(button.textContent)
        && element["date"].getMonth() == dateToCheck.getMonth()
        && element["date"].getYear() == dateToCheck.getYear());

        if (entry.length > 0) {
            button.className = button.className += " position-relative";
            button.innerHTML = `${button.innerHTML}<span class="position-absolute translate-middle badge rounded-circle bg-success fw-normal fs-sm no-ptr-evt" style="font-size: 0.7em; top: 10%; left: 90%">${entry.length}</span>`;
        }
    });


    $(".rd-day-body").click(function(event) {
        // Execute with small delay to give the calendar system time to react to the selected date
        setTimeout(function() {updateDate(event)}, 10);
    });
}
setTimeout(function() {resetDayButtons();}, 1000)
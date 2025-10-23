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

function getEntries(){
    calendarEntries = []

    let AJAXData = {csrfmiddlewaretoken: '{{ csrf_token }}'};
    $.when( basicAJAX(type="POST", url=`{% url 'calendar:get' %}`, data=AJAXData) )
        .done(function( accompData ) {
            calendarEntries = accompData["entries"]

            // Convert all date strings to native JS Date objects
            calendarEntries.forEach(function(entry) {
                entry["date"] = new Date(entry["date"])
            });
            setTimeout(function() {resetDayButtons();}, 500)
        })
}
getEntries();

function resetDayButtons(event){
    let buttons = document.querySelectorAll(".rd-day-body:not(.rd-day-prev-month):not(.rd-day-next-month), .rd-day-selected");
    let dateToCheck = calendar.getDate();

    buttons.forEach(function(button) {
        if (button.dataset.value == undefined){
            button.dataset.value = button.textContent;
        }

        entry = calendarEntries.filter((element) => 
        element["date"].getDate() == button.dataset.value
        && element["date"].getMonth() == dateToCheck.getMonth()
        && element["date"].getYear() == dateToCheck.getYear());

        if (entry.length > 0) {
            button.className = button.className += " position-relative";
            button.innerHTML = `<span class="no-ptr-evt text-body">${button.innerHTML}</span><span class="position-absolute translate-middle badge rounded-circle bg-success fw-normal fs-sm no-ptr-evt" style="font-size: 0.7em; top: 10%; left: 90%">${entry.length}</span>`;
        }
        else {
            button.innerHTML = `<span class="no-ptr-evt text-body">${button.dataset.value}</span>`;
        }
    });

    $(".rd-day-body").off()
    $(".rd-day-body").click(function(event) {
        // Execute with small delay to give the calendar system time to react to the selected date
        setTimeout(function() {updateDate(event)}, 10);
    });
}
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
function openRepeat(data) {
    let _data = data.getAttribute("data-accomp-data").replaceAll(`'`, `"`).replaceAll(`None`, `null`).replaceAll(`False`, `false`).replaceAll(`True`, `true`);
    accomplishmentStorage = JSON.parse(_data)
    closePopup();
    openPopup("repeat-accomp-popup");
    prepareRepeat()
}

function prepareRepeat(){
    Object.entries(accomplishmentStorage).forEach(function(field) {
            let form_field = document.querySelector(`#repeat-accomp-form #id_${field[0]}`)

            if (form_field){
                if (field[0] = "measurement" && field[1] == null){ field[1] = "x"}
                form_field.value = field[1];
            }
        });

    let today = new Date()
    document.querySelector(`#repeat-accomp-form #id_date`).valueAsDate = today;
    document.querySelector(`#repeat-accomp-form #id_date_from`).valueAsDate = today;
    document.querySelector(`#repeat-accomp-form #id_date_to`).valueAsDate = today;

    //Apply name and icon
    document.querySelector(`#repeat-accomp-popup #edit-accomp-name`).textContent = accomplishmentStorage["name"]
    document.querySelector(`#repeat-accomp-popup #edit-accomp-icon`).className = `bi bi-${accomplishmentStorage["icon"]} h5`;
    document.querySelector(`#repeat-accomp-popup #lb-created-on`).textContent = ""

    document.querySelector(`#repeat-accomp-popup #id_measurement`).disabled = true;

    document.querySelector("#repeat-accomp-popup #btn-create").disabled = false;
    document.querySelector("#repeat-accomp-popup #btn-abort").disabled = false;

    $("#repeat-accomp-popup #btn-create").disabled = false;
    $("#repeat-accomp-popup #btn-abort").disabled = false;
}


$("#repeat-accomp-popup #btn-abort").click(function (event) {
    movePopupDown();
});


$("#repeat-accomp-popup #btn-create").click(function (event) {
    document.querySelector("#repeat-accomp-popup #btn-create").disabled = true;
    document.querySelector("#repeat-accomp-popup #btn-abort").disabled = true;

    let form = $("#repeat-accomp-form");
    let AJAXData = form.serializeArray();

    $("#repeat-accomp-popup #btn-create").disabled = true;
    $("#repeat-accomp-popup #btn-abort").disabled = true;

    if (document.querySelector("#repeat-accomp-popup #id_date").deactivated){
        AJAXData.push({'name': 'date_from', 'value': document.querySelector("#repeat-accomp-popup #id_date_from").value});
        AJAXData.push({'name': 'date_to', 'value': document.querySelector("#repeat-accomp-popup #id_date_to").value});
    }
    else {
        AJAXData.push({'name': 'date', 'value': document.querySelector("#repeat-accomp-popup #id_date").value});
    }

    $.when(basicAJAX(type = "POST", url = `${repeatAccompURL}`, data = AJAXData))
        .done(function (accompData) {
            if (accompData != null) {                
                setTimeout(function() {
                    playConfetti(offset=0.55);
                }, 1);

                setTimeout(function() {
                    createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
                }, 1600);

                setTimeout(function() {
                    movePopup()
                }, 2500);
            }
            $("#repeat-accomp-popup #btn-create").disabled = false;
            $("#repeat-accomp-popup #btn-abort").disabled = false;
        })
});
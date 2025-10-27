let buttonEditAbort = document.querySelector("#edit-accomp-popup #btn-abort");
let buttonEditApply = document.querySelector("#edit-accomp-popup #btn-apply-changes");

let form = document.querySelector("#edit-accomp-form");

buttonEditAbort.addEventListener("click", function() {
    movePopupDown();
});

buttonEditApply.addEventListener("click", function() {
    buttonEditAbort.disabled = true;
    buttonEditApply.disabled = true;

    let form_data = $("#edit-accomp-form")
    let form_array = form_data.serializeArray()
    if (document.querySelector('#edit-accomp-form #id_date').deactivated){
        form_array.push({'name': 'date_from', 'value': document.querySelector('#edit-accomp-form #id_date_from').value});
        form_array.push({'name': 'date_to', 'value': document.querySelector('#edit-accomp-form #id_date_to').value});
    }
    else {
        form_array.push({'name': 'date_from', 'value': document.querySelector('#edit-accomp-form #id_date').value});
        form_array.push({'name': 'date_to', 'value': document.querySelector('#edit-accomp-form #id_date').value});
    }

    console.log(form_data.serializeArray())

    basicAJAX(type="POST", url=`${editAccompURL}${accompToEdit}`, data=form_array)

    playCheckmarkAnimation();

    setTimeout(function() {
        createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
    }, 1600-400);

    setTimeout(function() {
        movePopup();
    }, movePopupDelay-400);
});


var accompToEdit = -1
//$(`#edit-accomp-${data["pk"]}`).click(function (event) {
function openEditPrompt(ID) {
    accompToEdit = ID;
    currentAJAXURL = editAccompURL;

    let AJAXData = { csrfmiddlewaretoken: '{{ csrf_token }}' };

    $.when(basicAJAX(type = "POST", url = `${getAccompURL}${ID}`, data = AJAXData))
        .done(function (accompData) {
            if (accompData != null) {
                let language = languageCode;
                if (language == "") { language = "en"; }

                openPopup("edit-accomp-popup");

                // Fill the fields with the obtained data
                var fields = ['measurement', "measurement_quantity", "date_from", "date_to"]

                fields.forEach(function (field) {
                    $(`#edit-accomp-popup #id_${field}`).val(accompData[field]);
                });

                $(`#edit-accomp-popup #id_measurement_quantity`).val($(`#edit-accomp-popup #id_measurement_quantity`).val().replaceAll(".00", ""));

                $('#edit-accomp-popup #edit-accomp-name').text(accompData["name"]);
                document.getElementById('edit-accomp-icon').className = `bi bi-${accompData["icon"]}`;

                $('#edit-accomp-popup #edit-accomp-created').text(new Date(accompData["created"]).toLocaleDateString(language, {
                    weekday: "short", year: "numeric",
                    month: "short", day: "numeric",
                }));

                $(`#edit-accomp-popup #id_measurement`).prop("disabled", true)
                // If the user has not Measurement type but a quantity specified, use x (amount of times)
                if (accompData['measurement'] == null) {
                    $(`#edit-accomp-popup #id_measurement`).val("x");
                }
                else {
                    $(`#edit-accomp-popup #id_measurement`).val(accompData['measurement']);
                }
                document.querySelector('#edit-accomp-popup #id_date').value = accompData["date_from"];
                document.querySelector('#edit-accomp-popup #id_date_from').value = accompData["date_from"];
                document.querySelector('#edit-accomp-popup #id_date_to').value = accompData["date_to"];

                if (accompData["date_to"] != accompData["date_from"]) {
                    document.querySelector('#edit-accomp-popup #id_timeframe').checked = false;
                    document.querySelector('#edit-accomp-popup #id_timeframe').click();
                }
                else {
                    document.querySelector('#edit-accomp-popup #id_timeframe').checked = true;
                    document.querySelector('#edit-accomp-popup #id_timeframe').click();
                }
            }
        });

    buttonEditAbort.disabled = false;
    buttonEditApply.disabled = false;
};
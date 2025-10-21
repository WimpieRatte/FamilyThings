var buttonEditAbort = document.querySelector("#edit-accomp-popup #btn-abort");
var buttonEditApply = document.querySelector("#edit-accomp-popup #btn-apply-changes");

var form = document.querySelector("#edit-accomp-form");

buttonEditAbort.addEventListener("click", function() {
    closePopup();
});

buttonEditApply.addEventListener("click", function() {
    buttonEditAbort.disabled = true;
    buttonEditApply.disabled = true;

    let form_data = $("#edit-accomp-form")
    let form_array = form_data.serializeArray()
    form_array.push({'name': 'date_from', 'value': document.querySelector('#edit-accomp-form #id_date_from').value});
    form_array.push({'name': 'date_to', 'value': document.querySelector('#edit-accomp-form #id_date_to').value});

    basicAJAX(type="POST", url=`${editAccompURL}${selectedAccomplishment}`, data=form_array)
    playCheckmarkAnimation();

    setTimeout(function() {
        createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
        closePopup();
        buttonEditAbort.disabled = false;
        buttonEditApply.disabled = false;
    }, 2600);
});

//$(`#edit-accomp-${data["pk"]}`).click(function (event) {
function openEditPrompt(ID) {
    selectedAccomplishment = ID;
    currentAJAXURL = editAccompURL;

    let AJAXData = { csrfmiddlewaretoken: '{{ csrf_token }}' };

    $.when(basicAJAX(type = "POST", url = `${getAccompURL}${ID}`, data = AJAXData))
        .done(function (accompData) {
            if (accompData != null) {
                let language = languageCode;
                if (language == "") { language = "en"; }

                openPopup("edit-accomp-popup");

                // Fill the fields with the obtained data
                var fields = ['measurement', "measurement_quantity", "date_from_day", "date_from_month",
                    "date_from_year", "date_to_day", "date_to_month", "date_to_year"]

                fields.forEach(function (field) {
                    $(`#edit-accomp-popup #id_${field}`).val(accompData[field]);
                });

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
                document.querySelector('#edit-accomp-popup  #id_date_from').value = accompData["date_from"];
                document.querySelector('#edit-accomp-popup  #id_date_to').value = accompData["date_to"];
            }
        });
};
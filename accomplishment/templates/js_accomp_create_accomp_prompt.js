let newName = document.querySelector(`#new-accomp-popup #edit-accomp-name`);
let newIcon = document.querySelector(`#new-accomp-popup #edit-accomp-icon`)

let formNameField = document.querySelector("#new-accomp-popup #id_name")
let formCategoryField = document.querySelector('#new-accomp-popup #id_accomplishment_type')
let formDescriptionField = document.querySelector('#new-accomp-popup #id_description')
let formUnitField = document.querySelector('#new-accomp-popup #id_measurement')
let formQuantityField = document.querySelector('#new-accomp-popup #id_measurement_quantity')
let formAchievementField = document.querySelector('#new-accomp-popup #id_is_achievement')
let formDateField = document.querySelector('#new-accomp-popup #id_date')
let formDateFromField = document.querySelector('#new-accomp-popup #id_date_from')
let formDateToField = document.querySelector('#new-accomp-popup #id_date_to')

let formButtonCreate = document.querySelector("#new-accomp-popup #btn-create");
let formButtonAbort = document.querySelector("#new-accomp-popup #btn-abort");


function initiateCreate() {
    closePopup();
    openPopup("new-accomp-popup");

    //Apply name and icon
    newName.textContent = nameField.value;
    newIcon.className = `bi bi-plus-circle-fill h5`;

    //Reset fields while importing the name that was entered in the previous screen
    formNameField.value = nameField.value;

    formCategoryField.value = "";
    formDescriptionField.value = "";
    formUnitField.value = "";
    formQuantityField.value = 0;
    formAchievementField.checked = false;

    let today = new Date()
    formDateField.valueAsDate = today;
    formDateFromField.valueAsDate = today;
    formDateToField.valueAsDate = today;

    formButtonCreate.disabled = false;
    formButtonAbort.disabled = false;

    document.querySelector('#new-accomp-popup #id_timeframe').checked = true;
    document.querySelector('#new-accomp-popup #id_timeframe').click();

    input_change_value(document.querySelector(`#new-accomp-popup #icon-btn-dash`), `#new-accomp-popup #id_icon`);
}

$('#new-accomp-popup #id_is_achievement').click(function() {
        if ($(this).prop("checked") == true) { 
            newIcon.className = `bi bi-plus-circle-fill h5 special-achievement`;
            newName.className = `h5 special-achievement`;
        }
        else { 
            newIcon.className = `bi bi-plus-circle-fill h5`;
            newName.className = `h5`;
        }
    }
);

$("#new-accomp-popup #btn-abort").click(function(event) {
    if (confirm(`Are you sure you want to quit?`)) {
        movePopupDown();
        createAlert(text="Creation aborted.", key="", type="warning");
    }
});

// AJAX Submission
$("#new-accomp-popup #btn-create").click(function(event) {
    event.preventDefault(); // Prevents the button from creating the default HTTPRequest
    formButtonCreate.disabled = true;
    formButtonAbort.disabled = true;

    enableLoadingScreen();  // Function is defined in site_js

    let form_data = $("#new-accomp-popup #accomplishment-form")
    let form_array = form_data.serializeArray()
    if (formDateField.deactivated){
        form_array.push({'name': 'date_from', 'value': formDateFromField.value});
        form_array.push({'name': 'date_to', 'value': formDateToField.value});
    }
    else {
        form_array.push({'name': 'date', 'value': formDateField.value});
    }
    
    $.ajax({ 
        type: 'POST', url: '{% url "accomplishment:submit_new" %}',
        data: form_array,
        success: function(json) {
            disableLoadingScreen();
            createAlert(text=json["alert-message"], key="", type=json["alert-type"]);
            
            setTimeout(function() {
                playConfetti(offset=0.6);
            }, 1);

            setTimeout(function() {
                createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
            }, 1600);

            setTimeout(function() {
                movePopup()
            }, 2500);
        },
        error: function(xhr, errmsg, err) {
            event.target.disabled = false;
            disableLoadingScreen();
            createAlert(xhr.responseText, key="", type="danger");
            formButtonCreate.disabled = false;
            formButtonAbort.disabled = false;
        }
    });
});
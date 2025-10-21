
let newName = document.querySelector(`#new-accomp-popup #edit-accomp-name`);
let newIcon = document.querySelector(`#new-accomp-popup #edit-accomp-icon`)

let formNameField = document.querySelector("#new-accomp-popup #id_name")
let formCategoryField = document.querySelector('#new-accomp-popup #id_accomplishment_type')
let formDescriptionField = document.querySelector('#new-accomp-popup #id_description')
let formUnitField = document.querySelector('#new-accomp-popup #id_measurement')
let formQuantityField = document.querySelector('#new-accomp-popup #id_measurement_quantity')
let formAchievementField = document.querySelector('#new-accomp-popup #id_is_achievement')
let formDateFromField = document.querySelector('#new-accomp-popup #id_date_from')
let formDateToField = document.querySelector('#new-accomp-popup #id_date_to')


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
    formDateFromField.valueAsDate = today;
    formDateToField.valueAsDate = today;

    input_change_value(document.querySelector(`#new-accomp-popup #icon-btn-dash`), `#new-accomp-popup #id_icon`);
}


const duplicateAccomplishmentPrompt = document.getElementById("duplicate-accomplishment-prompt");
var duplicateAccomplishment = new Object()
const accompNameField = document.getElementById("id_name");
const accompDescriptionField = document.getElementById("id_description");
const accompSubmitButton = document.getElementById("btn-create");

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
    closePopup();
});

// AJAX Submission
$("#new-accomp-popup #btn-create").click(function(event) {
    event.preventDefault(); // Prevents the button from creating the default HTTPRequest
    submitButton.disabled = true; //  Disables the log in button

    enableLoadingScreen();  // Function is defined in site_js

    accompDescriptionField.disabled = false;

    let form_data = $("#new-accomp-popup #accomplishment-form")
    let form_array = form_data.serializeArray()
    form_array.push({'name': 'date_from', 'value': formDateFromField.value});
    form_array.push({'name': 'date_to', 'value': formDateToField.value});
    
    $.ajax({ 
        type: 'POST', url: '{% url "accomplishment:submit_new" %}',
        data: form_array,
        success: function(json) {
            disableLoadingScreen();
            createAlert(text=json["alert-message"], key="", type=json["alert-type"]);

            setTimeout(function() {
                closePopup();
                createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
            }, 2000);

            playConfetti();
        },
        error: function(xhr, errmsg, err) {
            event.target.disabled = false;
            disableLoadingScreen();
            createAlert(xhr.responseText, key="", type="danger");
        }
    });
});
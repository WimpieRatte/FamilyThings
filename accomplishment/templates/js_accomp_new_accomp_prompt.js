function initiateCreate() {
    closePopup();
    openPopup("new-accomp-popup");

    //Apply name and icon
    document.querySelector(`#new-accomp-popup #edit-accomp-name`).textContent = nameField.value;
    document.querySelector(`#new-accomp-popup #edit-accomp-icon`).className = `bi bi-plus-circle-fill h5`;

    //Reset fields while importing the name that was entered in the previous screen
    document.querySelector("#new-accomp-popup #id_name").value = nameField.value;

    document.querySelector('#new-accomp-popup #id_accomplishment_type').value = "";
    document.querySelector('#new-accomp-popup #id_description').value = "";
    document.querySelector('#new-accomp-popup #id_measurement').value = "";
    document.querySelector('#new-accomp-popup #id_measurement_quantity').value = 0;
    document.querySelector('#new-accomp-popup #id_is_achievement').checked = false;

    let today = new Date()
    document.querySelector('#new-accomp-popup #id_date_from').valueAsDate = today;
    document.querySelector('#new-accomp-popup #id_date_to').valueAsDate = today;

    input_change_value(document.querySelector(`#new-accomp-popup #icon-btn-dash`), `#new-accomp-popup #id_icon`);
}


const duplicateAccomplishmentPrompt = document.getElementById("duplicate-accomplishment-prompt");
var duplicateAccomplishment = new Object()
const accompNameField = document.getElementById("id_name");
const accompDescriptionField = document.getElementById("id_description");
const accompSubmitButton = document.getElementById("btn-create");

$('#new-accomp-popup #id_is_achievement').click(function() {
        if ($(this).prop("checked") == true) { 
            document.querySelector(`#new-accomp-popup #edit-accomp-icon`).className = `bi bi-plus-circle-fill h5 special-achievement`;
            document.querySelector(`#new-accomp-popup #edit-accomp-name`).className = `h5 special-achievement`;
        }
        else { 
            document.querySelector(`#new-accomp-popup #edit-accomp-icon`).className = `bi bi-plus-circle-fill h5`;
            document.querySelector(`#new-accomp-popup #edit-accomp-name`).className = `h5`;
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
    form_array.push({'name': 'date_from', 'value': document.querySelector('#new-accomp-popup #id_date_from').value});
    form_array.push({'name': 'date_to', 'value': document.querySelector('#new-accomp-popup #id_date_to').value});
    
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

            setTimeout(function () {
                    var count = 200;
                    var new_shape = confetti.shapeFromPath({ path: 'M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z' });
                    var defaults = { origin: { y: 0.55 }, shapes: [new_shape], gravity: 1.133 };

                    function fire(particleRatio, opts) {
                        confetti({ ...defaults, ...opts, particleCount: Math.floor(count * particleRatio) });
                    }
                    fire(0.25, { spread: 26, startVelocity: 55, zIndex: 2000, });
                    fire(0.2, { spread: 60, zIndex: 2000, scalar: 1.2 });
                    fire(0.35, { spread: 100, decay: 0.91, scalar: 0.8, zIndex: 2000});
                    fire(0.1, { spread: 120, startVelocity: 25, scalar: 1.2, decay: 0.92, scalar: 1.2, zIndex: 2000 });
                    fire(0.1, { spread: 120, startVelocity: 45, scalar: 1.2, zIndex: 2000});
                }, 1);
        },
        error: function(xhr, errmsg, err) {
            event.target.disabled = false;
            disableLoadingScreen();
            createAlert(xhr.responseText, key="", type="danger");
        }
    });
});
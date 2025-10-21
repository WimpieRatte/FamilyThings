$(document).ready(function() {
    const saveBtn = document.getElementById("btn-save-event");
    const cancelBtn = document.getElementById("btn-cancel-event");

    const titleField = document.getElementById("event-title");
    const descField = document.getElementById("event-description");
    const dateField = document.getElementById("event-date");
    const errorMsg = document.getElementById('event-error');
    const successMsg = document.getElementById('event-success');


/********************************
 * CREATE NEW CALENDAR ENTRY
 ****************************/

clearFormData = function(){
    titleField.value = "";
    descField.value = "";
    dateField.value = "";
}

$(cancelBtn).click(function () {
    closePopup();
    clearFormData();
});

$("#add-new-button").click(function(event) {
    event.preventDefault();
    openPopup("calendar-event-popup");
    clearFormData();
});

$(saveBtn).click(function(event) {
    event.preventDefault();

          const title = titleField.value.trim();
        const description = descField.value.trim();
        const date = dateField.value;

        if (!title || !date) {
            successMsg.style.display = "none";
            errorMsg.style.display = "block";
            return
        }

        enableLoadingScreen();

    let form_data = {
        title,
        description,
        date,
        csrfmiddlewaretoken: '{{ csrf_token }}'
    }

    $.ajax({ 
        type: 'POST', url: '{% url "calendar:create_event" %}',
        data: {
            ...form_data
        },
        success: function(json) {
            disableLoadingScreen();
            playCheckmarkAnimation();
            //closePopup();
            createAlert(text=json["alert-message"], key="", type=json["alert-type"]);

            setTimeout(function() {
                window.location.replace('{{request.session.last_visited_page}}'); 
            }, 2600);
        },
        error: function(xhr, errmsg, err) {
            event.target.disabled = false;
            disableLoadingScreen();
            createAlert(xhr.responseText, key="", type="danger");
        }
    });
});
});
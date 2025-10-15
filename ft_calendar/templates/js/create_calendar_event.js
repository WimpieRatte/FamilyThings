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

        if (!title || !date || !description) {
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
            closePopup();
            createAlert(text=json["alert-message"], key="", type=json["alert-type"]);
            setTimeout(function() {window.location.replace('{{request.session.last_visited_page}}');}, 2000);

            setTimeout(function() {
                var count = 200;
                var defaults = {origin: { y: 0.65 }};

                function fire(particleRatio, opts) {
                    confetti({...defaults, ...opts, particleCount: Math.floor(count * particleRatio)});
                }
                fire(0.25, { spread: 26, startVelocity: 55});
                fire(0.2, {spread: 60,});
                fire(0.35, {spread: 100, decay: 0.91, scalar: 0.8});
                fire(0.1, {spread: 120, startVelocity: 25, decay: 0.92, scalar: 1.2});
                fire(0.1, {spread: 120, startVelocity: 45});
            }, 10);
        },
        error: function(xhr, errmsg, err) {
            event.target.disabled = false;
            disableLoadingScreen();
            createAlert(xhr.responseText, key="", type="danger");
        }
    });
});
});
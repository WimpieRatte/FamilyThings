$(document).ready(function() {
    const saveBtn = $("#btn-save-event");
    const cancelBtn = $("#btn-cancel-event");

    const titleField = $("#event-title");
    const descField = $("#event-description");
    const dateField = $("#event-date");
    const errorMsg = $("#event-error");
    const successMsg = $("#event-success");
    const eventIdField = $("#event-id");  // hidden input in your form

    /********************************
     * DJANGO URLS (safe injection)
     ********************************/
    const createEventUrl = "{% url 'calendar:create_event' %}";
    // Using placeholder UUID — we’ll replace it dynamically
    const editEventUrlTemplate = "{% url 'calendar:calendar_edit' 0 %}";

    function getEventUrl(eventId) {
        return eventId
            ? editEventUrlTemplate.replace('0', eventId)
            : createEventUrl;
    }
    
    /********************************
     * UTILITIES
     ********************************/
    function clearFormData() {
        titleField.val("");
        descField.val("");
        dateField.val("");
        eventIdField.val("");
        successMsg.hide();
        errorMsg.hide();
    }

    $(cancelBtn).click(function() {
        movePopupDown();
        clearFormData();
    });

    $("#add-new-button").click(function(event) {
        event.preventDefault();
        openPopup("calendar-event-popup");
        $("#lb-calendar-create").text("Create Calendar Entry");
        clearFormData();
        document.getElementById("event-date").valueAsDate = calendar.getDate();
    });

    /********************************
     * CREATE OR EDIT CALENDAR ENTRY
     ********************************/
    $(saveBtn).click(async function() {
        saveBtn.disabled = true;
        const title = titleField.val().trim();
        const description = descField.val().trim();
        const date = dateField.val();
        const eventId = eventIdField.val();

        if (!title || !date) {
            errorMsg.text("Please fill in all required fields.").fadeIn();
            successMsg.hide();
            return;
        }

        const url = getEventUrl(eventId);

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    title: title,
                    description: description,
                    date: date,
                }),
            });

            if (!response.ok) throw new Error("Server error");

            const data = await response.json();

            if (data.status === "success") {
                // successMsg.text(data.message).fadeIn();
                // errorMsg.hide();

                disableLoadingScreen();
                playCheckmarkAnimation();
                createAlert(text=data.message, key="", type="success");
                getEntries();

                setTimeout(function() {
                    movePopupDown();
                }, 2600);
            } else {
                throw new Error(data.message || "Something went wrong");
            }
        } catch (err) {
            // errorMsg.text(err.message).fadeIn();
            // successMsg.hide();
            
            disableLoadingScreen();
            createAlert(text=err.message, key="", type="danger");

        }
    });

    /********************************
     * OPEN FORM IN EDIT MODE
     ********************************/
    $(document).on("click", ".btn-edit-event", function() {
        const eventId = $(this).data("event-id");
        const title = $(this).data("event-title");
        const desc = $(this).data("event-description");
        let rawDate = $(this).data("event-date");

        // Convert it to a real Date object and then format it to YYYY-MM-DD
        let formattedDate = new Date(rawDate).toISOString().split("T")[0];


        $("#event-date").val(formattedDate);    
        $("#event-id").val(eventId);
        $("#event-title").val(title);
        $("#event-description").val(desc);
        $("#lb-calendar-create").text("Edit Calendar Entry");
    
        openPopup("calendar-event-popup");
    });
    
    
    $(document).on("click", ".btn-delete-event", async function() {
        const eventId = $(this).data("event-id");
        const url = `{% url 'calendar:calendar_delete' 0 %}`.replace('0', eventId);
        if (!confirm("Are you sure you want to delete this Entry?")) return;
    
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            });
            if (response.ok) {
                $(`#card${eventId}`).fadeOut();
                createAlert(text="Entry has been successfully deleted.", key="", type="warning");
                getEntries();
            } else {
                createAlert(text="Failed to delete Entry.", key="", type="danger");
            }
        } catch (err) {
            console.error(err);
        }
    });
    
    /********************************
     * HELPER: Get CSRF token
     ********************************/
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === name + "=") {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

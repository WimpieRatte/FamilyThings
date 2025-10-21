$("#edit-template-popup #btn-abort").click(function(event) {
    closePopup();
});

$("#edit-template-popup #btn-apply-changes").click(function(event) {
    let form_data = $("#edit-template-popup #accomplishment-form")
    let form_array = form_data.serializeArray()
    $.when(basicAJAX(type = "POST", url = `${saveTemplateURL}`, data = form_array))
    .done(function (result) {
        playCheckmarkAnimation();

        setTimeout(function() {
            createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
            closePopup();
        }, 2600);
    });
});

function editAccomplishmentPrompt(ID) {
    let AJAXData = {csrfmiddlewaretoken: '{{ csrf_token }}', ID: ID};

    $.when(basicAJAX(type = "POST", url = `${getTemplateURL}`, data = AJAXData))
    .done(function (result) {
        if (result != null) {
            // Fill the fields with the obtained data
            var fields = ['name', 'description', 'measurement', 'accomplishment_type', 'ID']

            fields.forEach(function (field) {
                if (result[field] != undefined){
                    document.querySelector(`#edit-template-popup #id_${field}`).value = result[field];
                }
            });
            document.querySelector(`#edit-template-popup #id_is_achievement`).checked = result["is_achievement"];

            input_change_value(document.querySelector(`#edit-template-popup #icon-btn-${result["icon"]}`), `#edit-template-popup #id_icon`);

            openPopup("edit-template-popup");
        }
    });
}
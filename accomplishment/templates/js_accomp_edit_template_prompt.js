$("#edit-template-popup #btn-abort").click(function(event) {
    closePopup();
});

$("#edit-template-popup #btn-apply-changes").click(function(event) {
    playCheckmarkAnimation();
});

function editAccomplishmentPrompt(ID) {
    let AJAXData = {csrfmiddlewaretoken: '{{ csrf_token }}', ID: ID};

    $.when(basicAJAX(type = "POST", url = `${getTemplateURL}`, data = AJAXData))
    .done(function (result) {
        if (result != null) {
            console.log(result)
            openPopup("edit-template-popup");
        }
    });
}
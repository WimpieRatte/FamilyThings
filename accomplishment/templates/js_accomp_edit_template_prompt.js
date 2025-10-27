var buttonTemplateEditAbort = document.querySelector("#edit-template-popup #btn-abort");
var buttonTemplateEditApply = document.querySelector("#edit-template-popup #btn-apply-changes");

var templateFormNameField = document.querySelector("#edit-template-popup #id_name");

buttonTemplateEditAbort.addEventListener("click", function() {
    movePopupDown();
});

buttonTemplateEditApply.addEventListener("click", function() {
    let form_data = $("#edit-template-popup #accomplishment-form")
    let form_array = form_data.serializeArray()
    $.when(basicAJAX(type = "POST", url = `${saveTemplateURL}`, data = form_array))
    .done(function (result) {
        playCheckmarkAnimation();

        setTimeout(function() {
            createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
        }, 1600);

        setTimeout(function() {
            movePopup()
        }, movePopupDelay);
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
            currentTemplateName = result["name"]
        }
    });
}

let currentTemplateName = ""
let previousTemplateName = ""
function templateNameCheckAvailable(enforceCheck = false) {
    if (templateFormNameField.value.length > 0 && (previousTemplateName != templateFormNameField.value || enforceCheck)){
        previousTemplateName = templateFormNameField.value;

        $.ajax({ 
            type: 'POST', url: `${nameCheckURL}${templateFormNameField.value}`, data: {
                csrfmiddlewaretoken: '{{ csrf_token }}'},
            success: function() {
                if (templateFormNameField.value != currentTemplateName){
                    buttonTemplateEditApply.disabled = true;
                    templateFormNameField.className = "bg-danger";
                }
            },
            error: function() {
                buttonTemplateEditApply.disabled = false;
                templateFormNameField.className = "";
            }
        });
    }
    setTimeout(function() { templateNameCheckAvailable() }, 1000);
}
templateNameCheckAvailable();

templateFormNameField.addEventListener("keyup", function() {
    buttonTemplateEditApply.disabled = true;
});
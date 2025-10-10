$("#edit-accomp-popup #btn-abort").click(function(event) {
    closePopup();
});

$("#btn-apply-changes").click(function(event) {
    let form_data = $("#edit-accomp-form");

    basicAJAX(type="POST", url=`${editAccompURL}${selectedAccomplishment}`, data=form_data.serializeArray())
    createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
    closePopup();
});
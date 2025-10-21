$("#edit-accomp-popup #btn-abort").click(function(event) {
    closePopup();
});

$("#edit-accomp-popup #btn-apply-changes").click(function(event) {
    let form_data = $("#edit-accomp-form")
    let form_array = form_data.serializeArray()
    form_array.push({'name': 'date_from', 'value': document.querySelector('#edit-accomp-form #id_date_from').value});
    form_array.push({'name': 'date_to', 'value': document.querySelector('#edit-accomp-form #id_date_to').value});

    basicAJAX(type="POST", url=`${editAccompURL}${selectedAccomplishment}`, data=form_array)
    createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
    playCheckmarkAnimation();
    closePopup();
});
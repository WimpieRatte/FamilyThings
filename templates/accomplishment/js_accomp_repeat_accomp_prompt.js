function prepareRepeat(){
    Object.entries(accomplishmentStorage).forEach(function(field) {
            let form_field = document.querySelector(`#repeat-accomp-form #id_${field[0]}`)

            if (form_field){
                if (field[0] = "measurement" && field[1] == null){ field[1] = "x"}
                form_field.value = field[1];
            }
        });

    //Apply name and icon
    document.querySelector(`#repeat-accomp-popup #edit-accomp-name`).textContent = accomplishmentStorage["name"]
    document.querySelector(`#repeat-accomp-popup #edit-accomp-icon`).className = `bi bi-${accomplishmentStorage["icon"]} h5`;
    document.querySelector(`#repeat-accomp-popup #lb-created-on`).textContent = ""

    document.querySelector(`#repeat-accomp-popup #id_measurement`).disabled = true;
}


$("#repeat-accomp-popup #btn-abort").click(function (event) {
    closePopup();
});


$("#repeat-accomp-popup #btn-create").click(function (event) {
    //closePopup()
    let form = $("#repeat-accomp-form");
    let AJAXData = form.serializeArray();

    $.when(basicAJAX(type = "POST", url = `${repeatAccompURL}`, data = AJAXData))
        .done(function (accompData) {
            if (accompData != null) {
                setTimeout(function () { closePopup() }, 3000);

                setTimeout(function () {
                    var count = 200;
                    var defaults = { origin: { y: 0.55 } };

                    function fire(particleRatio, opts) {
                        confetti({ ...defaults, ...opts, particleCount: Math.floor(count * particleRatio) });
                    }
                    fire(0.25, { spread: 26, startVelocity: 55, zIndex: 2000 });
                    fire(0.2, { spread: 60, zIndex: 2000 });
                    fire(0.35, { spread: 100, decay: 0.91, scalar: 0.8, zIndex: 2000 });
                    fire(0.1, { spread: 120, startVelocity: 25, decay: 0.92, scalar: 1.2, zIndex: 2000 });
                    fire(0.1, { spread: 120, startVelocity: 45, zIndex: 2000 });
                }, 1);
                createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
            }
        })
});
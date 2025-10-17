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

    $("#repeat-accomp-popup #btn-create").disabled = false;
    $("#repeat-accomp-popup #btn-abort").disabled = false;
}


$("#repeat-accomp-popup #btn-abort").click(function (event) {
    closePopup();
});


$("#repeat-accomp-popup #btn-create").click(function (event) {
    let form = $("#repeat-accomp-form");
    let AJAXData = form.serializeArray();

    $("#repeat-accomp-popup #btn-create").disabled = true;
    $("#repeat-accomp-popup #btn-abort").disabled = true;

    $.when(basicAJAX(type = "POST", url = `${repeatAccompURL}`, data = AJAXData))
        .done(function (accompData) {
            if (accompData != null) {
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
                createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
            }
        })
});
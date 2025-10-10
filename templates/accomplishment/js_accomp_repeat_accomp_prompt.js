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
                }, 10);
                createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
            }
        })
});
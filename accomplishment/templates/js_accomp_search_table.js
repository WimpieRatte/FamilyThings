var todaysAccContainer = $("#accomplishments-table-body");
var searchBar = document.getElementById("search-filter");
var tablePreviousButton = document.getElementById("previous-button");
var tableNextButton = document.getElementById("next-button");
var accomTableBody = document.getElementById("accomplishments-table-body")

var currentIndex = 1;
var currentEnd = 0;
var totalEntries = 0;

var searchText = "";
var searchSelector = "name";

/* Get Today's Accomplishments */
const queryURL = "{{HOST}}/accomplishments/get"
function createAccomplishmentsTable(length = 15, start = 1, search = "", selector = "name") {
    tablePreviousButton.disabled = true;
    tableNextButton.disabled = true;
    currentIndex = start;

    let queryURLFinal = `${queryURL}/amount=${length}/start=${start}/selector='${selector}'`

    if (search != "") { queryURLFinal += `/key='${search}'` }
    $.get(queryURLFinal, function () { })
        .done(function (response) {
            var index = 0;
            todaysAccContainer.empty();
            Object.entries(response.result).forEach(function (entry) {
                let data = entry[1];
                createTableEntry(todaysAccContainer, data, start + index, searchText, selector)
                index++;
            });

            currentEnd = start + Object.entries(response.result).length;
            totalEntries = response.total;
            if (currentEnd - 1 < totalEntries) { tableNextButton.disabled = false; }
            document.getElementById("range-start").textContent = start;
            document.getElementById("range-end").textContent = start - 1 + Object.entries(response.result).length;
            document.getElementById("range-total").textContent = response.total;

            applyLocaleToPage() /* Refresh all language content */
            updateTooltips(); // Required to make the new Entries interactable
        })
        .fail(function (err) { console.log(err); })

    if (currentIndex > 1) { tablePreviousButton.disabled = false; }
}
createAccomplishmentsTable()

/* Dynamically create Accomplishment entries */
const tableEntryTemplate = `{% include "temp_accomp_entry.html" %}`

function createTableEntry(target_container, data, index, highlight = "", selector = "name") {
    // Get the date
    let language = languageCode;
    if (language == "") { language = "en"; }

    creation_date = new Date(data["fields"]["created"]).toLocaleTimeString(language, {
        year: "numeric", month: "short", day: "numeric",
        hour: '2-digit', minute: '2-digit'
    })

    // Prepare the template and retrieve the Accomplishment details
    let accom_template = data["fields"]["accomplishment"];
    let templateDump = tableEntryTemplate;
    let accomp_name = accom_template["name"];

    /* Highlight the name based on the search query */
    if (highlight != "" && selector == 'name') { accomp_name = accomp_name.replace(highlight, `<strong>$1</strong>`) }

    //accomp_name = `<span class='position-relative'><span id='lb-new' class='bg-primary p-1 rounded fs-sm position-absolute start-100 top-50 translate-middle'>New</span>${accomp_name}</span>`

    /* Turn the whole name + icon yellow */
    if (accom_template["is_achievement"]) { templateDump = templateDump.replace("%name_style%", 'style="color: #ddc67f !important;"') }
    else { templateDump = templateDump.replace("%name_style%", '') }


    // Apply most of the template
    templateDump = templateDump.replace("%index%", index)
        .replace("%date_created%", creation_date)
        .replaceAll("%name%", accomp_name)
        .replaceAll("%ID%", data["pk"])
        .replace("%icon%", accom_template["icon"])
        .replace("%category%", accom_template["type"])
        .replace("%description%", accom_template["description"])
        .replace("%repeatURL%", `"add%3Frepeat=${accom_template["ID"]}""`)
        .replace("undefined", "N/A")
        .replace("%content%", JSON.stringify(accom_template))

    // Process Measurement Data
    let measurement_data = "-"
    if (accom_template["measurement"] != null) {
        measurement_data = `${data["fields"]["measurement_quantity"]}${accom_template["measurement"]}`;
    }
    else if (data["fields"]["measurement_quantity"] != null && data["fields"]["measurement_quantity"] != 0) {
        measurement_data = `${parseInt(data["fields"]["measurement_quantity"])}x`;
    }
    templateDump = templateDump.replace("%measurement%", measurement_data);

    target_container.append(templateDump);


    // Add Delete Accomplishment prompt to the generated entry
    var deleteURL = "{{HOST}}/accomplishments/delete/id="
    document.getElementById(`delete-accomplishment-btn-${data["pk"]}`).addEventListener("click", (event) => {
        let accomp_id = event.currentTarget.getAttribute("data-accomp-id");
        if (confirm(`Are you sure you want to delete this entry?\n(This cannot be undone!)`)) {
            $.get(`${deleteURL}${accomp_id}`, function () { })
                .done(function (response) {
                    createAlert("Accomplishment has been removed.", key = "", type = "warning");
                    createAccomplishmentsTable(length = 15, start = currentIndex, search = searchBar.value);
                })
                .fail(function (err) {
                    createAlert(xhr.responseText, key = "", type = "danger");
                })
        }
    });

    $(`#repeat-accomp-${data["pk"]}`).click(function (event) {
        let _data = $(this).val().replaceAll(`'`, `"`).replaceAll(`None`, `null`).replaceAll(`False`, `false`)
        accomplishmentStorage = JSON.parse(_data)
        closePopup();
        openPopup("repeat-accomp-popup");
        prepareRepeat()
    });

    $(`#edit-accomp-${data["pk"]}`).click(function (event) {
        selectedAccomplishment = $(this).val();
        currentAJAXURL = editAccompURL;

        let AJAXData = { csrfmiddlewaretoken: '{{ csrf_token }}' };

        $.when(basicAJAX(type = "POST", url = `${getAccompURL}${$(this).val()}`, data = AJAXData))
            .done(function (accompData) {
                if (accompData != null) {
                    openPopup("edit-accomp-popup");

                    // Fill the fields with the obtained data
                    var fields = ['measurement', "measurement_quantity", "date_from_day", "date_from_month",
                        "date_from_year", "date_to_day", "date_to_month", "date_to_year"]

                    fields.forEach(function (field) {
                        $(`#id_${field}`).val(accompData[field]);
                    });

                    $('#edit-accomp-popup #edit-accomp-name').text(accompData["name"]);
                    document.getElementById('edit-accomp-icon').className = `bi bi-${accompData["icon"]}`;

                    $('#edit-accomp-created').text(new Date(accompData["created"]).toLocaleDateString(language, {
                        weekday: "short", year: "numeric",
                        month: "short", day: "numeric",
                    }));

                    $(`#id_measurement`).prop("disabled", true)
                    // If the user has not Measurement type but a quantity specified, use x (amount of times)
                    if (accompData['measurement'] == null) {
                        $(`#id_measurement`).val("x");
                    }
                }
            });
    });
}

// "Previous" button = offset search by -15; "Next" button = offset search by +15;
$("#previous-button").click(function(event) { createAccomplishmentsTable(15, currentIndex-15, searchBar.value, searchSelector); });
$("#next-button").click(function(event) { createAccomplishmentsTable(15, currentIndex+15, searchBar.value, searchSelector); });

// Automatically run after a short period,
// and only make a query if the user made an input since then.
var previousSearch = ""
function updateSearch() {
    if (previousSearch != searchBar.value){
        previousSearch = searchBar.value;
        searchText = new RegExp(`(${searchBar.value})`,'gi');
        createAccomplishmentsTable(15, 0, searchBar.value, searchSelector);
    }
    setTimeout(function() { updateSearch() }, 300);
}
updateSearch()

// Run search immediately if they pressed enter (filter-form) or changed the filter selector (filter-selector)
$("#filter-form").submit(function(event) {
    event.preventDefault();
    searchText = new RegExp(`(${searchBar.value})`,'gi');
    createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
});

$("#filter-selector").change(function(event) {
    searchSelector = document.getElementById("filter-selector").value;
    createAccomplishmentsTable(15, 1, searchBar.value, searchSelector);
});
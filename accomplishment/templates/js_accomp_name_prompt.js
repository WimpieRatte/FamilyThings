/* Duplicate Check */
var nameField = document.getElementById("lb-new-accomp-prompt")
var submitButton = document.getElementById("btn-create-new");
var repeatButton = document.getElementById("btn-repeat");

var nameAvailableText = document.getElementById("lb-name-available");
var nameTakenText = document.getElementById("lb-name-taken-prompt");
var foundAccompText = document.getElementById("found-accomp");

var accomplishmentStorage = null;

// Get Accomplishment names
let AJAXData = {csrfmiddlewaretoken: '{{ csrf_token }}'};
$.when( basicAJAX(type="POST", url=`{% url 'accomplishment:get_names' %}`, data=AJAXData) )
    .done(function( accompData ) {
        let dataList = document.getElementById("accomp-suggestions");
        accompData["name"].forEach(function(name) {
            dataList.appendChild(document.createElement("option")).value = name[0]
        });
    })

// Open Name Prompt
$("#add-new-button").click(function(event) {
    event.preventDefault();
    resetNamePrompt();
    openPopup("name-prompt-popup");
});

/*$("#btn-create-new").click(function(event) {
    nameField.value = ""
    closePopup()
    openPopup("name-prompt-popup");
});*/

function resetNamePrompt() {
    accomplishmentStorage = null
    nameField.value = ""
    repeatButton.style.display = "none";
    nameAvailableText.style.display = "none";
    nameTakenText.style.display = "none";
    foundAccompText.textContent = "";
    foundAccompText.className = "";
    submitButton.disabled = true;
    repeatButton.disabled = true;
}

$("#name-prompt-popup #btn-abort").click(function(event) { 
    resetNamePrompt();
    closePopup();
});

$("#name-prompt-popup #btn-repeat").click(function(event) {
    if (accomplishmentStorage != null){
        closePopup();
        openPopup("repeat-accomp-popup");
        prepareRepeat()
        // Only run this after carrying all the nesssiary accomplishment data
        resetNamePrompt();
    }
});

var previousName = ""
function nameCheckAvailable(enforceCheck = false) {
    if (nameField.value.length > 0 && (previousName != nameField.value || enforceCheck)){
        previousName = nameField.value;

        $.ajax({ 
            type: 'POST', url: `${nameCheckURL}${nameField.value}`, data: {
                csrfmiddlewaretoken: '{{ csrf_token }}'},
            success: function(result) {
                submitButton.style.display = "none";
                nameAvailableText.style.display = "none";

                repeatButton.style.display = "block";
                repeatButton.disabled = false;
                nameTakenText.style.display = "block";
                foundAccompText.textContent = result["name"];
                foundAccompText.className = `bi bi-${result["icon"]} h5`;
                
                selectedAccomplishment = result["ID"];
                accomplishmentStorage = result
            },
            error: function(xhr, errmsg, err) {
                submitButton.style.display = "block";
                submitButton.disabled = false;
                nameAvailableText.style.display = "block";

                repeatButton.style.display = "none";
                nameTakenText.style.display = "none";
                foundAccompText.textContent = "";
                foundAccompText.className = "";

                selectedAccomplishment = null;
                accomplishmentStorage = null;
            }
        });
    }
    setTimeout(function() { nameCheckAvailable() }, 1000);
}
nameCheckAvailable();

$("#lb-new-accomp-prompt").keyup(function(event) {
    submitButton.disabled = true;
    repeatButton.disabled = true;
    foundAccompText.textContent = "";
    foundAccompText.className = "";
    nameTakenText.style.display = "none";
    nameAvailableText.style.display = "none";
});


document.getElementById("lb-new-accomp-prompt").addEventListener("keydown", function(event) {
    if(event.key === 'Enter') {
        nameCheckAvailable(enforceCheck = true); 
        submitButton.click();
        repeatButton.click();
    }
})
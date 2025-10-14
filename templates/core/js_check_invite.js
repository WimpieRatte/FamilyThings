var currentToken = ""
var previousInput = ""
var inviteField = document.getElementById("id_invite_code");
var inviteButton = null

function tokenCheckValid() {
    if (inviteField.value.length > 0 && previousInput != inviteField.value){
        previousInput = inviteField.value;

        $.ajax({ 
            type: 'POST', url: `{% url 'core:check_invite' %}`, data: {
                csrfmiddlewaretoken: '{{ csrf_token }}',
                token: inviteField.value
            },
            success: function(result) {
                inviteField.readOnly = true;
                inviteField.className = inviteField.className += " bg-success"
                if (inviteButton) { inviteButton.disabled = false; }
                currentToken = inviteField.value;
            },
            error: function(xhr, errmsg, err) {

            }
        });
    }
    setTimeout(function() { tokenCheckValid() }, 1000);
}
tokenCheckValid();
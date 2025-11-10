document.getElementById("continueBtn").addEventListener("click", function() {
    const sessionId = document.getElementById("sessionInput").value.trim();
    if(!sessionId) {
        alert("⚠️ Please enter your session ID!");
        return;
    }
    // Redirect to Flask start route with POST
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/start";
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = "sessionid";
    input.value = sessionId;
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
});
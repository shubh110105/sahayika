document
    .getElementById("registerForm")
    .addEventListener("submit", async function (event) {

        event.preventDefault();

        const message = document.getElementById("message");

        const data = {
            full_name: document.getElementById("full_name").value,
            email: document.getElementById("email").value,
            phone: document.getElementById("phone").value,
            password: document.getElementById("password").value,
            role: document.getElementById("role").value
        };

        try {
            const response = await fetch("/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            showAlert(
                message,
                result.message || "Registration failed.",
                result.success ? "success" : "danger"
            );

            if (result.success) {
                document.getElementById("registerForm").reset();
            }

        } catch (error) {

            showAlert(
                message,
                "Something went wrong. Please try again.",
                "danger"
            );

            console.error(error);
        }
    });


// Messages are inserted as text, never as HTML.
function showAlert(container, text, type) {
    const alertBox = document.createElement("div");
    alertBox.className = `alert alert-${type}`;
    alertBox.textContent = text;
    container.replaceChildren(alertBox);
}

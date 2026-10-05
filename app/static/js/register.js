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

            if (result.success) {
                message.innerHTML = `
                    <div class="alert alert-success">
                        ${result.message}
                    </div>
                `;

                document.getElementById("registerForm").reset();
            } else {
                message.innerHTML = `
                    <div class="alert alert-danger">
                        ${result.message}
                    </div>
                `;
            }

        } catch (error) {

            message.innerHTML = `
                <div class="alert alert-danger">
                    Something went wrong. Please try again.
                </div>
            `;

            console.error(error);
        }
    });
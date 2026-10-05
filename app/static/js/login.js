document
    .getElementById("loginForm")
    .addEventListener("submit", async function (event) {

        event.preventDefault();

        const message = document.getElementById("message");

        const data = {
            email: document.getElementById("email").value,
            password: document.getElementById("password").value
        };

        try {

            const response = await fetch("/auth/login", {
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

                console.log("Logged in user:", result);

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
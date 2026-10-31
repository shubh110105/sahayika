
document
    .getElementById("loginForm")
    .addEventListener("submit", async function (event) {
        event.preventDefault();

        const message = document.getElementById("message");

        const data = {
            email: document.getElementById("email").value.trim(),
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

            if (!response.ok || !result.success) {
                message.innerHTML = "";

                const alert = document.createElement("div");
                alert.className = "alert alert-danger";
                alert.textContent = result.message || "Login failed.";
                message.appendChild(alert);
                return;
            }

            // Redirect users according to their account role.
            const dashboardRoutes = {
                CUSTOMER: "/customer/dashboard",
                MAID: "/maid/dashboard",
                ADMIN: "/admin/dashboard"
            };

            const dashboardUrl = dashboardRoutes[result.role];

            if (!dashboardUrl) {
                message.innerHTML = "";

                const alert = document.createElement("div");
                alert.className = "alert alert-danger";
                alert.textContent =
                    "Login succeeded, but the dashboard for this role is not configured.";
                message.appendChild(alert);
                return;
            }

            window.location.assign(dashboardUrl);

        } catch (error) {
            message.innerHTML = "";

            const alert = document.createElement("div");
            alert.className = "alert alert-danger";
            alert.textContent =
                "Something went wrong. Please try again.";
            message.appendChild(alert);

            console.error("Login error:", error);
        }
    });

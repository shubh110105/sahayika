async function loadProfile() {

    try {

        const response = await fetch("/customer/profile");
        const result = await response.json();

        if (!result.success) {
            showMessage(result.message, "danger");
            return;
        }

        const profile = result.profile;

        document.getElementById("fullName").textContent =
            profile.full_name || "";

        document.getElementById("email").textContent =
            profile.email || "";

        document.getElementById("phone").textContent =
            profile.phone || "";

        document.getElementById("address").value =
            profile.address || "";

        document.getElementById("city").value =
            profile.city || "";

        document.getElementById("state").value =
            profile.state || "";

        document.getElementById("pincode").value =
            profile.pincode || "";

    } catch (error) {

        console.error(error);

        showMessage(
            "Unable to load profile.",
            "danger"
        );
    }
}


document
    .getElementById("profileForm")
    .addEventListener("submit", async function (event) {

        event.preventDefault();

        const data = {
            address: document.getElementById("address").value,
            city: document.getElementById("city").value,
            state: document.getElementById("state").value,
            pincode: document.getElementById("pincode").value
        };

        try {

            const response = await fetch(
                "/customer/profile",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(data)
                }
            );

            const result = await response.json();

            if (result.success) {

                showMessage(
                    result.message,
                    "success"
                );

            } else {

                showMessage(
                    result.message,
                    "danger"
                );
            }

        } catch (error) {

            console.error(error);

            showMessage(
                "Unable to save profile.",
                "danger"
            );
        }
    });


function showMessage(message, type) {

    document.getElementById("message").innerHTML = `
        <div class="alert alert-${type}">
            ${message}
        </div>
    `;
}


loadProfile();
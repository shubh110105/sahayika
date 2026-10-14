async function loadProfile() {

    try {

        const response = await fetch("/maid/profile");
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

        document.getElementById("pincode").value =
            profile.pincode || "";

        document.getElementById("experienceYears").value =
            profile.experience_years ?? "";

        document.getElementById("bio").value =
            profile.bio || "";

        updateVerificationStatus(
            profile.verification_status
        );

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
            pincode: document.getElementById("pincode").value,
            experience_years:
                document.getElementById("experienceYears").value,
            bio: document.getElementById("bio").value
        };

        try {

            const response = await fetch(
                "/maid/profile",
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

                await loadProfile();

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


function updateVerificationStatus(status) {

    const element =
        document.getElementById("verificationStatus");

    if (!status) {

        element.textContent = "Not Submitted";
        element.className = "badge bg-secondary";

        return;
    }

    element.textContent = status;

    if (status === "VERIFIED") {
        element.className = "badge bg-success";
    }
    else if (status === "REJECTED") {
        element.className = "badge bg-danger";
    }
    else if (status === "SUSPENDED") {
        element.className = "badge bg-dark";
    }
    else {
        element.className = "badge bg-warning text-dark";
    }
}


function showMessage(message, type) {

    document.getElementById("message").innerHTML = `
        <div class="alert alert-${type}">
            ${message}
        </div>
    `;
}


loadProfile();
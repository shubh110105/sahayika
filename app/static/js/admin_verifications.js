
const requestsContainer = document.getElementById("requests");
const messageContainer = document.getElementById("message");

async function loadRequests() {
    requestsContainer.textContent = "Loading requests...";

    try {
        const response = await fetch("/verification/admin/pending");
        const result = await response.json();

        if (!response.ok || !result.success) {
            requestsContainer.textContent = "";
            showMessage(result.message || "Unable to load requests.", "danger");
            return;
        }

        renderRequests(result.verifications || []);
    } catch (error) {
        console.error(error);
        requestsContainer.textContent = "";
        showMessage("Unable to connect to the server.", "danger");
    }
}

function renderRequests(requests) {
    requestsContainer.replaceChildren();

    if (requests.length === 0) {
        requestsContainer.textContent = "No pending verification requests.";
        return;
    }

    requests.forEach((item) => {
        const card = document.createElement("div");
        card.className = "card shadow-sm mb-3";

        const body = document.createElement("div");
        body.className = "card-body";

        const heading = document.createElement("h5");
        heading.textContent = item.full_name || "Unnamed maid";

        const details = document.createElement("p");
        details.textContent =
            `Verification ID: ${item.verification_id} | ` +
            `Maid ID: ${item.maid_id} | Status: ${item.status}`;

        const contact = document.createElement("p");
        contact.textContent =
            `Email: ${item.email || "—"} | Phone: ${item.phone || "—"}`;

        const experience = document.createElement("p");
        experience.textContent =
            `City: ${item.city || "—"} | Experience: ${item.experience_years ?? "—"} years`;

        const remarks = document.createElement("textarea");
        remarks.className = "form-control mb-3";
        remarks.placeholder = "Remarks (required for rejection)";
        remarks.setAttribute("aria-label", "Admin verification remarks");

        const verifyButton = document.createElement("button");
        verifyButton.className = "btn btn-success me-2";
        verifyButton.textContent = "Verify";
        verifyButton.addEventListener("click", () => {
            reviewRequest(item.verification_id, "VERIFIED", remarks.value);
        });

        const rejectButton = document.createElement("button");
        rejectButton.className = "btn btn-danger";
        rejectButton.textContent = "Reject";
        rejectButton.addEventListener("click", () => {
            reviewRequest(item.verification_id, "REJECTED", remarks.value);
        });

        body.append(heading, details, contact, experience, remarks,
                    verifyButton, rejectButton);
        card.appendChild(body);
        requestsContainer.appendChild(card);
    });
}

async function reviewRequest(verificationId, status, remarks) {
    if (status === "REJECTED" && !remarks.trim()) {
        showMessage("Please enter remarks before rejecting.", "warning");
        return;
    }

    const confirmed = window.confirm(
        `Are you sure you want to mark request ${verificationId} as ${status}?`
    );

    if (!confirmed) return;

    try {
        const response = await fetch(
            `/verification/admin/${verificationId}/review`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ status, remarks })
            }
        );

        const result = await response.json();

        showMessage(
            result.message || "Review completed.",
            response.ok ? "success" : "danger"
        );

        if (response.ok && result.success) {
            await loadRequests();
        }
    } catch (error) {
        console.error(error);
        showMessage("Unable to submit the review.", "danger");
    }
}

function showMessage(text, type) {
    const alert = document.createElement("div");
    alert.className = `alert alert-${type}`;
    alert.textContent = text;

    messageContainer.replaceChildren(alert);
}

loadRequests();

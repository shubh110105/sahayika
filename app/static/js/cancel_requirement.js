
document.addEventListener("DOMContentLoaded", () => {
    const cancelButton = document.getElementById(
        "cancelRequirementButton"
    );
    const message = document.getElementById(
        "cancelRequirementMessage"
    );

    if (!cancelButton || !message) {
        return;
    }

    cancelButton.addEventListener("click", async () => {
        const confirmed = window.confirm(
            "Are you sure you want to cancel this requirement? " +
            "This action cannot be undone."
        );

        if (!confirmed) {
            return;
        }

        const requirementId = cancelButton.dataset.requirementId;

        cancelButton.disabled = true;
        message.textContent = "Cancelling requirement...";
        message.className = "text-muted mt-2 mb-0";

        try {
            const response = await fetch(
                `/requirements/${requirementId}/cancel`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message || "Unable to cancel requirement."
                );
            }

            message.textContent = result.message;
            message.className = "text-success mt-2 mb-0";

            // Refresh to show the updated requirement status.
            window.location.reload();

        } catch (error) {
            message.textContent = error.message;
            message.className = "text-danger mt-2 mb-0";
            cancelButton.disabled = false;
        }
    });
});

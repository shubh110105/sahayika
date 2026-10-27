
document.addEventListener("DOMContentLoaded", function () {
    const submitButton = document.getElementById(
        "submitRequirementButton"
    );

    const message = document.getElementById(
        "submitRequirementMessage"
    );

    // This script is also loaded on pages without the submission button.
    if (!submitButton || !message) {
        return;
    }

    submitButton.addEventListener("click", async function () {
        const requirementId = submitButton.dataset.requirementId;

        submitButton.disabled = true;
        message.textContent = "Submitting requirement...";
        message.className = "mt-2 mb-0 text-muted";

        try {
            const response = await fetch(
                `/requirements/${requirementId}/submit`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({})
                }
            );

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message || "Unable to submit requirement."
                );
            }

            message.textContent = result.message;
            message.className = "mt-2 mb-0 text-success";

            // Refresh the requirement details to show its new status.
            window.location.reload();
        } catch (error) {
            message.textContent = error.message;
            message.className = "mt-2 mb-0 text-danger";
            submitButton.disabled = false;
        }
    });
});

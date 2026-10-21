
document.addEventListener("DOMContentLoaded", () => {
    const reviewButton = document.getElementById("salaryReviewButton");
    const message = document.getElementById("salaryReviewMessage");

    if (!reviewButton || !message) {
        return;
    }

    reviewButton.addEventListener("click", async () => {
        const requirementId = reviewButton.dataset.requirementId;

        reviewButton.disabled = true;
        message.textContent = "Submitting salary review request...";

        try {
            const response = await fetch(
                `/requirements/${requirementId}/salary-review`,
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
                    result.message || "Unable to submit the request."
                );
            }

            message.textContent = result.message;
            message.className = "text-success mt-2 mb-0";

            // Reload to display the updated requirement status.
            window.location.reload();

        } catch (error) {
            message.textContent = error.message;
            message.className = "text-danger mt-2 mb-0";
            reviewButton.disabled = false;
        }
    });
});

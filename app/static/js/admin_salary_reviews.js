
document.addEventListener("DOMContentLoaded", async () => {
    // Get the HTML elements used to display requests and status messages.
    const tableBody = document.getElementById("salaryReviewTableBody");
    const message = document.getElementById("reviewMessage");

    // Show a message if the required HTML elements are missing.
    if (!tableBody || !message) {
        console.error("Salary review table elements were not found.");
        return;
    }

    try {
        // Fetch pending salary review requests from the Admin-only API.
        const response = await fetch("/admin/salary-reviews");
        const result = await response.json();

        // Stop if the server reports an error.
        if (!response.ok || !result.success) {
            throw new Error(
                result.message || "Unable to load salary review requests."
            );
        }

        const requests = result.requests || [];

        // Clear existing rows before displaying the latest results.
        tableBody.replaceChildren();

        // Display a friendly message when there are no pending requests.
        if (requests.length === 0) {
            message.textContent =
                "There are no pending salary review requests.";
            message.className = "alert alert-success";
            return;
        }

        message.textContent =
            `${requests.length} pending salary review request(s).`;
        message.className = "alert alert-info";

        // Create a table row for each pending salary review request.
        requests.forEach((item) => {
            const row = document.createElement("tr");

            // Combine the address fields into one readable location.
            const location = [
                item.location_address,
                item.city,
                item.state,
                item.pincode
            ].filter(Boolean).join(", ");

            // Format the salary as Indian Rupees with two decimal places.
            const salary = item.estimated_monthly_salary == null
                ? "Not available"
                : `₹${Number(item.estimated_monthly_salary).toLocaleString(
                    "en-IN",
                    {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }
                )}`;

            // Display the timestamp associated with the salary estimate.
            const requestedOn = item.salary_estimated_at
                ? new Date(item.salary_estimated_at).toLocaleString("en-IN")
                : "Not available";

            // Add the basic requirement details to the row.
            [
                item.requirement_id,
                location || "Not available",
                salary,
                requestedOn
            ].forEach((value) => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            // Create the Actions cell for the Admin's decision buttons.
            const actionsCell = document.createElement("td");
            actionsCell.className = "text-nowrap";

            // Create a reusable function for each decision button.
            function createDecisionButton(label, decision, buttonClass) {
                const button = document.createElement("button");

                button.type = "button";
                button.textContent = label;
                button.className = `btn ${buttonClass} btn-sm me-2 mb-1`;

                // Submit the selected decision to the Admin API.
                button.addEventListener("click", async () => {
                    const confirmation = window.confirm(
                        `Are you sure you want to ${label.toLowerCase()} ` +
                        `for requirement #${item.requirement_id}?`
                    );

                    // Do nothing if the Admin cancels the confirmation.
                    if (!confirmation) {
                        return;
                    }

                    // Prevent duplicate submissions while the request is processing.
                    const buttons = actionsCell.querySelectorAll("button");
                    buttons.forEach((currentButton) => {
                        currentButton.disabled = true;
                    });

                    message.textContent = "Saving Admin decision...";
                    message.className = "alert alert-info";

                    try {
                        // Send the selected decision to the protected Flask route.
                        const decisionResponse = await fetch(
                            `/admin/salary-reviews/${item.requirement_id}/decision`,
                            {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json"
                                },
                                body: JSON.stringify({ decision })
                            }
                        );

                        const decisionResult = await decisionResponse.json();

                        // Show any validation or server error returned by Flask.
                        if (!decisionResponse.ok || !decisionResult.success) {
                            throw new Error(
                                decisionResult.message ||
                                "Unable to save the decision."
                            );
                        }

                        // Tell the Admin the decision was saved.
                        message.textContent = decisionResult.message;
                        message.className = "alert alert-success";

                        // Reload the queue so the resolved request disappears.
                        await loadSalaryReviewRequests();

                    } catch (error) {
                        // Keep the request visible and allow the Admin to retry.
                        message.textContent = error.message;
                        message.className = "alert alert-danger";

                        buttons.forEach((currentButton) => {
                            currentButton.disabled = false;
                        });
                    }
                });

                return button;
            }

            // Approval retains the existing salary estimate.
            const approveButton = createDecisionButton(
                "Approve Estimate",
                "APPROVED",
                "btn-success"
            );

            // Reassessment records the need for further review.
            const reassessButton = createDecisionButton(
                "Request Reassessment",
                "REASSESSMENT_REQUESTED",
                "btn-warning"
            );

            actionsCell.appendChild(approveButton);
            actionsCell.appendChild(reassessButton);
            row.appendChild(actionsCell);

            // Add the completed row to the table.
            tableBody.appendChild(row);
        });

    } catch (error) {
        // Display errors encountered while initially loading the queue.
        message.textContent = error.message;
        message.className = "alert alert-danger";
    }
});

// Reload the pending requests after a decision has been saved.
async function loadSalaryReviewRequests() {
    // Refresh the page to reload the server-rendered data and current queue.
    window.location.reload();
}

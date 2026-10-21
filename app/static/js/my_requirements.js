
document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("requirementsContainer");
    const message = document.getElementById("requirementsMessage");

    function showMessage(text, type) {
        message.textContent = text;
        message.className = `alert alert-${type}`;
    }

    function createCell(text, className = "") {
        const cell = document.createElement("td");
        cell.textContent = text ?? "—";
        if (className) {
            cell.className = className;
        }
        return cell;
    }

    function formatDate(value) {
        if (!value) return "—";

        const date = new Date(value);
        if (Number.isNaN(date.getTime())) {
            return String(value);
        }

        return date.toLocaleDateString();
    }

    try {
        const response = await fetch("/requirements/");
        const result = await response.json();

        if (!response.ok || !result.success) {
            container.textContent =
                result.message || "Unable to load requirements.";
            showMessage("Could not load your requirements.", "danger");
            return;
        }

        const requirements = result.requirements || [];

        if (requirements.length === 0) {
            container.textContent =
                "You haven't created any household requirements yet.";
            return;
        }

        const table = document.createElement("div");
        table.className = "table-responsive";

        const tableElement = document.createElement("table");
        tableElement.className =
            "table table-bordered table-hover align-middle bg-white";

        const thead = document.createElement("thead");
        thead.className = "table-light";

        const headerRow = document.createElement("tr");

        [
        "Reference ID",
        "Location",
        "Experience",
        "Estimated Salary",
        "Status",
        "Created"
    ].forEach(title => {
            const th = document.createElement("th");
            th.scope = "col";
            th.textContent = title;
            headerRow.appendChild(th);
        });

        thead.appendChild(headerRow);
        tableElement.appendChild(thead);

        const tbody = document.createElement("tbody");

        requirements.forEach(requirement => {
            const row = document.createElement("tr");

            
            const referenceCell = document.createElement("td");

            const detailsLink = document.createElement("a");
            detailsLink.href = `/requirements/${requirement.requirement_id}`;
            detailsLink.textContent = `#${requirement.requirement_id}`;
            detailsLink.className = "fw-semibold text-decoration-none";

            referenceCell.appendChild(detailsLink);
            row.appendChild(referenceCell);


            const location = [
                requirement.location_address,
                requirement.city,
                requirement.state,
                requirement.pincode
            ].filter(Boolean).join(", ");

            row.appendChild(createCell(location || "—"));

            const experience =
                requirement.experience_requirement == null
                    ? "No minimum"
                    : `${requirement.experience_requirement} year(s)`;

            row.appendChild(createCell(experience));
            const salary = requirement.estimated_monthly_salary;

const salaryText =
    salary == null
        ? "Not estimated"
        : `₹${Number(salary).toLocaleString("en-IN", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;

row.appendChild(createCell(salaryText));
          const statusCell = document.createElement("td");
const badge = document.createElement("span");
badge.className = "badge text-bg-secondary";

            const statusLabels = {
                DRAFT: "Draft",
                SALARY_ESTIMATED: "Salary estimate ready",
                SALARY_REVIEW_REQUESTED: "Salary review requested",
                SUBMITTED: "Submitted",
                UNDER_REVIEW: "Under review",
                MAID_ASSIGNED: "Maid assigned",
                WAITING_FOR_MAID: "Waiting for maid response",
                MAID_ACCEPTED: "Maid accepted",
                CUSTOMER_CONFIRMED: "Awaiting admin confirmation",
                ADMIN_CONFIRMED: "Confirmed",
                NO_MATCH_AVAILABLE: "No suitable maid available",
                CANCELLED: "Cancelled",
                COMPLETED: "Completed"
            };

            const status = requirement.status || "UNKNOWN";
            badge.textContent = statusLabels[status] || status;
            statusCell.appendChild(badge);
            row.appendChild(statusCell);
            row.appendChild(createCell(formatDate(requirement.created_at)));

            tbody.appendChild(row);
        });

        tableElement.appendChild(tbody);
        table.appendChild(tableElement);
        container.replaceChildren(table);

    } catch (error) {
        container.textContent =
            "A server connection error occurred while loading requirements.";
        showMessage("Could not connect to the server.", "danger");
    }
});

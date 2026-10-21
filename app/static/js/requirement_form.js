
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("requirementForm");
    const scheduleContainer = document.getElementById("scheduleContainer");
    const addScheduleButton = document.getElementById("addScheduleButton");
    const formMessage = document.getElementById("formMessage");
    const submitButton = document.getElementById("submitButton");

    const weekdays = [
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY"
    ];

    function addScheduleRow() {
        const row = document.createElement("div");
        row.className = "row align-items-end mb-3 schedule-row";

        const dayColumn = document.createElement("div");
        dayColumn.className = "col-md-4 mb-2";

        const dayLabel = document.createElement("label");
        dayLabel.className = "form-label";
        dayLabel.textContent = "Day";

        const daySelect = document.createElement("select");
        daySelect.className = "form-select schedule-day";
        daySelect.required = true;

        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "Select day";
        placeholder.disabled = true;
        placeholder.selected = true;
        daySelect.appendChild(placeholder);

        weekdays.forEach(day => {
            const option = document.createElement("option");
            option.value = day;
            option.textContent =
                day.charAt(0) + day.slice(1).toLowerCase();
            daySelect.appendChild(option);
        });

        dayLabel.appendChild(daySelect);
        dayColumn.appendChild(dayLabel);

        const startColumn = document.createElement("div");
        startColumn.className = "col-md-3 mb-2";

        const startLabel = document.createElement("label");
        startLabel.className = "form-label";
        startLabel.textContent = "Start time";

        const startInput = document.createElement("input");
        startInput.type = "time";
        startInput.className = "form-control schedule-start";
        startInput.required = true;

        startLabel.appendChild(startInput);
        startColumn.appendChild(startLabel);

        const endColumn = document.createElement("div");
        endColumn.className = "col-md-3 mb-2";

        const endLabel = document.createElement("label");
        endLabel.className = "form-label";
        endLabel.textContent = "End time";

        const endInput = document.createElement("input");
        endInput.type = "time";
        endInput.className = "form-control schedule-end";
        endInput.required = true;

        endLabel.appendChild(endInput);
        endColumn.appendChild(endLabel);

        const removeColumn = document.createElement("div");
        removeColumn.className = "col-md-2 mb-2";

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.className = "btn btn-outline-danger w-100";
        removeButton.textContent = "Remove";

        removeButton.addEventListener("click", () => {
            if (scheduleContainer.children.length === 1) {
                showMessage(
                    "At least one schedule is required.",
                    "danger"
                );
                return;
            }

            row.remove();
            clearMessage();
        });

        removeColumn.appendChild(removeButton);

        row.append(
            dayColumn,
            startColumn,
            endColumn,
            removeColumn
        );

        scheduleContainer.appendChild(row);
    }

    function showMessage(message, type) {
        formMessage.textContent = message;
        formMessage.className = `alert alert-${type}`;
    }

    function clearMessage() {
        formMessage.textContent = "";
        formMessage.className = "alert d-none";
    }

    addScheduleButton.addEventListener("click", addScheduleRow);

    addScheduleRow();

    form.addEventListener("submit", async event => {
        event.preventDefault();
        clearMessage();

        const selectedServices = Array.from(
            document.querySelectorAll(".service-option:checked")
        ).map(input => Number(input.value));

        if (selectedServices.length === 0) {
            showMessage("Select at least one service.", "danger");
            return;
        }

        const schedules = Array.from(
            document.querySelectorAll(".schedule-row")
        ).map(row => ({
            day_of_week: row.querySelector(".schedule-day").value,
            start_time: row.querySelector(".schedule-start").value,
            end_time: row.querySelector(".schedule-end").value
        }));

        for (const schedule of schedules) {
            if (!schedule.day_of_week ||
                !schedule.start_time ||
                !schedule.end_time) {
                showMessage(
                    "Complete every schedule's day and time fields.",
                    "danger"
                );
                return;
            }

            if (schedule.start_time >= schedule.end_time) {
                showMessage(
                    "End time must be later than start time.",
                    "danger"
                );
                return;
            }
        }

        const experienceValue =
            document.getElementById("experience_requirement").value;

        const payload = {
            location_address:
                document.getElementById("location_address").value.trim(),
            city: document.getElementById("city").value.trim(),
            state: document.getElementById("state").value.trim(),
            pincode: document.getElementById("pincode").value.trim(),
            experience_requirement:
                experienceValue === "" ? null : Number(experienceValue),
            additional_requirements:
                document.getElementById("additional_requirements").value.trim(),
            service_ids: selectedServices,
            schedules: schedules
        };

        submitButton.disabled = true;
        submitButton.textContent = "Submitting...";

        try {
            const response = await fetch("/requirements/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                showMessage(
                    result.message || "Could not create requirement.",
                    "danger"
                );
                return;
            }

            showMessage(
                `Requirement created successfully. Reference ID: ${result.requirement_id}`,
                "success"
            );

            form.reset();
            scheduleContainer.replaceChildren();
            addScheduleRow();

        } catch (error) {
            showMessage(
                "Could not connect to the server. Please try again.",
                "danger"
            );
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = "Submit Requirement";
        }
    });
});


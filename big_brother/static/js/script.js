// Dynamic form handling for phone and email formsets
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for formset buttons
    const addPhoneButton = document.getElementById('add-phone');
    const addEmailButton = document.getElementById('add-email');

    if (addPhoneButton) {
        addPhoneButton.addEventListener('click', function() {
            const totalForms = document.getElementById('id_phone_set-TOTAL_FORMS');
            const formNum = parseInt(totalForms.value);
            const formRow = document.querySelector('#phone-formset .form-row:last-child');
            const newRow = formRow.cloneNode(true);

            // Update form indices
            newRow.innerHTML = newRow.innerHTML.replace(/phone_set-\d+-/g, `phone_set-${formNum}-`);
            newRow.innerHTML = newRow.innerHTML.replace(/id_phone_set-\d+-/g, `id_phone_set-${formNum}-`);

            // Clear input values
            const numberInput = newRow.querySelector('input[type="text"]');
            if (numberInput) numberInput.value = '';

            // Remove delete checkbox for new forms
            const deleteCheckbox = newRow.querySelector('input[type="checkbox"]');
            if (deleteCheckbox) {
                deleteCheckbox.checked = false;
                deleteCheckbox.style.display = 'none';
                const deleteLabel = newRow.querySelector('label');
                if (deleteLabel) deleteLabel.style.display = 'none';
            }

            // Append new row
            document.getElementById('phone-formset').appendChild(newRow);
            totalForms.value = formNum + 1;
        });
    }

    if (addEmailButton) {
        addEmailButton.addEventListener('click', function() {
            const totalForms = document.getElementById('id_email_set-TOTAL_FORMS');
            const formNum = parseInt(totalForms.value);
            const formRow = document.querySelector('#email-formset .form-row:last-child');
            const newRow = formRow.cloneNode(true);

            // Update form indices
            newRow.innerHTML = newRow.innerHTML.replace(/email_set-\d+-/g, `email_set-${formNum}-`);
            newRow.innerHTML = newRow.innerHTML.replace(/id_email_set-\d+-/g, `id_email_set-${formNum}-`);

            // Clear input values
            const emailInput = newRow.querySelector('input[type="email"]');
            if (emailInput) emailInput.value = '';

            // Remove delete checkbox for new forms
            const deleteCheckbox = newRow.querySelector('input[type="checkbox"]');
            if (deleteCheckbox) {
                deleteCheckbox.checked = false;
                deleteCheckbox.style.display = 'none';
                const deleteLabel = newRow.querySelector('label');
                if (deleteLabel) deleteLabel.style.display = 'none';
            }

            // Append new row
            document.getElementById('email-formset').appendChild(newRow);
            totalForms.value = formNum + 1;
        });
    }
});

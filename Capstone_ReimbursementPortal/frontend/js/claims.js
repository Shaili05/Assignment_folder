async function handleSubmitClaim() {
    try {
        const data = {
            employeeId: parseInt(
                document.getElementById('employeeId').value
            ),
            amount: parseFloat(
                document.getElementById('amount').value
            ),
            date: document.getElementById('date').value,
            description: document.getElementById('description').value
        };

        if (!data.employeeId || data.employeeId <= 0) {
            showMessage('submitMsg',
                'Please enter a valid Employee ID', true);
            return;
        }
        if (!data.amount || data.amount <= 0) {
            showMessage('submitMsg',
                'Please enter a valid amount', true);
            return;
        }
        if (!data.date) {
            showMessage('submitMsg', 'Please select a date', true);
            return;
        }
        if (!data.description) {
            showMessage('submitMsg',
                'Please enter a description', true);
            return;
        }

        const result = await submitClaim(data);

        if (result.status === 'success') {
            showMessage('submitMsg', 'Claim submitted successfully!');
        } else {
            showMessage('submitMsg',
                result.message || 'Something went wrong', true);
        }
    } catch (err) {
        showMessage('submitMsg', 'Could not connect to server', true);
    }
}

async function handleViewClaims() {
    try {
        const empId = document.getElementById('viewEmployeeId').value;

        if (!empId || parseInt(empId) <= 0) {
            showMessage('claimsMsg',
                'Please enter a valid Employee ID', true);
            return;
        }

        const result = await getMyClaims(empId);

        if (result.status === 'success') {
            const claims = result.data.content;

            if (claims.length === 0) {
                showMessage('claimsMsg', 'No claims found', true);
                return;
            }

            let rows = '';
            claims.forEach(claim => {
                rows += `
                    <tr>
                        <td>${claim.id}</td>
                        <td>₹${claim.amount}</td>
                        <td>${claim.date}</td>
                        <td>${claim.description}</td>
                        <td class="${getStatusClass(claim.status)}">
                            ${claim.status}
                        </td>
                        <td>${claim.reviewerComment || '-'}</td>
                    </tr>
                `;
            });

            document.getElementById('claimsBody').innerHTML = rows;
            document.getElementById('claimsTable').style.display = 'table';
        } else {
            showMessage('claimsMsg',
                result.message || 'Something went wrong', true);
        }
    } catch (err) {
        showMessage('claimsMsg', 'Could not connect to server', true);
    }
}
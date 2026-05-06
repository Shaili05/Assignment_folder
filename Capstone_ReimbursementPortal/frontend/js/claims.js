if (!requireAuth('EMPLOYEE')) {
    window.location.href = 'login.html';
}

window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        window.location.replace(window.location.href);
    }
});

setHeaderUserName();

const CURRENT_EMPLOYEE_ID = parseInt(
    localStorage.getItem('userId'), 10);

handleViewClaims();

async function handleSubmitClaim() {
    const amount = parseFloat(
        document.getElementById('amount').value
    );
    const date = document.getElementById('date').value;
    const description = document
        .getElementById('description').value.trim();

    if (!amount || amount <= 0) {
        showMessage('submitMsg',
            'Please enter a valid amount', true);
        return;
    }
    if (amount > 100000) {
        showMessage('submitMsg',
            'Amount cannot exceed ₹100,000', true);
        return;
    }
    if (!date) {
        showMessage('submitMsg', 'Please select a date', true);
        return;
    }
    if (!description) {
        showMessage('submitMsg',
            'Please enter a description', true);
        return;
    }

    const data = {
        employeeId: CURRENT_EMPLOYEE_ID,
        amount,
        date,
        description
    };

    try {
        const result = await submitClaim(data);
        if (result.status === 'success') {
            showMessage('submitMsg',
                'Claim submitted successfully');
            document.getElementById('amount').value = '';
            document.getElementById('date').value = '';
            document.getElementById('description').value = '';
            handleViewClaims();
        } else {
            showMessage('submitMsg',
                result.message || 'Something went wrong', true);
        }
    } catch (err) {
        showMessage('submitMsg',
            'Could not connect to server', true);
    }
}

async function handleViewClaims() {
    try {
        const result = await getMyClaims(CURRENT_EMPLOYEE_ID);

        if (result.status === 'success') {
            const claims = result.data.content;

            if (claims.length === 0) {
                document.getElementById('claimsTable')
                    .style.display = 'none';
                document.getElementById('claimsEmpty')
                    .style.display = 'block';
                return;
            }

            let rows = '';
            claims.forEach(function(claim) {
                rows += '<tr>'
                    + '<td>' + claim.id + '</td>'
                    + '<td>&#x20B9;' + claim.amount + '</td>'
                    + '<td>' + claim.date + '</td>'
                    + '<td>' + claim.description + '</td>'
                    + '<td>' + getStatusBadge(claim.status) + '</td>'
                    + '<td>' + (claim.reviewerComment || '-') + '</td>'
                    + '</tr>';
            });

            document.getElementById('claimsBody').innerHTML = rows;
            document.getElementById('claimsTable')
                .style.display = 'table';
            document.getElementById('claimsEmpty')
                .style.display = 'none';
        } else {
            showMessage('claimsMsg',
                result.message || 'Failed to load claims', true);
        }
    } catch (err) {
        showMessage('claimsMsg',
            'Could not connect to server', true);
    }
}
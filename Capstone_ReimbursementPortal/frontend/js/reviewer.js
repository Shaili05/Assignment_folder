if (!requireAuth('MANAGER')) {
    window.location.href = 'login.html';
}

window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        window.location.replace(window.location.href);
    }
});

setHeaderUserName();

const CURRENT_REVIEWER_ID = parseInt(
    localStorage.getItem('userId'), 10
);

function handleLoadReviewerClaims() {
    loadReviewerClaims().catch(function(err) {
        console.error('Failed to load reviewer claims', err);
    });
}

function handleLoadManagerOwnClaims() {
    loadManagerOwnClaims().catch(function(err) {
        console.error('Failed to load own claims', err);
    });
}

handleLoadReviewerClaims();
handleLoadManagerOwnClaims();

async function loadReviewerClaims() {
    const result = await getReviewerClaims(CURRENT_REVIEWER_ID);

    if (result.status === 'success') {
        const claims = result.data.content;

        if (claims.length === 0) {
            document.getElementById('reviewerTable')
                .style.display = 'none';
            document.getElementById('reviewerEmpty')
                .style.display = 'block';
            document.getElementById('actionCard')
                .style.display = 'none';
            return;
        }

        let rows = '';
        claims.forEach(function(claim) {
            const empName = claim.employeeName
                ? String(claim.employeeName) : '-';
            const revComment = claim.reviewerComment
                ? String(claim.reviewerComment) : '-';
            const actionBtn = claim.status === 'SUBMITTED'
                ? '<button class="btn-small btn-action" onclick="'
                + 'prefillAction(' + claim.id + ')">'
                + 'Action</button>'
                : '<span class="done-label">Done</span>';

            rows += '<tr>'
                + '<td>' + claim.id + '</td>'
                + '<td>' + empName + '</td>'
                + '<td>&#x20B9;' + claim.amount + '</td>'
                + '<td>' + claim.date + '</td>'
                + '<td>' + claim.description + '</td>'
                + '<td>' + getStatusBadge(claim.status) + '</td>'
                + '<td>' + revComment + '</td>'
                + '<td>' + actionBtn + '</td>'
                + '</tr>';
        });

        document.getElementById('reviewerBody').innerHTML = rows;
        document.getElementById('reviewerTable')
            .style.display = 'table';
        document.getElementById('reviewerEmpty')
            .style.display = 'none';
        document.getElementById('actionCard')
            .style.display = 'block';
    } else {
        showMessage('reviewerMsg',
            result.message || 'Failed to load claims', true);
    }
}

function prefillAction(claimId) {
    const el = document.getElementById('claimId');
    if (el) {
        el.value = claimId;
        document.getElementById('actionCard')
            .scrollIntoView({ behavior: 'smooth' });
    }
}

async function handleApprove() {
    const claimIdEl = document.getElementById('claimId');
    const claimId = parseInt(claimIdEl.value, 10);
    const comment = document.getElementById('comment').value.trim();

    if (!claimId || claimId <= 0) {
        showMessage('actionMsg',
            'Please enter a valid Claim ID', true);
        return;
    }
    if (!comment) {
        showMessage('actionMsg', 'Comment is required', true);
        return;
    }

    const result = await approveClaim(
        claimId, CURRENT_REVIEWER_ID, comment);
    if (result.status === 'success') {
        showMessage('actionMsg', 'Claim approved successfully');
        document.getElementById('claimId').value = '';
        document.getElementById('comment').value = '';
        await loadReviewerClaims();
    } else {
        showMessage('actionMsg',
            result.message || 'Something went wrong', true);
    }
}

async function handleReject() {
    const claimIdEl = document.getElementById('claimId');
    const claimId = parseInt(claimIdEl.value, 10);
    const comment = document.getElementById('comment').value.trim();

    if (!claimId || claimId <= 0) {
        showMessage('actionMsg',
            'Please enter a valid Claim ID', true);
        return;
    }
    if (!comment) {
        showMessage('actionMsg',
            'Comment is required for rejection', true);
        return;
    }

    const result = await rejectClaim(
        claimId, CURRENT_REVIEWER_ID, comment);

    if (result.status === 'success') {
        showMessage('actionMsg', 'Claim rejected successfully');
        document.getElementById('claimId').value = '';
        document.getElementById('comment').value = '';
        await loadReviewerClaims();
    } else {
        showMessage('actionMsg',
            result.message || 'Something went wrong', true);
    }
}

async function loadManagerOwnClaims() {
    const result = await getManagerOwnClaims(CURRENT_REVIEWER_ID);

    if (result.status === 'success') {
        const claims = result.data.content;

        if (claims.length === 0) {
            document.getElementById('ownClaimsTable')
                .style.display = 'none';
            document.getElementById('ownClaimsEmpty')
                .style.display = 'block';
            return;
        }

        let rows = '';
        claims.forEach(function(claim) {
            const revComment = claim.reviewerComment
                ? String(claim.reviewerComment) : '-';
            rows += '<tr>'
                + '<td>' + claim.id + '</td>'
                + '<td>&#x20B9;' + claim.amount + '</td>'
                + '<td>' + claim.date + '</td>'
                + '<td>' + claim.description + '</td>'
                + '<td>' + getStatusBadge(claim.status) + '</td>'
                + '<td>' + revComment + '</td>'
                + '</tr>';
        });

        document.getElementById('ownClaimsBody').innerHTML = rows;
        document.getElementById('ownClaimsTable')
            .style.display = 'table';
        document.getElementById('ownClaimsEmpty')
            .style.display = 'none';
    } else {
        showMessage('ownClaimsMsg',
            result.message || 'Failed to load claims', true);
    }
}

async function handleManagerSubmitClaim() {
    const amountEl = document.getElementById('ownAmount');
    const amount = parseFloat(amountEl.value);
    const date = document.getElementById('ownDate').value;
    const description = document
        .getElementById('ownDescription').value.trim();

    if (!amount || amount <= 0) {
        showMessage('ownSubmitMsg',
            'Please enter a valid amount', true);
        return;
    }
    if (amount > 100000) {
        showMessage('ownSubmitMsg',
            'Amount cannot exceed 100000', true);
        return;
    }
    if (!date) {
        showMessage('ownSubmitMsg', 'Please select a date', true);
        return;
    }
    if (!description) {
        showMessage('ownSubmitMsg',
            'Please enter a description', true);
        return;
    }

    const data = {
        employeeId: CURRENT_REVIEWER_ID,
        amount: amount,
        date: date,
        description: description
    };

    try {
        const result = await submitClaim(data);
        if (result.status === 'success') {
            showMessage('ownSubmitMsg',
                'Claim submitted successfully');
            document.getElementById('ownAmount').value = '';
            document.getElementById('ownDate').value = '';
            document.getElementById('ownDescription').value = '';
            await loadManagerOwnClaims();
        } else {
            showMessage('ownSubmitMsg',
                result.message || 'Something went wrong', true);
        }
    } catch (err) {
        showMessage('ownSubmitMsg',
            'Could not connect to server', true);
    }
}
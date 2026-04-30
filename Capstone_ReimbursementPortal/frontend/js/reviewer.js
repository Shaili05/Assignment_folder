async function loadReviewerClaims() {
    const reviewerId = parseInt(
        document.getElementById('reviewerId').value
    );

    if (!reviewerId || reviewerId <= 0) {
        showMessage('reviewerMsg',
            'Please enter a valid Reviewer ID', true);
        return;
    }

    const result = await getReviewerClaims(reviewerId);

    if (result.status === 'success') {
        const claims = result.data.content;

        if (claims.length === 0) {
            showMessage('reviewerMsg',
                'No claims assigned to you', true);
            return;
        }

        let rows = '';
        claims.forEach(claim => {
            rows += `
                <tr>
                    <td>${claim.id}</td>
                    <td>${claim.employeeName}</td>
                    <td>₹${claim.amount}</td>
                    <td>${claim.date}</td>
                    <td>${claim.description}</td>
                    <td class="${getStatusClass(claim.status)}">
                        ${claim.status}
                    </td>
                    <td>
                        ${claim.status === 'SUBMITTED' ? 'Pending' : 'Done'}
                    </td>
                </tr>
            `;
        });

        document.getElementById('reviewerBody').innerHTML = rows;
        document.getElementById('reviewerTable').style.display = 'table';
    } else {
        showMessage('reviewerMsg',
            result.message || 'Something went wrong', true);
    }
}

async function handleApprove() {
    const claimId = parseInt(
        document.getElementById('claimId').value
    );
    const reviewerId = parseInt(
        document.getElementById('actionReviewerId').value
    );
    const comment = document.getElementById('comment').value;

    if (!claimId || !reviewerId) {
        showMessage('actionMsg',
            'Please enter Claim ID and Reviewer ID', true);
        return;
    }

    const result = await approveClaim(claimId, reviewerId, comment);

    if (result.status === 'success') {
        showMessage('actionMsg', 'Claim approved successfully!');
        loadReviewerClaims();
    } else {
        showMessage('actionMsg',
            result.message || 'Something went wrong', true);
    }
}

async function handleReject() {
    const claimId = parseInt(
        document.getElementById('claimId').value
    );
    const reviewerId = parseInt(
        document.getElementById('actionReviewerId').value
    );
    const comment = document.getElementById('comment').value;

    if (!claimId || !reviewerId || !comment) {
        showMessage('actionMsg',
            'Please enter Claim ID, Reviewer ID and a comment', true);
        return;
    }

    const result = await rejectClaim(claimId, reviewerId, comment);

    if (result.status === 'success') {
        showMessage('actionMsg', 'Claim rejected successfully!');
        loadReviewerClaims();
    } else {
        showMessage('actionMsg',
            result.message || 'Something went wrong', true);
    }
}
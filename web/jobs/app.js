// Global variables
let allJobs = [];
let currentSort = 'date';

// Set job role from quick filters
function setRole(role) {
    document.getElementById('job-role').value = role;
}

// Search jobs
async function searchJobs() {
    // Get form values
    const role = document.getElementById('job-role').value.trim();
    const location = document.getElementById('location').value;
    const jobType = document.getElementById('job-type').value;
    
    // Get selected sources
    const sources = [];
    document.querySelectorAll('.source-chip input:checked').forEach(input => {
        sources.push(input.dataset.source);
    });

    if (!role) {
        alert('Please enter a job role or keyword');
        return;
    }

    if (sources.length === 0) {
        alert('Please select at least one job source');
        return;
    }

    // Show loading, hide results
    document.getElementById('loading-section').classList.remove('hidden');
    document.getElementById('results-section').classList.add('hidden');

    try {
        // Call Python backend to search jobs
        const response = await fetch('http://localhost:8000/search-jobs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                keywords: [role],
                location: location,
                job_type: jobType === 'all' ? ['internship', 'full-time'] : [jobType],
                sources: sources,
                max_per_source: 25
            })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch jobs');
        }

        const data = await response.json();
        allJobs = data.jobs || [];

        // Hide loading, show results
        document.getElementById('loading-section').classList.add('hidden');
        displayResults(allJobs);

    } catch (error) {
        console.error('Error searching jobs:', error);
        document.getElementById('loading-section').classList.add('hidden');
        alert('Error searching jobs. Please make sure the backend server is running.');
    }
}

// Display search results
function displayResults(jobs) {
    const resultsSection = document.getElementById('results-section');
    const jobsContainer = document.getElementById('jobs-container');
    const noResults = document.getElementById('no-results');

    resultsSection.classList.remove('hidden');

    if (jobs.length === 0) {
        jobsContainer.innerHTML = '';
        noResults.classList.remove('hidden');
        updateStats(jobs);
        return;
    }

    noResults.classList.add('hidden');

    // Update stats
    updateStats(jobs);

    // Display jobs
    jobsContainer.innerHTML = jobs.map((job, index) => `
        <div class="job-card" onclick="showJobDetails(${index})">
            <div class="job-header">
                <div class="job-title-section">
                    <div class="job-title">
                        <i class="fas fa-briefcase"></i>
                        ${escapeHtml(job.title)}
                    </div>
                    <div class="company-name">
                        <i class="fas fa-building"></i>
                        ${escapeHtml(job.company)}
                    </div>
                </div>
                <div class="job-badges">
                    <span class="badge badge-internship">
                        ${job.job_type === 'internship' ? 'Stage' : 'Full-time'}
                    </span>
                    ${job.remote ? '<span class="badge badge-remote">Remote</span>' : ''}
                    <span class="badge badge-source">${escapeHtml(job.source)}</span>
                </div>
            </div>

            <div class="job-details">
                <div class="job-detail-item">
                    <i class="fas fa-map-marker-alt"></i>
                    ${escapeHtml(job.location)}
                </div>
                <div class="job-detail-item">
                    <i class="fas fa-calendar-alt"></i>
                    ${formatDate(job.posted_date)}
                </div>
                ${job.salary ? `
                <div class="job-detail-item">
                    <i class="fas fa-euro-sign"></i>
                    ${escapeHtml(job.salary)}
                </div>
                ` : ''}
            </div>

            ${job.description ? `
            <div class="job-description">
                ${escapeHtml(job.description.substring(0, 200))}...
            </div>
            ` : ''}

            <div class="job-actions">
                <button class="btn-primary" onclick="event.stopPropagation(); openJobUrl('${escapeHtml(job.url)}')">
                    <i class="fas fa-external-link-alt"></i>
                    View Job Posting
                </button>
                <button class="btn-secondary" onclick="event.stopPropagation(); showJobDetails(${index})">
                    <i class="fas fa-info-circle"></i>
                    Details
                </button>
            </div>
        </div>
    `).join('');

    // Update total jobs in header
    document.getElementById('total-jobs').textContent = jobs.length;
}

// Update statistics
function updateStats(jobs) {
    document.getElementById('internship-count').textContent = jobs.length;
    
    const uniqueCompanies = new Set(jobs.map(j => j.company)).size;
    document.getElementById('company-count').textContent = uniqueCompanies;
    
    const uniqueLocations = new Set(jobs.map(j => j.location)).size;
    document.getElementById('location-count').textContent = uniqueLocations;
    
    const uniqueSources = new Set(jobs.map(j => j.source)).size;
    document.getElementById('source-count').textContent = uniqueSources;
}

// Sort results
function sortResults() {
    const sortBy = document.getElementById('sort-by').value;
    currentSort = sortBy;

    const sorted = [...allJobs].sort((a, b) => {
        switch (sortBy) {
            case 'date':
                return new Date(b.posted_date) - new Date(a.posted_date);
            case 'company':
                return a.company.localeCompare(b.company);
            case 'location':
                return a.location.localeCompare(b.location);
            case 'source':
                return a.source.localeCompare(b.source);
            default:
                return 0;
        }
    });

    displayResults(sorted);
}

// Show job details in modal
function showJobDetails(index) {
    const job = allJobs[index];
    const modal = document.getElementById('job-modal');
    const modalBody = document.getElementById('modal-body');

    modalBody.innerHTML = `
        <div style="padding: 32px;">
            <div style="margin-bottom: 24px;">
                <h2 style="font-size: 28px; margin-bottom: 12px; display: flex; align-items: center; gap: 12px;">
                    <i class="fas fa-briefcase" style="color: var(--primary-color);"></i>
                    ${escapeHtml(job.title)}
                </h2>
                <div style="display: flex; align-items: center; gap: 12px; font-size: 18px; color: var(--text-secondary);">
                    <i class="fas fa-building" style="color: var(--warning-color);"></i>
                    ${escapeHtml(job.company)}
                </div>
            </div>

            <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 24px;">
                <span class="badge badge-internship" style="padding: 8px 16px; font-size: 14px;">
                    ${job.job_type === 'internship' ? 'Stage / Internship' : 'Full-time'}
                </span>
                ${job.remote ? '<span class="badge badge-remote" style="padding: 8px 16px; font-size: 14px;">Remote</span>' : ''}
                <span class="badge badge-source" style="padding: 8px 16px; font-size: 14px;">
                    ${escapeHtml(job.source)}
                </span>
            </div>

            <div style="background: var(--dark-bg); padding: 20px; border-radius: 12px; margin-bottom: 24px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <div style="color: var(--text-secondary); font-size: 12px; text-transform: uppercase; margin-bottom: 4px;">
                            <i class="fas fa-map-marker-alt"></i> Location
                        </div>
                        <div style="font-size: 16px; font-weight: 500;">${escapeHtml(job.location)}</div>
                    </div>
                    <div>
                        <div style="color: var(--text-secondary); font-size: 12px; text-transform: uppercase; margin-bottom: 4px;">
                            <i class="fas fa-calendar-alt"></i> Posted Date
                        </div>
                        <div style="font-size: 16px; font-weight: 500;">${formatDate(job.posted_date)}</div>
                    </div>
                    ${job.salary ? `
                    <div>
                        <div style="color: var(--text-secondary); font-size: 12px; text-transform: uppercase; margin-bottom: 4px;">
                            <i class="fas fa-euro-sign"></i> Salary
                        </div>
                        <div style="font-size: 16px; font-weight: 500;">${escapeHtml(job.salary)}</div>
                    </div>
                    ` : ''}
                    ${job.remote ? `
                    <div>
                        <div style="color: var(--text-secondary); font-size: 12px; text-transform: uppercase; margin-bottom: 4px;">
                            <i class="fas fa-laptop-house"></i> Work Type
                        </div>
                        <div style="font-size: 16px; font-weight: 500;">Remote</div>
                    </div>
                    ` : ''}
                </div>
            </div>

            ${job.description ? `
            <div style="margin-bottom: 24px;">
                <h3 style="font-size: 20px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-file-alt" style="color: var(--primary-color);"></i>
                    Description
                </h3>
                <div style="line-height: 1.8; color: var(--text-secondary);">
                    ${escapeHtml(job.description)}
                </div>
            </div>
            ` : ''}

            ${job.requirements ? `
            <div style="margin-bottom: 24px;">
                <h3 style="font-size: 20px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-list-check" style="color: var(--primary-color);"></i>
                    Requirements
                </h3>
                <div style="line-height: 1.8; color: var(--text-secondary);">
                    ${escapeHtml(job.requirements)}
                </div>
            </div>
            ` : ''}

            <div style="display: flex; gap: 12px; margin-top: 32px;">
                <button class="btn-primary" onclick="openJobUrl(${index})" style="padding: 14px 28px; font-size: 16px;">
                    <i class="fas fa-external-link-alt"></i>
                    Apply on ${escapeHtml(job.source)}
                </button>
                <button class="btn-secondary" onclick="closeModal()" style="padding: 14px 28px; font-size: 16px;">
                    <i class="fas fa-times"></i>
                    Close
                </button>
            </div>
        </div>
    `;

    modal.classList.remove('hidden');
}

// Close modal
function closeModal() {
    document.getElementById('job-modal').classList.add('hidden');
}

// Open job URL in new tab
function openJobUrl(jobIndex) {
    // If jobIndex is a number, get the URL from allJobs array
    if (typeof jobIndex === 'number') {
        const job = allJobs[jobIndex];
        if (job && job.url && job.url !== 'N/A' && job.url !== '') {
            window.open(job.url, '_blank');
        } else {
            alert('Job URL not available');
        }
    } 
    // If it's a string (legacy), use it directly
    else if (jobIndex && jobIndex !== 'N/A' && jobIndex !== '') {
        window.open(jobIndex, '_blank');
    } else {
        alert('Job URL not available');
    }
}

// Export results
function exportResults() {
    if (allJobs.length === 0) {
        alert('No jobs to export');
        return;
    }

    // Create CSV content
    const headers = ['Title', 'Company', 'Location', 'Type', 'Posted Date', 'Source', 'URL'];
    const csvContent = [
        headers.join(','),
        ...allJobs.map(job => [
            `"${job.title}"`,
            `"${job.company}"`,
            `"${job.location}"`,
            job.job_type,
            job.posted_date,
            `"${job.source}"`,
            `"${job.url}"`
        ].join(','))
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `xeno_jobs_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Utility functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    } catch (error) {
        return dateString;
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('job-modal');
    if (event.target === modal) {
        closeModal();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('XENO Job Hunter initialized');
});

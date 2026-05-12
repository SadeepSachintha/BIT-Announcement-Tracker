document.addEventListener('DOMContentLoaded', () => {
    const refreshBtn = document.getElementById('refresh-btn');
    const container = document.getElementById('announcements-container');
    const template = document.getElementById('announcement-template');
    const scraperStatus = document.getElementById('scraper-status');
    const subCount = document.getElementById('sub-count');

    async function fetchStatus() {
        try {
            const response = await fetch('/api/status');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            console.log('Status data received:', data);
            
            if (data.scraper_running) {
                scraperStatus.textContent = 'Online';
                scraperStatus.className = 'value status-online';
            } else {
                scraperStatus.textContent = 'Offline';
                scraperStatus.className = 'value status-offline';
            }
            
            // Ensure we handle cases where data might be missing
            const count = data.total_subscribers !== undefined ? data.total_subscribers : 0;
            subCount.textContent = count;
            
        } catch (error) {
            console.error('Failed to fetch status:', error);
            scraperStatus.textContent = 'Error';
            scraperStatus.className = 'value status-offline';
            subCount.textContent = 'Error';
        }
    }

    async function fetchAnnouncements() {
        try {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = 'Refreshing...';
            
            const response = await fetch('/api/announcements');
            const data = await response.json();
            
            container.innerHTML = '';
            
            if (data.length === 0) {
                container.innerHTML = '<div class="loading">No announcements found yet.</div>';
            } else {
                data.forEach(item => {
                    const clone = template.content.cloneNode(true);
                    
                    clone.querySelector('.title').textContent = item.title;
                    
                    const sourceBadge = clone.querySelector('.source-badge');
                    const source = item.source || 'Main Site';
                    sourceBadge.textContent = source;
                    
                    if (source === 'VLE') {
                        sourceBadge.classList.add('source-vle');
                    } else if (source === 'Project VLE') {
                        sourceBadge.classList.add('source-project');
                    } else {
                        sourceBadge.classList.add('source-main');
                    }
                    
                    // Format date nicely
                    try {
                        const dateObj = new Date(item.pub_date);
                        if (!isNaN(dateObj)) {
                            clone.querySelector('.date').textContent = dateObj.toLocaleDateString(undefined, { 
                                year: 'numeric', month: 'short', day: 'numeric' 
                            });
                        } else {
                            clone.querySelector('.date').textContent = item.pub_date;
                        }
                    } catch (e) {
                        clone.querySelector('.date').textContent = item.pub_date;
                    }
                    
                    clone.querySelector('.link-btn').href = item.link;
                    
                    container.appendChild(clone);
                });
            }
        } catch (error) {
            console.error('Failed to fetch announcements', error);
            container.innerHTML = '<div class="loading" style="color: #ef4444">Failed to load announcements. Please try again.</div>';
        } finally {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg> Refresh';
        }
    }

    // Initial fetch
    fetchStatus();
    fetchAnnouncements();

    // Event listeners
    refreshBtn.addEventListener('click', () => {
        fetchStatus();
        fetchAnnouncements();
    });

    // Auto-refresh every 30 seconds
    setInterval(() => {
        fetchStatus();
        fetchAnnouncements();
    }, 30000);
});

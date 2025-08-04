// Promptitron Web UI JavaScript

class PrompitronApp {
    constructor() {
        this.currentOperation = null;
        this.studentProfile = {
            student_id: null,
            target_exam: 'TYT',
            daily_hours: 6,
            weak_subjects: [],
            strong_subjects: []
        };
        this.conversationHistory = [];
        this.curriculumData = {};
        
        this.init();
    }
    
    init() {
        // Check API health
        this.checkHealth();
        
        // Load curriculum data
        this.loadCurriculum();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initialize student profile
        this.loadStudentProfile();
        
        // Start health check interval
        setInterval(() => this.checkHealth(), 30000); // Check every 30 seconds
    }
    
    setupEventListeners() {
        // AI Assistant input
        const aiInput = document.getElementById('ai-user-input');
        if (aiInput) {
            aiInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendAIMessage();
                }
            });
        }
        
        // Tab switching
        const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
        tabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                if (e.target.id === 'manual-control-tab') {
                    this.resetManualOperations();
                }
            });
        });
        
        // Form inputs change detection
        this.setupFormChangeListeners();
    }
    
    setupFormChangeListeners() {
        const profileInputs = ['target-exam', 'daily-hours', 'weak-subjects'];
        profileInputs.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', () => this.updateStudentProfile());
            }
        });
    }
    
    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            const indicator = document.getElementById('status-indicator');
            const text = document.getElementById('status-text');
            
            if (data.status === 'healthy') {
                indicator.className = 'status-indicator status-healthy';
                text.textContent = 'Sistem Çalışıyor';
            } else {
                indicator.className = 'status-indicator status-unhealthy';
                text.textContent = 'Sistem Hatası';
            }
        } catch (error) {
            console.error('Health check failed:', error);
            const indicator = document.getElementById('status-indicator');
            const text = document.getElementById('status-text');
            indicator.className = 'status-indicator status-unhealthy';
            text.textContent = 'Bağlantı Hatası';
        }
    }
    
    async loadCurriculum() {
        try {
            const response = await fetch('/curriculum');
            if (response.ok) {
                this.curriculumData = await response.json();
                this.renderCurriculumTree();
            }
        } catch (error) {
            console.error('Failed to load curriculum:', error);
            this.showCurriculumError();
        }
    }
    
    renderCurriculumTree() {
        const container = document.getElementById('curriculum-tree');
        if (!container) return;
        
        let html = '';
        
        Object.entries(this.curriculumData).forEach(([subject, data]) => {
            html += `
                <div class="curriculum-subject mb-2">
                    <div class="curriculum-item fw-bold" onclick="app.toggleSubject('${subject}')">
                        <i class="fas fa-book me-2"></i>${subject}
                        <i class="fas fa-chevron-down float-end"></i>
                    </div>
                    <div id="subject-${subject}" class="curriculum-topics ms-3" style="display: none;">
            `;
            
            if (data.topics && Array.isArray(data.topics)) {
                data.topics.forEach((topic, index) => {
                    html += `
                        <div class="curriculum-item small" onclick="app.selectTopic('${subject}', '${topic.name || topic}')">
                            <i class="fas fa-bookmark me-2"></i>${topic.name || topic}
                        </div>
                    `;
                });
            }
            
            html += `
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    showCurriculumError() {
        const container = document.getElementById('curriculum-tree');
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p>Müfredat verileri yüklenemedi</p>
                </div>
            `;
        }
    }
    
    toggleSubject(subject) {
        const element = document.getElementById(`subject-${subject}`);
        if (element) {
            const isVisible = element.style.display !== 'none';
            element.style.display = isVisible ? 'none' : 'block';
            
            // Update chevron icon
            const chevron = element.previousElementSibling.querySelector('.fa-chevron-down, .fa-chevron-up');
            if (chevron) {
                chevron.className = isVisible ? 'fas fa-chevron-down float-end' : 'fas fa-chevron-up float-end';
            }
        }
    }
    
    selectTopic(subject, topic) {
        // Update topic in relevant forms
        const topicInputs = document.querySelectorAll('input[id*="topic"]');
        topicInputs.forEach(input => {
            input.value = topic;
        });
        
        // Update subject in relevant selects
        const subjectSelects = document.querySelectorAll('select[id*="subject"]');
        subjectSelects.forEach(select => {
            const normalizedSubject = subject.toUpperCase().replace(/\s+/g, '_');
            const option = Array.from(select.options).find(opt => 
                opt.value.includes(normalizedSubject) || 
                opt.text.toLowerCase().includes(subject.toLowerCase())
            );
            if (option) {
                select.value = option.value;
            }
        });
        
        // Highlight selected topic
        document.querySelectorAll('.curriculum-item').forEach(item => {
            item.classList.remove('selected');
        });
        event.target.classList.add('selected');
        
        this.showNotification(`Seçildi: ${subject} - ${topic}`, 'info');
    }
    
    loadStudentProfile() {
        const saved = localStorage.getItem('promptitron_student_profile');
        if (saved) {
            this.studentProfile = JSON.parse(saved);
            this.updateProfileForm();
        }
    }
    
    updateStudentProfile() {
        // Get values from form
        const targetExam = document.getElementById('target-exam')?.value;
        const dailyHours = document.getElementById('daily-hours')?.value;
        const weakSubjects = Array.from(document.getElementById('weak-subjects')?.selectedOptions || [])
            .map(option => option.value);
        
        // Update profile
        if (targetExam) this.studentProfile.target_exam = targetExam;
        if (dailyHours) this.studentProfile.daily_hours = parseInt(dailyHours);
        this.studentProfile.weak_subjects = weakSubjects;
        
        // Save to localStorage
        localStorage.setItem('promptitron_student_profile', JSON.stringify(this.studentProfile));
        
        this.showNotification('Profil güncellendi', 'success');
    }
    
    updateProfileForm() {
        const targetExam = document.getElementById('target-exam');
        const dailyHours = document.getElementById('daily-hours');
        const weakSubjects = document.getElementById('weak-subjects');
        
        if (targetExam) targetExam.value = this.studentProfile.target_exam;
        if (dailyHours) dailyHours.value = this.studentProfile.daily_hours;
        if (weakSubjects) {
            Array.from(weakSubjects.options).forEach(option => {
                option.selected = this.studentProfile.weak_subjects.includes(option.value);
            });
        }
    }
    
    async sendAIMessage() {
        const input = document.getElementById('ai-user-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Clear input
        input.value = '';
        
        // Add user message to chat
        this.addMessageToChat(message, 'user');
        
        // Show loading
        this.addLoadingToChat();
        
        try {
            const response = await fetch('/ai-assistant', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    context: {
                        student_profile: this.studentProfile
                    }
                })
            });
            
            const data = await response.json();
            
            // Remove loading
            this.removeLoadingFromChat();
            
            if (data.error) {
                this.addMessageToChat(`Hata: ${data.error}`, 'assistant');
            } else {
                const assistantMessage = data.response || data.text || 'Yanıt alınamadı';
                this.addMessageToChat(assistantMessage, 'assistant');
                
                // Handle special response types
                if (data.questions) {
                    this.displayQuestions(data.questions);
                } else if (data.study_plan) {
                    this.displayStudyPlan(data.study_plan);
                }
            }
            
        } catch (error) {
            this.removeLoadingFromChat();
            this.addMessageToChat(`Bağlantı hatası: ${error.message}`, 'assistant');
        }
    }
    
    addMessageToChat(message, type) {
        const container = document.getElementById('ai-chat-container');
        if (!container) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        if (type === 'user') {
            messageDiv.innerHTML = `<strong>Siz:</strong> ${this.escapeHtml(message)}`;
        } else {
            messageDiv.innerHTML = `<strong>AI Asistan:</strong> ${this.formatMessage(message)}`;
        }
        
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
    }
    
    addLoadingToChat() {
        const container = document.getElementById('ai-chat-container');
        if (!container) return;
        
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant loading-message';
        loadingDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <span>AI düşünüyor...</span>
            </div>
        `;
        
        container.appendChild(loadingDiv);
        container.scrollTop = container.scrollHeight;
    }
    
    removeLoadingFromChat() {
        const loading = document.querySelector('.loading-message');
        if (loading) {
            loading.remove();
        }
    }
    
    formatMessage(message) {
        // Convert markdown-like formatting to HTML
        let formatted = this.escapeHtml(message);
        
        // Bold text
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic text
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Lists
        formatted = formatted.replace(/^\- (.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        return formatted;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    selectOperation(operation) {
        this.currentOperation = operation;
        
        // Hide all forms
        document.querySelectorAll('[id$="-form"]').forEach(form => {
            form.style.display = 'none';
        });
        document.getElementById('no-operation').style.display = 'none';
        
        // Show selected form
        const formId = `${operation}-form`;
        const form = document.getElementById(formId);
        if (form) {
            form.style.display = 'block';
        }
        
        // Update button states
        document.querySelectorAll('.btn-group-custom .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
    }
    
    resetManualOperations() {
        this.currentOperation = null;
        
        // Hide all forms
        document.querySelectorAll('[id$="-form"]').forEach(form => {
            form.style.display = 'none';
        });
        document.getElementById('no-operation').style.display = 'block';
        
        // Reset button states
        document.querySelectorAll('.btn-group-custom .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Clear output
        document.getElementById('manual-output').innerHTML = 
            '<p class="text-muted">İşlem sonuçları burada görüntülenecek.</p>';
    }
    
    async executeOperation(operation) {
        if (!operation) return;
        
        this.showManualLoading(true);
        
        try {
            let requestData = {};
            
            // Prepare request data based on operation
            switch (operation) {
                case 'chat':
                    requestData = {
                        message: document.getElementById('chat-message').value,
                        use_memory: document.getElementById('chat-use-memory').checked,
                        student_id: this.studentProfile.student_id
                    };
                    break;
                    
                case 'generate-questions':
                    requestData = {
                        subject: document.getElementById('question-subject').value,
                        topic: document.getElementById('question-topic').value,
                        difficulty: document.getElementById('question-difficulty').value,
                        count: parseInt(document.getElementById('question-count').value),
                        exam_type: document.getElementById('question-exam-type').value,
                        question_type: 'MULTIPLE_CHOICE'
                    };
                    break;
                    
                case 'generate-study-plan':
                    requestData = {
                        student_profile: {
                            ...this.studentProfile,
                            target_exam: document.getElementById('plan-target-exam').value,
                            daily_hours: parseInt(document.getElementById('plan-daily-hours').value)
                        },
                        target_exam: document.getElementById('plan-target-exam').value,
                        duration_weeks: parseInt(document.getElementById('plan-duration').value),
                        daily_hours: parseInt(document.getElementById('plan-daily-hours').value)
                    };
                    break;
                    
                case 'search':
                    requestData = {
                        query: document.getElementById('search-query').value,
                        n_results: parseInt(document.getElementById('search-results').value),
                        include_personalization: document.getElementById('search-personalization').checked
                    };
                    break;
                    
                case 'analyze-content':
                    requestData = {
                        content: document.getElementById('analysis-content').value,
                        analysis_type: document.getElementById('analysis-type').value,
                        include_suggestions: document.getElementById('analysis-suggestions').checked
                    };
                    break;
            }
            
            const response = await fetch(`/manual/${operation}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            this.showManualLoading(false);
            this.displayManualResult(data, operation);
            
        } catch (error) {
            this.showManualLoading(false);
            this.displayManualError(error.message);
        }
    }
    
    showManualLoading(show) {
        const loading = document.getElementById('manual-loading');
        const output = document.getElementById('manual-output');
        
        if (show) {
            loading.style.display = 'block';
            output.style.display = 'none';
        } else {
            loading.style.display = 'none';
            output.style.display = 'block';
        }
    }
    
    displayManualResult(data, operation) {
        const output = document.getElementById('manual-output');
        if (!output) return;
        
        let html = '';
        
        if (data.error) {
            html = `<div class="alert alert-danger">Hata: ${data.error}</div>`;
        } else {
            switch (operation) {
                case 'chat':
                    html = `
                        <div class="card">
                            <div class="card-body">
                                <h6>Sohbet Yanıtı</h6>
                                <p>${this.formatMessage(data.response || data.text)}</p>
                            </div>
                        </div>
                    `;
                    break;
                    
                case 'generate-questions':
                    html = this.formatQuestions(data);
                    break;
                    
                case 'generate-study-plan':
                    html = this.formatStudyPlan(data);
                    break;
                    
                case 'search':
                    html = this.formatSearchResults(data);
                    break;
                    
                case 'analyze-content':
                    html = this.formatAnalysis(data);
                    break;
                    
                default:
                    html = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            }
        }
        
        output.innerHTML = html;
    }
    
    formatQuestions(data) {
        if (!data || !Array.isArray(data)) {
            return '<p class="text-muted">Soru bulunamadı.</p>';
        }
        
        let html = '<h6>Üretilen Sorular</h6>';
        
        data.forEach((question, index) => {
            html += `
                <div class="question-item">
                    <div class="question-text">
                        <strong>Soru ${index + 1}:</strong> ${question.question_text}
                    </div>
            `;
            
            if (question.options && Array.isArray(question.options)) {
                question.options.forEach(option => {
                    const isCorrect = option.option_letter === question.correct_answer;
                    html += `
                        <div class="option ${isCorrect ? 'correct' : ''}">
                            <strong>${option.option_letter})</strong> ${option.option_text}
                        </div>
                    `;
                });
            }
            
            if (question.explanation) {
                html += `
                    <div class="explanation">
                        <strong>Açıklama:</strong> ${question.explanation}
                    </div>
                `;
            }
            
            html += '</div>';
        });
        
        return html;
    }
    
    formatStudyPlan(data) {
        let html = '<h6>Çalışma Planı</h6>';
        
        if (data.overall_strategy) {
            html += `
                <div class="card mb-3">
                    <div class="card-body">
                        <h6>Genel Strateji</h6>
                        <p>${data.overall_strategy}</p>
                    </div>
                </div>
            `;
        }
        
        if (data.weekly_plans && Array.isArray(data.weekly_plans)) {
            html += '<h6>Haftalık Plan</h6>';
            data.weekly_plans.forEach((week, index) => {
                html += `
                    <div class="card mb-2">
                        <div class="card-body">
                            <h6>Hafta ${index + 1}</h6>
                            <p>${week}</p>
                        </div>
                    </div>
                `;
            });
        }
        
        return html;
    }
    
    formatSearchResults(data) {
        let html = '<h6>Arama Sonuçları</h6>';
        
        if (data.results && Array.isArray(data.results)) {
            data.results.forEach(result => {
                html += `
                    <div class="card mb-2">
                        <div class="card-body">
                            <h6>${result.title || 'Başlıksız'}</h6>
                            <p>${result.content}</p>
                            <small class="text-muted">
                                Skor: ${result.relevance_score?.toFixed(2) || 'N/A'}
                            </small>
                        </div>
                    </div>
                `;
            });
        } else {
            html += '<p class="text-muted">Sonuç bulunamadı.</p>';
        }
        
        return html;
    }
    
    formatAnalysis(data) {
        let html = '<h6>İçerik Analizi</h6>';
        
        if (data.analysis) {
            html += `
                <div class="card">
                    <div class="card-body">
                        <p>${this.formatMessage(data.analysis)}</p>
                    </div>
                </div>
            `;
        }
        
        return html;
    }
    
    displayManualError(error) {
        const output = document.getElementById('manual-output');
        if (output) {
            output.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Hata:</strong> ${error}
                </div>
            `;
        }
    }
    
    async uploadFile() {
        const fileInput = document.getElementById('file-input');
        const description = document.getElementById('file-description').value;
        
        if (!fileInput.files[0]) {
            this.showNotification('Lütfen bir dosya seçin', 'warning');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('description', description);
        
        try {
            this.showNotification('Dosya yükleniyor...', 'info');
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                this.showNotification(`Hata: ${data.error}`, 'danger');
            } else {
                this.showNotification('Dosya başarıyla yüklendi', 'success');
                
                // Clear form
                fileInput.value = '';
                document.getElementById('file-description').value = '';
            }
            
        } catch (error) {
            this.showNotification(`Yükleme hatası: ${error.message}`, 'danger');
        }
    }
    
    async exportData(format) {
        try {
            this.showNotification(`${format.toUpperCase()} formatında dışa aktarılıyor...`, 'info');
            
            const response = await fetch(`/export/${format}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `promptitron_export.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showNotification('Dosya başarıyla indirildi', 'success');
            } else {
                this.showNotification('Dışa aktarma başarısız', 'danger');
            }
            
        } catch (error) {
            this.showNotification(`Dışa aktarma hatası: ${error.message}`, 'danger');
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
}

// Global functions for HTML onclick events
function handleAIEnter(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        app.sendAIMessage();
    }
}

function sendAIMessage() {
    app.sendAIMessage();
}

function updateProfile() {
    app.updateStudentProfile();
}

function selectOperation(operation) {
    app.selectOperation(operation);
}

function executeOperation(operation) {
    app.executeOperation(operation);
}

function uploadFile() {
    app.uploadFile();
}

function exportData(format) {
    app.exportData(format);
}

// Initialize app when page loads
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new PrompitronApp();
});
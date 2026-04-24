function handleSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('githubUrl');
    const url = input.value.trim();
    
    if (!isValidGitHubUrl(url)) {
        showError('请输入有效的GitHub URL');
        return;
    }
    
    // 生成加速链接
    const acceleratedUrl = generateAcceleratedUrl(url);
    
    // 显示结果
    showResult(acceleratedUrl);
}

function generateAcceleratedUrl(url) {
    const baseUrl = window.appConfig.baseUrl;
    const cleanUrl = url.replace(/^https?:\\/\\//, '');
    return `${baseUrl}/https://${cleanUrl}`;
}

function showResult(acceleratedUrl) {
    const resultBox = document.getElementById('resultBox');
    const resultUrl = document.getElementById('resultUrl');
    
    resultUrl.value = acceleratedUrl;
    resultBox.style.display = 'block';
    
    // 添加动画效果
    resultBox.classList.add('fade-in');
    
    // 自动滚动到结果
    resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function copyToClipboard() {
    const resultUrl = document.getElementById('resultUrl');
    const copyBtn = document.querySelector('.copy-btn');
    
    resultUrl.select();
    resultUrl.setSelectionRange(0, 99999);
    
    navigator.clipboard.writeText(resultUrl.value).then(() => {
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fas fa-check"></i> 已复制';
        copyBtn.classList.add('success');
        
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.classList.remove('success');
        }, 2000);
    }).catch(() => {
        // 降级方案
        document.execCommand('copy');
        showSuccess('链接已复制到剪贴板');
    });
}

function isValidGitHubUrl(url) {
    const patterns = [
        /^(?:https?:\\/\\/)?github\\.com\\/.+\\/(?:releases|archive)\\//,
        /^(?:https?:\\/\\/)?github\\.com\\/.+\\/(?:blob|raw)\\//,
        /^(?:https?:\\/\\/)?github\\.com\\/.+\\/(?:info|git-).+/,
        /^(?:https?:\\/\\/)?raw\\.(?:githubusercontent|github)\\.com\\/.+\\/.+\\/.+\\//,
        /^(?:https?:\\/\\/)?gist\\.(?:githubusercontent|github)\\.com\\/.+\\/.+\\//
    ];
    
    return patterns.some(pattern => pattern.test(url));
}

function showError(message) {
    const input = document.getElementById('githubUrl');
    const existingError = document.querySelector('.error-message');
    
    if (existingError) {
        existingError.remove();
    }
    
    input.style.borderColor = '#ef4444';
    input.insertAdjacentHTML('afterend', `<div class="error-message">${message}</div>`);
    
    setTimeout(() => {
        input.style.borderColor = '#e2e8f0';
        const error = document.querySelector('.error-message');
        if (error) error.remove();
    }, 3000);
}

function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'toast success';
    toast.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}

// 添加输入框动画
document.getElementById('githubUrl').addEventListener('focus', function() {
    this.parentElement.style.transform = 'scale(1.02)';
});

document.getElementById('githubUrl').addEventListener('blur', function() {
    this.parentElement.style.transform = 'scale(1)';
});

// 粘贴事件增强
document.getElementById('githubUrl').addEventListener('paste', function(e) {
    setTimeout(() => {
        if (isValidGitHubUrl(this.value)) {
            this.style.borderColor = '#10b981';
            setTimeout(() => {
                this.style.borderColor = '#e2e8f0';
            }, 500);
        }
    }, 100);
});

// 快捷键支持
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K 聚焦输入框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('githubUrl').focus();
    }
});

// 添加输入提示
document.getElementById('githubUrl').addEventListener('input', function() {
    const url = this.value.trim();
    if (url && isValidGitHubUrl(url)) {
        this.style.borderColor = '#10b981';
    } else if (url) {
        this.style.borderColor = '#f59e0b';
    } else {
        this.style.borderColor = '#e2e8f0';
    }
});

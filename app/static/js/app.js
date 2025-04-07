function handleSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('githubUrl');
    const url = input.value.trim();
    
    if (!isValidGitHubUrl(url)) {
        showError('请输入有效的GitHub URL');
        return;
    }
    
    window.location.href = `/${url}`;
}

function isValidGitHubUrl(url) {
    return /^(?:https?:\/\/)?github\.com\/.+/.test(url);
}

function showError(message) {
    // 添加错误提示动画
    const input = document.getElementById('githubUrl');
    input.style.borderColor = '#ef4444';
    input.insertAdjacentHTML('afterend', `<div class="error-message">${message}</div>`);
    
    setTimeout(() => {
        input.style.borderColor = '#e2e8f0';
        document.querySelector('.error-message').remove();
    }, 3000);
}

// 添加输入框动画
document.getElementById('githubUrl').addEventListener('focus', function() {
    this.parentElement.style.transform = 'scale(1.02)';
});

document.getElementById('githubUrl').addEventListener('blur', function() {
    this.parentElement.style.transform = 'scale(1)';
});


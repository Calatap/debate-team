// ===== 辩论队管理系统 - 通用脚本 =====

// 自动关闭 Flash 消息
document.addEventListener('DOMContentLoaded', function() {
    const flashes = document.querySelectorAll('.flash-message');
    flashes.forEach(function(msg) {
        setTimeout(function() {
            if (msg.parentElement) msg.remove();
        }, 5000);
    });
});

// ===== 懒加载图片 =====
if ('IntersectionObserver' in window) {
    document.querySelectorAll('img[loading="lazy"]').forEach(function(img) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    img.src = img.dataset.src || img.src;
                    observer.unobserve(img);
                }
            });
        });
        observer.observe(img);
    });
}

const IMAGE_INDEX_VERSION = 1;
const IMAGE_RECORD_FIELDS = ['id', 'src', 'album', 'caption', 'alt'];
const PREVIEW_HIDE_DELAY_MS = 180;

const gallery = document.getElementById('link-gallery');
const galleryStatus = document.getElementById('gallery-status');
const preview = document.getElementById('preview');
const previewStatus = document.getElementById('preview-status');
const previewImage = document.getElementById('preview-image');

let hideTimer = null;
let previewRequestId = 0;

function validateImageIndex(data) {
    if (!data || data.version !== IMAGE_INDEX_VERSION || !Array.isArray(data.images)) {
        throw new Error('图片索引数据契约不匹配');
    }

    data.images.forEach((image, index) => {
        IMAGE_RECORD_FIELDS.forEach(field => {
            if (typeof image[field] !== 'string' || image[field].length === 0) {
                throw new Error(`第 ${index + 1} 条图片记录缺少有效字段: ${field}`);
            }
        });

        if (!image.src.startsWith('../image/') || image.src.includes('\\')) {
            throw new Error(`第 ${index + 1} 条图片记录包含无效 URL: ${image.src}`);
        }
    });

    return data.images;
}

function requirePageElements() {
    if (!gallery || !galleryStatus || !preview || !previewStatus || !previewImage) {
        throw new Error('图片索引页面缺少必要元素');
    }
}

function positionPreview(left, top) {
    const margin = 12;
    const maximumLeft = window.scrollX + window.innerWidth - preview.offsetWidth - margin;
    const maximumTop = window.scrollY + window.innerHeight - preview.offsetHeight - margin;

    preview.style.left = `${Math.max(window.scrollX + margin, Math.min(left, maximumLeft))}px`;
    preview.style.top = `${Math.max(window.scrollY + margin, Math.min(top, maximumTop))}px`;
}

function positionPreviewByPointer(event) {
    positionPreview(event.pageX + 12, event.pageY + 12);
}

function positionPreviewByLink(link) {
    const bounds = link.getBoundingClientRect();
    let left = window.scrollX + bounds.right + 12;

    if (left + preview.offsetWidth > window.scrollX + window.innerWidth - 12) {
        left = window.scrollX + bounds.left - preview.offsetWidth - 12;
    }

    positionPreview(left, window.scrollY + bounds.top);
}

function showPreview(image, positionCallback) {
    window.clearTimeout(hideTimer);
    previewRequestId += 1;
    const requestId = previewRequestId;

    preview.hidden = false;
    preview.classList.remove('show');
    previewStatus.hidden = false;
    previewStatus.classList.remove('is-error');
    previewStatus.textContent = '正在加载预览…';
    previewImage.hidden = true;
    previewImage.alt = image.alt;
    positionCallback();

    preview.getBoundingClientRect();
    preview.classList.add('show');

    previewImage.onload = function () {
        if (requestId !== previewRequestId) {
            return;
        }

        previewStatus.hidden = true;
        previewImage.hidden = false;
        positionCallback();
    };

    previewImage.onerror = function () {
        if (requestId !== previewRequestId) {
            return;
        }

        previewImage.hidden = true;
        previewStatus.hidden = false;
        previewStatus.classList.add('is-error');
        previewStatus.textContent = '预览加载失败，可点击链接打开原图。';
        positionCallback();
    };

    previewImage.src = image.src;
}

function hidePreview() {
    previewRequestId += 1;
    preview.classList.remove('show');
    window.clearTimeout(hideTimer);
    hideTimer = window.setTimeout(() => {
        preview.hidden = true;
    }, PREVIEW_HIDE_DELAY_MS);
}

function createImageLink(image) {
    const linkElement = document.createElement('li');
    const link = document.createElement('a');

    linkElement.className = 'link-item';
    link.href = image.src;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.className = 'link';
    link.textContent = image.caption;
    link.setAttribute('aria-controls', 'preview');
    linkElement.appendChild(link);

    let pointerPageX = 0;
    let pointerPageY = 0;
    const positionByLatestPointer = () => {
        positionPreview(pointerPageX + 12, pointerPageY + 12);
    };

    link.addEventListener('mouseenter', event => {
        pointerPageX = event.pageX;
        pointerPageY = event.pageY;
        showPreview(image, positionByLatestPointer);
    });
    link.addEventListener('mousemove', event => {
        pointerPageX = event.pageX;
        pointerPageY = event.pageY;
        if (!preview.hidden) {
            positionByLatestPointer();
        }
    });
    link.addEventListener('mouseleave', () => {
        if (document.activeElement !== link) {
            hidePreview();
        }
    });
    link.addEventListener('focus', () => {
        showPreview(image, () => positionPreviewByLink(link));
    });
    link.addEventListener('blur', hidePreview);
    link.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            hidePreview();
        }
    });

    return linkElement;
}

requirePageElements();
fetch('json/image_index.json')
    .then(response => {
        if (!response.ok) {
            throw new Error(`图片索引请求失败: HTTP ${response.status}`);
        }

        return response.json();
    })
    .then(data => {
        const images = validateImageIndex(data);

        images.forEach(image => gallery.appendChild(createImageLink(image)));
        galleryStatus.hidden = images.length > 0;
        galleryStatus.textContent = images.length > 0 ? '' : '暂无图片。';
    })
    .catch(error => {
        galleryStatus.hidden = false;
        galleryStatus.classList.add('is-error');
        galleryStatus.textContent = '图片索引加载失败，请稍后重试。';
        console.error('加载错误:', error);
    });

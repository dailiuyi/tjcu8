function createImageLink(image, previewController) {
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
    previewController.bindLink(link, image);

    return linkElement;
}

export function renderGallery({ gallery, galleryStatus, images, previewController }) {
    images.forEach(image => {
        gallery.appendChild(createImageLink(image, previewController));
    });
    galleryStatus.hidden = images.length > 0;
    galleryStatus.textContent = images.length > 0 ? '' : '暂无图片。';
}

export function showGalleryError(galleryStatus) {
    galleryStatus.hidden = false;
    galleryStatus.classList.add('is-error');
    galleryStatus.textContent = '图片索引加载失败，请稍后重试。';
}

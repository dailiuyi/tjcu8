import { loadImageIndex } from './image-index/data.js';
import { renderGallery, showGalleryError } from './image-index/gallery.js';
import { createPreviewController } from './image-index/preview.js';

const pageElements = {
    gallery: document.getElementById('link-gallery'),
    galleryStatus: document.getElementById('gallery-status'),
    preview: document.getElementById('preview'),
    previewStatus: document.getElementById('preview-status'),
    previewImage: document.getElementById('preview-image')
};

function requirePageElements(elements) {
    if (Object.values(elements).some(element => !element)) {
        throw new Error('图片索引页面缺少必要元素');
    }
}

requirePageElements(pageElements);
const previewController = createPreviewController(pageElements);

loadImageIndex('json/image_index.json')
    .then(images => {
        renderGallery({
            gallery: pageElements.gallery,
            galleryStatus: pageElements.galleryStatus,
            images,
            previewController
        });
    })
    .catch(error => {
        showGalleryError(pageElements.galleryStatus);
        console.error('加载错误:', error);
    });

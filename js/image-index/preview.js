const PREVIEW_HIDE_DELAY_MS = 180;

export function createPreviewController(
    { preview, previewStatus, previewImage },
    { hideDelayMs = PREVIEW_HIDE_DELAY_MS } = {}
) {
    let hideTimer = null;
    let previewRequestId = 0;

    function positionPreview(left, top) {
        const margin = 12;
        const maximumLeft = window.scrollX + window.innerWidth - preview.offsetWidth - margin;
        const maximumTop = window.scrollY + window.innerHeight - preview.offsetHeight - margin;

        preview.style.left = `${Math.max(window.scrollX + margin, Math.min(left, maximumLeft))}px`;
        preview.style.top = `${Math.max(window.scrollY + margin, Math.min(top, maximumTop))}px`;
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
        }, hideDelayMs);
    }

    function bindLink(link, image) {
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
    }

    return { bindLink };
}

import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

async function importSource(relativePath) {
    const sourceUrl = new URL(`../${relativePath}`, import.meta.url);
    const source = await readFile(sourceUrl, 'utf8');
    const encoded = Buffer.from(source).toString('base64');
    return import(`data:text/javascript;base64,${encoded}`);
}

class FakeClassList {
    constructor() {
        this.values = new Set();
    }

    add(value) {
        this.values.add(value);
    }

    remove(value) {
        this.values.delete(value);
    }

    contains(value) {
        return this.values.has(value);
    }
}

function createFakeElement(tagName = 'div') {
    return {
        tagName,
        children: [],
        attributes: {},
        listeners: {},
        classList: new FakeClassList(),
        className: '',
        hidden: false,
        style: {},
        textContent: '',
        appendChild(child) {
            this.children.push(child);
        },
        setAttribute(name, value) {
            this.attributes[name] = value;
        },
        addEventListener(name, listener) {
            this.listeners[name] = listener;
        },
        getBoundingClientRect() {
            return { left: 100, right: 200, top: 80 };
        }
    };
}

const dataModule = await importSource('js/image-index/data.js');
const galleryModule = await importSource('js/image-index/gallery.js');
const previewModule = await importSource('js/image-index/preview.js');
const payload = JSON.parse(
    await readFile(new URL('../pages/json/image_index.json', import.meta.url), 'utf8')
);
const images = dataModule.validateImageIndex(payload);

assert.equal(images.length, payload.images.length);
assert.throws(
    () => dataModule.validateImageIndex({ version: 2, images: [] }),
    /图片索引数据契约不匹配/
);
assert.throws(
    () => dataModule.validateImageIndex({
        version: 1,
        images: [{ id: 'x', src: '..\\image\\x.jpg', album: 'x', caption: 'x', alt: 'x' }]
    }),
    /包含无效 URL/
);

globalThis.fetch = async url => {
    assert.equal(url, 'json/image_index.json');
    return { ok: true, json: async () => payload };
};
assert.equal(
    (await dataModule.loadImageIndex('json/image_index.json')).length,
    images.length
);
globalThis.fetch = async () => ({ ok: false, status: 503 });
await assert.rejects(
    dataModule.loadImageIndex('json/image_index.json'),
    /图片索引请求失败: HTTP 503/
);

globalThis.document = {
    activeElement: null,
    createElement: createFakeElement
};
globalThis.window = {
    scrollX: 0,
    scrollY: 0,
    innerWidth: 1024,
    innerHeight: 768,
    clearTimeout,
    setTimeout
};

const gallery = createFakeElement('ul');
const galleryStatus = createFakeElement('p');
const bindings = [];
const previewControllerStub = {
    bindLink(link, image) {
        bindings.push({ link, image });
    }
};
galleryModule.renderGallery({
    gallery,
    galleryStatus,
    images: images.slice(0, 2),
    previewController: previewControllerStub
});
assert.equal(gallery.children.length, 2);
assert.equal(bindings.length, 2);
assert.equal(gallery.children[0].children[0].href, images[0].src);
assert.equal(gallery.children[0].children[0].attributes['aria-controls'], 'preview');
assert.equal(galleryStatus.hidden, true);

const emptyStatus = createFakeElement('p');
galleryModule.renderGallery({
    gallery: createFakeElement('ul'),
    galleryStatus: emptyStatus,
    images: [],
    previewController: previewControllerStub
});
assert.equal(emptyStatus.hidden, false);
assert.equal(emptyStatus.textContent, '暂无图片。');
galleryModule.showGalleryError(emptyStatus);
assert.equal(emptyStatus.textContent, '图片索引加载失败，请稍后重试。');
assert.equal(emptyStatus.classList.contains('is-error'), true);

const preview = createFakeElement();
preview.hidden = true;
preview.offsetWidth = 220;
preview.offsetHeight = 120;
const previewStatus = createFakeElement('p');
const previewImage = createFakeElement('img');
previewImage.hidden = true;
const previewController = previewModule.createPreviewController(
    { preview, previewStatus, previewImage },
    { hideDelayMs: 0 }
);
const previewLink = createFakeElement('a');
previewController.bindLink(previewLink, images[0]);
previewLink.listeners.mouseenter({ pageX: 300, pageY: 200 });
assert.equal(preview.hidden, false);
assert.equal(preview.style.left, '312px');
assert.equal(preview.style.top, '212px');
previewLink.listeners.mousemove({ pageX: 350, pageY: 250 });
assert.equal(preview.style.left, '362px');
assert.equal(preview.style.top, '262px');
previewLink.listeners.mouseleave();
await new Promise(resolve => setTimeout(resolve, 5));
assert.equal(preview.hidden, true);

previewLink.listeners.focus();
assert.equal(preview.hidden, false);
assert.equal(preview.classList.contains('show'), true);
assert.equal(previewStatus.textContent, '正在加载预览…');
assert.equal(previewImage.alt, images[0].alt);
assert.equal(previewImage.src, images[0].src);
previewImage.onload();
assert.equal(previewStatus.hidden, true);
assert.equal(previewImage.hidden, false);
previewLink.listeners.keydown({ key: 'Escape' });
await new Promise(resolve => setTimeout(resolve, 5));
assert.equal(preview.hidden, true);

previewLink.listeners.focus();
previewImage.onerror();
assert.equal(previewImage.hidden, true);
assert.equal(previewStatus.classList.contains('is-error'), true);
assert.equal(previewStatus.textContent, '预览加载失败，可点击链接打开原图。');

console.log(
    `Image index JavaScript check passed: ${images.length} records, ` +
    'data loading, gallery rendering, pointer/keyboard preview states.'
);

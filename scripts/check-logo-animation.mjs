import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const source = await readFile(
    new URL('../js/logo-animation.js', import.meta.url),
    'utf8'
);
const encoded = Buffer.from(source).toString('base64');
const { initializeLogoAnimation } = await import(
    `data:text/javascript;base64,${encoded}`
);

class FakeElement {
    constructor() {
        this.listeners = {};
        this.style = {};
        this.image = null;
    }

    querySelector(selector) {
        return selector === 'img' ? this.image : null;
    }

    addEventListener(name, listener) {
        this.listeners[name] = listener;
    }

    removeEventListener(name, listener) {
        if (this.listeners[name] === listener) {
            delete this.listeners[name];
        }
    }
}

function createFixture({ reduced = false } = {}) {
    const logo = new FakeElement();
    const logoImage = new FakeElement();
    logo.image = logoImage;
    const motionListeners = {};
    const reducedMotion = {
        matches: reduced,
        addEventListener(name, listener) {
            motionListeners[name] = listener;
        },
        removeEventListener(name, listener) {
            if (motionListeners[name] === listener) {
                delete motionListeners[name];
            }
        }
    };
    const frames = new Map();
    let nextFrameId = 1;
    const view = {
        matchMedia(query) {
            assert.equal(query, '(prefers-reduced-motion: reduce)');
            return reducedMotion;
        },
        setTimeout,
        clearTimeout,
        requestAnimationFrame(callback) {
            const frameId = nextFrameId;
            nextFrameId += 1;
            frames.set(frameId, callback);
            return frameId;
        },
        cancelAnimationFrame(frameId) {
            frames.delete(frameId);
        }
    };
    const root = {
        querySelector(selector) {
            return selector === '.logo' ? logo : null;
        }
    };

    return { logo, logoImage, motionListeners, reducedMotion, frames, root, view };
}

const missing = initializeLogoAnimation({
    root: { querySelector: () => null },
    view: {},
    startDelayMs: 0
});
assert.equal(missing, null);

const fixture = createFixture();
const controller = initializeLogoAnimation({
    root: fixture.root,
    view: fixture.view,
    startDelayMs: 0
});
assert.ok(controller);
assert.deepEqual(
    Object.keys(fixture.logo.listeners).sort(),
    ['blur', 'click', 'keydown', 'mouseenter', 'mouseleave'].sort()
);

fixture.logo.listeners.mouseenter();
await new Promise(resolve => setTimeout(resolve, 5));
assert.equal(fixture.logoImage.style.transform, 'rotate(25deg)');
assert.equal(fixture.frames.size, 1);
const [firstFrameId, firstFrame] = fixture.frames.entries().next().value;
fixture.frames.delete(firstFrameId);
firstFrame();
assert.equal(fixture.logoImage.style.transform, 'rotate(30deg)');
fixture.logo.listeners.mouseleave();
assert.equal(fixture.logoImage.style.transform, 'rotate(0deg)');
assert.equal(fixture.frames.size, 0);

fixture.logo.listeners.click();
await new Promise(resolve => setTimeout(resolve, 5));
assert.equal(fixture.logoImage.style.transform, 'rotate(25deg)');
fixture.logo.listeners.keydown({ key: 'Escape' });
assert.equal(fixture.logoImage.style.transform, 'rotate(0deg)');
assert.equal(fixture.frames.size, 0);

fixture.logo.listeners.click();
await new Promise(resolve => setTimeout(resolve, 5));
fixture.reducedMotion.matches = true;
fixture.motionListeners.change({ matches: true });
assert.equal(fixture.logoImage.style.transform, 'rotate(0deg)');
assert.equal(fixture.frames.size, 0);
fixture.logo.listeners.click();
await new Promise(resolve => setTimeout(resolve, 5));
assert.equal(fixture.frames.size, 0);

controller.destroy();
assert.deepEqual(Object.keys(fixture.logo.listeners), []);
assert.equal(fixture.motionListeners.change, undefined);

console.log(
    'Logo animation check passed: missing elements, original timing, pointer, ' +
    'keyboard, and reduced-motion boundaries.'
);

import assert from 'node:assert/strict';
import { readdir, readFile, stat } from 'node:fs/promises';
import { extname, join, relative, resolve } from 'node:path';

const projectRoot = resolve(import.meta.dirname, '..');
const outputRoot = join(projectRoot, 'dist');
const pagePaths = [
    'index.html',
    'pages/about.html',
    'pages/services.html',
    'pages/contact.html',
    'pages/image-index.html'
];
const imageExtensions = new Set(['.gif', '.jpeg', '.jpg', '.png']);

async function listFiles(directory) {
    const entries = await readdir(directory, { withFileTypes: true });
    const nestedFiles = await Promise.all(entries.map(async entry => {
        const path = join(directory, entry.name);
        return entry.isDirectory() ? listFiles(path) : [path];
    }));
    return nestedFiles.flat();
}

function pageText(html) {
    return html
        .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '')
        .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '')
        .replace(/<[^>]+>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

function localReferences(html) {
    return [...html.matchAll(/\b(?:href|src)=["']([^"']+)["']/gi)]
        .map(match => match[1])
        .filter(reference => !/^(?:[a-z]+:|#|\/\/)/i.test(reference));
}

const builtPages = (await listFiles(outputRoot))
    .filter(path => extname(path).toLowerCase() === '.html')
    .map(path => relative(outputRoot, path).replaceAll('\\', '/'))
    .sort();
assert.deepEqual(builtPages, [...pagePaths].sort());

for (const pagePath of pagePaths) {
    const sourceHtml = await readFile(join(projectRoot, pagePath), 'utf8');
    const outputPath = join(outputRoot, pagePath);
    const outputHtml = await readFile(outputPath, 'utf8');
    assert.equal(
        [...outputHtml.matchAll(/data-vue-shell=/g)].length,
        2,
        `${pagePath} must retain two Vue fallback shells`
    );
    assert.equal(
        pageText(outputHtml),
        pageText(sourceHtml),
        `${pagePath} visible text changed during build`
    );

    for (const reference of localReferences(outputHtml)) {
        const cleanReference = decodeURIComponent(reference.split(/[?#]/, 1)[0]);
        const target = resolve(outputPath, '..', cleanReference);
        assert.ok(
            target.startsWith(outputRoot),
            `${pagePath} reference escapes dist: ${reference}`
        );
        assert.ok((await stat(target)).isFile(), `${pagePath} missing ${reference}`);
    }
}

const sourceImages = (await listFiles(join(projectRoot, 'image')))
    .filter(path => imageExtensions.has(extname(path).toLowerCase()));
const outputImages = (await listFiles(join(outputRoot, 'image')))
    .filter(path => imageExtensions.has(extname(path).toLowerCase()));
for (const sourceImage of sourceImages) {
    const imageId = relative(join(projectRoot, 'image'), sourceImage);
    assert.ok(
        outputImages.includes(join(outputRoot, 'image', imageId)),
        `dist is missing source image: ${imageId}`
    );
}

const imageIndex = JSON.parse(
    await readFile(join(outputRoot, 'pages/json/image_index.json'), 'utf8')
);
assert.equal(imageIndex.images.length, sourceImages.length);
const builtJavaScriptPaths = await listFiles(join(outputRoot, 'js'));
const builtJavaScript = (
    await Promise.all(builtJavaScriptPaths.map(path => readFile(path, 'utf8')))
).join('\n');
for (const marker of [
    'data-vue-shell',
    '播放呼气之窝 Logo 动画',
    '未知页面布局',
    '版权所有,未经许可不得转载'
]) {
    assert.ok(builtJavaScript.includes(marker), `Vue bundle marker missing: ${marker}`);
}
assert.ok(builtJavaScriptPaths.length > 0);
assert.ok((await listFiles(join(outputRoot, 'css'))).length > 0);
assert.equal(
    (await listFiles(outputRoot)).some(path => extname(path) === '.vue'),
    false,
    'dist must not expose Vue source files'
);

console.log(
    `Built site check passed: ${pagePaths.length} pages, ` +
    `${sourceImages.length} source images, Vue shells, bundle markers and valid references.`
);
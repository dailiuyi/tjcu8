import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { renderToString } from '@vue/server-renderer';
import { createSSRApp } from 'vue';
import { createServer } from 'vite';
import {
    PAGE_CONFIGS,
    createFooterProps,
    createHeaderProps
} from '../js/shared-layout/config.js';

const projectRoot = resolve(import.meta.dirname, '..');
const vite = await createServer({
    root: projectRoot,
    appType: 'custom',
    logLevel: 'silent',
    server: { middlewareMode: true }
});

function escapePattern(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function extractShell(pageHtml, shellName, pageName) {
    const pageAttribute = shellName === 'header'
        ? ` data-page-name="${escapePattern(pageName)}"`
        : '';
    const pattern = new RegExp(
        `<div data-vue-shell="${shellName}"${pageAttribute}>([\\s\\S]*?)<\\/div>`
    );
    const match = pageHtml.match(pattern);
    assert.ok(match, `${pageName} is missing the ${shellName} fallback`);
    return match[1];
}

function normalizeShell(html) {
    return html
        .replace(/<!--[\s\S]*?-->/g, '')
        .replace(/&copy;/g, '©')
        .replace(/\salt(?=[\s>])/g, ' alt=""')
        .replace(/\svite-ignore=""/g, ' vite-ignore')
        .replace(/>\s+</g, '><')
        .replace(/\s+/g, ' ')
        .trim();
}

try {
    const [
        { default: SiteHeader },
        { default: SiteFooter },
        { initializeSharedLayout }
    ] = await Promise.all([
        vite.ssrLoadModule('/js/components/SiteHeader.vue'),
        vite.ssrLoadModule('/js/components/SiteFooter.vue'),
        vite.ssrLoadModule('/js/shared-layout.js')
    ]);
    assert.equal(
        initializeSharedLayout({ root: { querySelector: () => null } }),
        null
    );
    const renderedFooter = await renderToString(
        createSSRApp(SiteFooter, createFooterProps())
    );

    for (const pageName of Object.keys(PAGE_CONFIGS)) {
        const pageHtml = await readFile(resolve(projectRoot, pageName), 'utf8');
        const renderedHeader = await renderToString(
            createSSRApp(SiteHeader, createHeaderProps(pageName))
        );
        assert.equal(
            normalizeShell(extractShell(pageHtml, 'header', pageName)),
            normalizeShell(renderedHeader),
            `${pageName} header fallback differs from SiteHeader.vue`
        );
        assert.equal(
            normalizeShell(extractShell(pageHtml, 'footer', pageName)),
            normalizeShell(renderedFooter),
            `${pageName} footer fallback differs from SiteFooter.vue`
        );
    }

    assert.throws(() => createHeaderProps('pages/missing.html'), /未知页面布局/);
    console.log(
        `Vue shared layout check passed: ${Object.keys(PAGE_CONFIGS).length} pages, ` +
        'header/footer SSR parity, missing-host and unknown-page boundaries.'
    );
} finally {
    await vite.close();
}
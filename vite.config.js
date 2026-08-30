import { cp } from 'node:fs/promises';
import { resolve } from 'node:path';
import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';

const projectRoot = import.meta.dirname;
const pageEntries = {
    home: 'index.html',
    about: 'pages/about.html',
    services: 'pages/services.html',
    contact: 'pages/contact.html',
    imageIndex: 'pages/image-index.html'
};

function preserveStaticImageUrls() {
    return {
        name: 'preserve-static-image-urls',
        transformIndexHtml: {
            order: 'pre',
            handler(html) {
                return html.replace(/<img\b(?![^>]*\bvite-ignore\b)/g, '<img vite-ignore');
            }
        }
    };
}

function copyRuntimeData() {
    return {
        name: 'copy-runtime-data',
        async closeBundle() {
            await cp(
                resolve(projectRoot, 'image'),
                resolve(projectRoot, 'dist/image'),
                { recursive: true }
            );
            await cp(
                resolve(projectRoot, 'pages/json'),
                resolve(projectRoot, 'dist/pages/json'),
                { recursive: true }
            );
        }
    };
}

export default defineConfig({
    base: './',
    publicDir: false,
    plugins: [vue(), preserveStaticImageUrls(), copyRuntimeData()],
    build: {
        outDir: 'dist',
        emptyOutDir: true,
        rollupOptions: {
            input: Object.fromEntries(
                Object.entries(pageEntries).map(([name, page]) => [
                    name,
                    resolve(projectRoot, page)
                ])
            ),
            output: {
                entryFileNames: 'js/[name]-[hash].js',
                chunkFileNames: 'js/[name]-[hash].js',
                assetFileNames(assetInfo) {
                    const fileName = assetInfo.names?.[0] ?? assetInfo.name ?? '';
                    return fileName.endsWith('.css')
                        ? 'css/[name]-[hash][extname]'
                        : 'image/[name]-[hash][extname]';
                }
            }
        }
    }
});
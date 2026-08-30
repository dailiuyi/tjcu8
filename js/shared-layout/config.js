export const SITE_NAME = '呼气之窝';

export const NAVIGATION_ITEMS = Object.freeze([
    { key: 'home', label: '首页', target: 'index.html' },
    { key: 'about', label: '关于我们', target: 'pages/about.html' },
    { key: 'services', label: '服务', target: 'pages/services.html' },
    { key: 'contact', label: '加入我们', target: 'pages/contact.html' }
]);

export const PAGE_CONFIGS = Object.freeze({
    'index.html': { currentKey: 'home' },
    'pages/about.html': { currentKey: 'about' },
    'pages/services.html': { currentKey: 'services' },
    'pages/contact.html': { currentKey: 'contact' },
    'pages/image-index.html': { currentKey: 'services' }
});

export const FOOTER_LINES = Object.freeze([
    '© 2024 呼气之窝. 保留所有权利.',
    '版权所有,未经许可不得转载.',
    '收买h7不在版权考虑范围之内'
]);

export function relativeHref(pageName, targetName) {
    const sourceParts = pageName.split('/').slice(0, -1);
    const targetParts = targetName.split('/');
    let commonLength = 0;

    while (
        commonLength < sourceParts.length &&
        commonLength < targetParts.length &&
        sourceParts[commonLength] === targetParts[commonLength]
    ) {
        commonLength += 1;
    }

    const parentSegments = sourceParts.length - commonLength;
    const targetSegments = targetParts.slice(commonLength);
    return `${'../'.repeat(parentSegments)}${targetSegments.join('/')}`;
}

export function createHeaderProps(pageName) {
    const pageConfig = PAGE_CONFIGS[pageName];
    if (!pageConfig) {
        throw new Error(`未知页面布局: ${pageName}`);
    }

    const navigation = Object.fromEntries(
        NAVIGATION_ITEMS.map(item => [
            item.key,
            {
                label: item.label,
                href: relativeHref(pageName, item.target)
            }
        ])
    );

    return {
        siteName: SITE_NAME,
        logoSrc: relativeHref(pageName, 'image/logo.jpg'),
        navigation,
        currentKey: pageConfig.currentKey
    };
}

export function createFooterProps() {
    return { lines: FOOTER_LINES };
}
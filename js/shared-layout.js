import { createSSRApp } from 'vue';
import SiteFooter from './components/SiteFooter.vue';
import SiteHeader from './components/SiteHeader.vue';
import { createFooterProps, createHeaderProps } from './shared-layout/config.js';

const HEADER_SELECTOR = '[data-vue-shell="header"]';
const FOOTER_SELECTOR = '[data-vue-shell="footer"]';

export function initializeSharedLayout({ root = document } = {}) {
    const headerHost = root.querySelector(HEADER_SELECTOR);
    const footerHost = root.querySelector(FOOTER_SELECTOR);
    if (!headerHost || !footerHost) {
        return null;
    }

    const pageName = headerHost.dataset.pageName;
    const headerApp = createSSRApp(SiteHeader, createHeaderProps(pageName));
    const footerApp = createSSRApp(SiteFooter, createFooterProps());
    headerApp.mount(headerHost);
    footerApp.mount(footerHost);

    return {
        unmount() {
            headerApp.unmount();
            footerApp.unmount();
        }
    };
}
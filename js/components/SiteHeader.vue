<script setup>
const props = defineProps({
    siteName: {
        type: String,
        required: true
    },
    logoSrc: {
        type: String,
        required: true
    },
    navigation: {
        type: Object,
        required: true
    },
    currentKey: {
        type: String,
        required: true
    }
});

function currentPage(key) {
    return props.currentKey === key ? 'page' : undefined;
}
</script>

<template>
    <header class="header">
        <button class="logo" type="button" aria-label="播放呼气之窝 Logo 动画">
            <img vite-ignore :src="logoSrc" alt="">
            <span>{{ siteName }}</span>
        </button>
        <nav class="navigation" aria-label="主导航">
            <ul>
                <li>
                    <a :href="navigation.home.href" :aria-current="currentPage('home')">{{ navigation.home.label }}</a>
                </li>
                <li>
                    <a :href="navigation.about.href" :aria-current="currentPage('about')">{{ navigation.about.label }}</a>
                </li>
                <li>
                    <a :href="navigation.services.href" :aria-current="currentPage('services')">{{ navigation.services.label }}</a>
                </li>
                <li>
                    <a :href="navigation.contact.href" :aria-current="currentPage('contact')">{{ navigation.contact.label }}</a>
                </li>
            </ul>
        </nav>
    </header>
</template>
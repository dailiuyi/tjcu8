<script setup>
defineProps({
    lines: {
        type: Array,
        required: true
    }
});
</script>

<template>
    <footer>
        <p>{{ lines[0] }}</p>
        <p>{{ lines[1] }}</p>
        <p class="strikethrough">{{ lines[2] }}</p>
    </footer>
</template>
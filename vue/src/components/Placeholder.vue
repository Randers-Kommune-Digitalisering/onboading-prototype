<script setup>
    const props = defineProps({
        height: {
            type: Number,
            required: false,
            default: 7.2
        },
        dark: {
            type: Boolean,
            required: false,
            default: false
        }
    })
</script>

<template>
    <div :class="['card', {'dark': props.dark}]" :style="'height:' + height + 'rem'">
        <div class="card-header">
            <p class="placeholderText"></p>
        </div>
        <div class="card-content always-show">
            <p class="placeholderText bodyPlaceholder"></p>
        </div>
    </div>
</template>

<style scoped>
    .placeholderText {
        border-radius: 0.2rem;
        background-color: rgb(223, 216, 208);
        height: 1.5rem;
        width: 50%;
    }
    .dark .placeholderText {
        background-color: rgb(206, 198, 189);
    }
    .bodyPlaceholder {
        width: 90%;
        height:1.7rem;
        transform: translateY(-0.2rem);
    }
</style>
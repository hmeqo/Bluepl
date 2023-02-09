<template>
    <div class="group flex justify-center items-center p-1.5 w-full h-full bg-green-500 rounded-full shadow-md cursor-pointer">
        <div class="main relative flex justify-center items-center w-full h-full">
            <div class="border-t-2 w-full"></div>
            <div class="border-l-2 h-full"></div>
        </div>
    </div>
</template>

<style scoped>
.main>* {
    @apply absolute border-white
}
</style>

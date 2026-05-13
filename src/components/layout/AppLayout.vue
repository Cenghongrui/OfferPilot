<template>
    <div class="app-layout">
        <Sidabar></Sidabar>
        <div class="app-main">
            <Topbar></Topbar>
            <div class="app-content">
                <router-view></router-view>
            </div>
        </div>
    </div>
</template>

<script setup>
import Sidabar from "./Sidebar.vue";
import { useRouter } from "vue-router";
import Topbar from "./Topbar.vue";
const router = useRouter();
</script>

<style lang=scss scoped>
.app-layout {
    display: flex;
    width: 100%;
    height: 100vh;
    overflow: hidden;

    .app-main {
        display: flex;
        flex: 1;
        flex-direction: column;
        height: 100vh;
        min-width: 0;
        overflow: hidden;

        .app-content {
            flex: 1;
            min-height: 0;
            box-sizing: border-box;
            overflow-y: auto;
            padding: 20px;
            background-color: #f6f8fb;
        }
    }
}
</style>

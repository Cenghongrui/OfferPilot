<template>
    <div class="topbar">
        <div class="topbar-title">
            {{ router.currentRoute.value.meta.title }}
        </div>
        <div class="topbar-info">
            <div class="date" style="display: flex; align-items: center; gap: 5px;">
                <el-icon>
                    <Calendar />
                </el-icon>
                <div>{{ dayjs(Date.now()).format('YYYY-MM-DD dddd') }}</div>
            </div>
            <el-button class="notice" type="text">
                <el-icon>
                    <Bell />
                </el-icon>
            </el-button>

        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ElIcon, dayjs, } from 'element-plus';
const router = useRouter();



</script>

<style lang="scss" scoped>
.topbar {
    position: sticky;
    top: 0;
    display: flex;
    flex: 0 0 70px;
    height: 70px;
    box-sizing: border-box;
    background-color: #fff;
    z-index: 10;
    border-bottom: 1px solid #e0e0e0;
    justify-content: space-between;
    align-items: center;
    padding-left: 30px;
    padding-right: 30px;
    color: #000;

    .topbar-title {
        font-size: 24px;
        font-weight: bold;
    }


    .topbar-info {
        display: flex;
        align-items: center;
        gap: 20px;

        .notice {
            width: 40px;
            height: 30px;
            font-size: 18px;
            transition: background-color 0.5s ease, color 0.5s ease;

            .el-icon {
                color: #000;
            }

            &:hover {
                background-color: #055De5;

                .el-icon {
                    color: #fff;
                }
            }
        }

    }

}
</style>

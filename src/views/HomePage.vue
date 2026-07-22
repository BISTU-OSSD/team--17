<template>
<div>
<h1>给开源仓库做体检</h1>
<input v-model="repoName" placeholder="输入格式：owner/repo">
<button @click="analyze">开始分析</button>
<p v-if="error" style="color:red">{{ error }}</p >
</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const repoName = ref('')
const error = ref('')
const analyze = () => {
error.value = ''
let arr = repoName.value.split('/')
if(arr.length !== 2){
error.value = '格式错误'
return
}
router.push(`/report/${arr[0]}/${arr[1]}`)
}
</script>
// 创建Jenkins流水线
pipeline {
    triggers {
        // 定时触发
        cron('H */4 * * *')
        // GitHub Webhook触发
        githubPush()
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        retry(2)
        disableConcurrentBuilds()
    }
}
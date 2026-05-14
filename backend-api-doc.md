# OfferPilot 后端接口文档

## 1. 文档说明

本文档根据当前前端页面功能整理，用于后端接口设计与前后端联调。OfferPilot 是面向前端实习求职准备的训练工作台，核心模块包括账号登录注册、今日工作台、面试题库、算法练习、面经笔记、投递看板、模拟面试、个人中心与设置。

## 2. 基础约定

### 2.1 请求基础信息

- Base URL：`/api/v1`
- 请求格式：`Content-Type: application/json`
- 响应格式：JSON
- 时间格式：ISO 8601，例如 `2026-05-14T09:30:00+08:00`
- 日期格式：`YYYY-MM-DD`
- 认证方式：登录后通过 `Authorization: Bearer <accessToken>` 携带令牌

### 2.2 通用响应结构

成功响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

分页响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "list": [],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 100
    }
  }
}
```

错误响应：

```json
{
  "code": 40001,
  "message": "邮箱或密码不正确",
  "data": null
}
```

### 2.3 常用错误码

| code | 含义 |
| --- | --- |
| 0 | 成功 |
| 40000 | 请求参数错误 |
| 40001 | 登录失败 |
| 40002 | 邮箱已注册 |
| 40100 | 未登录或 token 无效 |
| 40300 | 无权限访问 |
| 40400 | 资源不存在 |
| 40900 | 数据状态冲突 |
| 50000 | 服务端异常 |

## 3. 枚举定义

### 3.1 题目分类 `QuestionCategory`

| 值 | 含义 |
| --- | --- |
| `CSS` | CSS |
| `JavaScript` | JavaScript |
| `Vue` | Vue |
| `Network` | 计算机网络 |
| `Algorithm` | 算法 |

### 3.2 难度 `Difficulty`

| 值 | 含义 |
| --- | --- |
| `easy` | 简单 |
| `medium` | 中等 |
| `hard` | 困难 |

### 3.3 算法状态 `ProblemStatus`

| 值 | 含义 |
| --- | --- |
| `todo` | 未开始 |
| `doing` | 进行中 |
| `done` | 已完成 |

### 3.4 投递阶段 `ApplicationStage`

| 值 | 含义 |
| --- | --- |
| `todo` | 待投递 |
| `applied` | 已投递 |
| `exam` | 笔试 |
| `interview_1` | 一面 |
| `interview_2` | 二面 |
| `hr` | HR 面 |
| `offer` | Offer |
| `closed` | 已结束 |

### 3.5 面经结果 `ExperienceResult`

| 值 | 含义 |
| --- | --- |
| `pending` | 跟进中 |
| `passed` | 通过 |
| `failed` | 已结束 |

### 3.6 模拟面试状态 `MockSessionStatus`

| 值 | 含义 |
| --- | --- |
| `idle` | 未开始 |
| `running` | 进行中 |
| `paused` | 已暂停 |
| `finished` | 已完成 |

## 4. 账号与用户

### 4.1 注册

- Method：`POST`
- Path：`/auth/register`
- Auth：否

请求体：

```json
{
  "name": "前端实习生",
  "email": "name@example.com",
  "password": "123456"
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "user": {
      "id": "user_001",
      "name": "前端实习生",
      "email": "name@example.com",
      "goal": "每天完成 2 小时学习与 3 道算法题",
      "notifications": true,
      "createdAt": "2026-05-14T09:30:00+08:00"
    },
    "accessToken": "jwt-token"
  }
}
```

### 4.2 登录

- Method：`POST`
- Path：`/auth/login`
- Auth：否

请求体：

```json
{
  "email": "name@example.com",
  "password": "123456"
}
```

响应字段同注册接口。

### 4.3 获取当前用户

- Method：`GET`
- Path：`/users/me`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": "user_001",
    "name": "前端实习生",
    "email": "name@example.com",
    "goal": "每天完成 2 小时学习与 3 道算法题",
    "notifications": true
  }
}
```

### 4.4 更新个人设置

- Method：`PATCH`
- Path：`/users/me`
- Auth：是

请求体：

```json
{
  "name": "前端冲刺选手",
  "goal": "每天复习 5 道题，并完成 1 次投递跟进",
  "notifications": true
}
```

响应：更新后的用户信息。

### 4.5 退出登录

- Method：`POST`
- Path：`/auth/logout`
- Auth：是

说明：如果后端采用无状态 JWT，此接口可仅用于前端清理状态；如果有 refresh token 或黑名单机制，则在服务端失效 token。

## 5. 今日工作台

### 5.1 获取工作台概览

- Method：`GET`
- Path：`/dashboard/overview`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "stats": {
      "studyHoursToday": 2.6,
      "reviewTodoCount": 12,
      "algorithmSolvedCount": 48,
      "applicationCount": 8,
      "mockInterviewCount": 2
    },
    "changes": {
      "studyHoursToday": -3,
      "reviewTodoCount": -3,
      "algorithmSolvedCount": 16,
      "applicationCount": 2,
      "mockInterviewCount": 1
    },
    "mastery": {
      "overall": 68,
      "levels": [
        { "label": "已掌握", "value": 32 },
        { "label": "较熟悉", "value": 36 },
        { "label": "一般", "value": 18 },
        { "label": "较弱", "value": 10 },
        { "label": "未掌握", "value": 4 }
      ]
    },
    "weakPoints": [
      { "name": "Vue3 响应式原理", "mastery": 40 },
      { "name": "虚拟 DOM", "mastery": 45 }
    ]
  }
}
```

### 5.2 获取今日学习计划

- Method：`GET`
- Path：`/dashboard/today-plan`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    {
      "id": "plan_001",
      "title": "Vue3 响应式原理",
      "type": "知识点",
      "startTime": "09:00",
      "endTime": "10:00",
      "completed": true
    }
  ]
}
```

### 5.3 更新计划完成状态

- Method：`PATCH`
- Path：`/dashboard/today-plan/{planId}`
- Auth：是

请求体：

```json
{
  "completed": true
}
```

## 6. 面试题库

### 6.1 获取题目列表

- Method：`GET`
- Path：`/questions`
- Auth：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `keyword` | string | 否 | 搜索标题、答案、标签 |
| `category` | string | 否 | 题目分类，不传表示全部 |
| `difficulty` | string | 否 | `easy` / `medium` / `hard` |
| `starred` | boolean | 否 | 是否只看收藏 |
| `mastered` | boolean | 否 | 是否已掌握 |
| `page` | number | 否 | 默认 1 |
| `pageSize` | number | 否 | 默认 20 |

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "list": [
      {
        "id": "q_js_001",
        "title": "介绍一下事件循环",
        "category": "JavaScript",
        "difficulty": "medium",
        "tags": ["event-loop", "promise", "async"],
        "answer": "同步任务先进入调用栈...",
        "followUps": ["Promise.then 属于什么任务？"],
        "pitfalls": ["不要把 async 函数本身说成微任务"],
        "mastered": false,
        "starred": true,
        "lastReviewedAt": "2026-05-13",
        "note": "结合页面渲染时机再复盘一次。"
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 1
    }
  }
}
```

### 6.2 获取题目详情

- Method：`GET`
- Path：`/questions/{questionId}`
- Auth：是

### 6.3 新增题目

- Method：`POST`
- Path：`/questions`
- Auth：是

请求体：

```json
{
  "title": "Vue3 响应式原理是什么？",
  "category": "Vue",
  "difficulty": "medium",
  "tags": ["proxy", "reactivity"],
  "answer": "Vue3 使用 Proxy 拦截对象读写...",
  "followUps": ["ref 和 reactive 的区别？"],
  "pitfalls": ["不要忽略依赖收集和触发更新是两个阶段。"],
  "note": ""
}
```

### 6.4 更新题目

- Method：`PATCH`
- Path：`/questions/{questionId}`
- Auth：是

可更新字段：`title`、`category`、`difficulty`、`tags`、`answer`、`followUps`、`pitfalls`、`note`、`mastered`、`starred`、`lastReviewedAt`。

### 6.5 删除题目

- Method：`DELETE`
- Path：`/questions/{questionId}`
- Auth：是

### 6.6 切换收藏

- Method：`PATCH`
- Path：`/questions/{questionId}/star`
- Auth：是

请求体：

```json
{
  "starred": true
}
```

### 6.7 更新掌握状态

- Method：`PATCH`
- Path：`/questions/{questionId}/mastery`
- Auth：是

请求体：

```json
{
  "mastered": true,
  "lastReviewedAt": "2026-05-14"
}
```

### 6.8 获取题库统计

- Method：`GET`
- Path：`/questions/stats`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "total": 4,
    "starred": 2,
    "reviewTodo": 3,
    "byCategory": [
      { "category": "Vue", "total": 1, "mastered": 0 }
    ]
  }
}
```

## 7. 算法练习

### 7.1 获取算法题列表

- Method：`GET`
- Path：`/algorithms`
- Auth：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `status` | string | 否 | `todo` / `doing` / `done` |
| `difficulty` | string | 否 | 难度 |
| `keyword` | string | 否 | 搜索标题、标签 |
| `page` | number | 否 | 页码 |
| `pageSize` | number | 否 | 每页数量 |

响应数据项：

```json
{
  "id": "lc_003",
  "title": "无重复字符的最长子串",
  "leetcodeUrl": "https://leetcode.cn/problems/longest-substring-without-repeating-characters/",
  "difficulty": "medium",
  "tags": ["sliding-window", "hash-map"],
  "status": "doing",
  "description": "给定一个字符串，找出其中不含重复字符的最长子串长度。",
  "idea": "使用滑动窗口维护当前无重复区间...",
  "complexity": "时间复杂度 O(n)，空间复杂度 O(k)。",
  "codeDraft": "function lengthOfLongestSubstring(s) {}",
  "notes": "注意 left 只能向右移动，不能回退。",
  "testCases": [
    { "id": "case_001", "input": "\"abcabcbb\"", "expected": "3" }
  ],
  "updatedAt": "2026-05-14T09:30:00+08:00"
}
```

### 7.2 获取算法题详情

- Method：`GET`
- Path：`/algorithms/{problemId}`
- Auth：是

### 7.3 新增算法题

- Method：`POST`
- Path：`/algorithms`
- Auth：是

请求体字段：`title`、`leetcodeUrl`、`difficulty`、`tags`、`description`、`idea`、`complexity`、`testCases`。

### 7.4 更新算法题

- Method：`PATCH`
- Path：`/algorithms/{problemId}`
- Auth：是

可更新字段：`title`、`leetcodeUrl`、`difficulty`、`tags`、`status`、`description`、`idea`、`complexity`、`codeDraft`、`notes`、`testCases`。

### 7.5 保存代码草稿

- Method：`PATCH`
- Path：`/algorithms/{problemId}/code-draft`
- Auth：是

请求体：

```json
{
  "codeDraft": "function lengthOfLongestSubstring(s) {\n  return 0\n}"
}
```

### 7.6 运行测试用例

- Method：`POST`
- Path：`/algorithms/{problemId}/run`
- Auth：是

请求体：

```json
{
  "code": "function lengthOfLongestSubstring(s) { return 3 }",
  "testCases": [
    { "input": "\"abcabcbb\"", "expected": "3" }
  ]
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "status": "passed",
    "results": [
      {
        "input": "\"abcabcbb\"",
        "expected": "3",
        "actual": "3",
        "passed": true,
        "runtimeMs": 3
      }
    ]
  }
}
```

说明：MVP 阶段可由前端模拟运行状态；如果后端执行用户代码，需要放入沙箱环境，并限制运行时间、内存和可访问 API。

### 7.7 获取算法统计

- Method：`GET`
- Path：`/algorithms/stats`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "total": 3,
    "done": 1,
    "doing": 1,
    "todo": 1,
    "completionRate": 33,
    "reviewCountThisWeek": 2
  }
}
```

## 8. 面经笔记

### 8.1 获取面经列表

- Method：`GET`
- Path：`/experiences`
- Auth：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `round` | string | 否 | `一面` / `二面` / `HR 面` / `Offer` |
| `result` | string | 否 | `pending` / `passed` / `failed` |
| `keyword` | string | 否 | 搜索公司、岗位、问题 |
| `page` | number | 否 | 页码 |
| `pageSize` | number | 否 | 每页数量 |

响应数据项：

```json
{
  "id": "exp_001",
  "company": "字节跳动",
  "role": "前端实习生",
  "city": "上海",
  "date": "2026-04-18",
  "round": "一面",
  "result": "pending",
  "questions": [
    { "category": "Vue", "content": "Vue3 响应式原理是什么？" }
  ],
  "review": {
    "good": "项目背景和路由权限讲得比较完整。",
    "stuck": "网络缓存回答不够细。",
    "action": "补强强缓存、协商缓存和部署缓存策略。"
  },
  "markdown": "### 复盘\n- 响应式原理需要补充 track/trigger。",
  "createdAt": "2026-05-14T09:30:00+08:00",
  "updatedAt": "2026-05-14T09:30:00+08:00"
}
```

### 8.2 获取面经详情

- Method：`GET`
- Path：`/experiences/{experienceId}`
- Auth：是

### 8.3 新增面经

- Method：`POST`
- Path：`/experiences`
- Auth：是

请求体：

```json
{
  "company": "小红书",
  "role": "前端实习生",
  "city": "上海",
  "date": "2026-05-14",
  "round": "一面",
  "result": "pending",
  "questions": [
    { "category": "待整理", "content": "记录本轮面试问题" }
  ],
  "review": {
    "good": "待补充",
    "stuck": "待补充",
    "action": "待补充"
  },
  "markdown": ""
}
```

### 8.4 更新面经

- Method：`PATCH`
- Path：`/experiences/{experienceId}`
- Auth：是

可更新字段同新增接口。

### 8.5 删除面经

- Method：`DELETE`
- Path：`/experiences/{experienceId}`
- Auth：是

### 8.6 导出面经 JSON

- Method：`GET`
- Path：`/experiences/export`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "filename": "offerpilot-experiences-2026-05-14.json",
    "items": []
  }
}
```

### 8.7 导入面经 JSON

- Method：`POST`
- Path：`/experiences/import`
- Auth：是

请求体：

```json
{
  "items": []
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "created": 3,
    "updated": 0,
    "failed": 0
  }
}
```

## 9. 投递看板

### 9.1 获取投递列表

- Method：`GET`
- Path：`/applications`
- Auth：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `stage` | string | 否 | 投递阶段 |
| `keyword` | string | 否 | 搜索公司、岗位、城市 |

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    {
      "id": "app_001",
      "company": "腾讯",
      "role": "前端开发实习生",
      "city": "深圳",
      "source": "官网",
      "stage": "interview_1",
      "deadline": "2026-05-30",
      "nextAction": "准备 Vue 项目深挖",
      "notes": "重点复习组件通信和权限路由",
      "sortOrder": 1000,
      "createdAt": "2026-05-14T09:30:00+08:00",
      "updatedAt": "2026-05-14T09:30:00+08:00"
    }
  ]
}
```

### 9.2 获取投递详情

- Method：`GET`
- Path：`/applications/{applicationId}`
- Auth：是

### 9.3 新增投递

- Method：`POST`
- Path：`/applications`
- Auth：是

请求体：

```json
{
  "company": "小红书",
  "role": "前端开发实习生",
  "city": "上海",
  "source": "Boss 直聘",
  "stage": "todo",
  "deadline": "2026-06-15",
  "nextAction": "补充简历并跟进进度",
  "notes": "新建记录"
}
```

### 9.4 更新投递

- Method：`PATCH`
- Path：`/applications/{applicationId}`
- Auth：是

可更新字段：`company`、`role`、`city`、`source`、`stage`、`deadline`、`nextAction`、`notes`、`sortOrder`。

### 9.5 删除投递

- Method：`DELETE`
- Path：`/applications/{applicationId}`
- Auth：是

### 9.6 移动投递卡片

- Method：`PATCH`
- Path：`/applications/{applicationId}/move`
- Auth：是

请求体：

```json
{
  "fromStage": "exam",
  "toStage": "interview_1",
  "sortOrder": 1000
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": "app_002",
    "stage": "interview_1",
    "sortOrder": 1000
  }
}
```

说明：前端拖拽时可以先乐观更新界面，接口失败后回滚到 `fromStage`。

### 9.7 获取投递统计

- Method：`GET`
- Path：`/applications/stats`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "total": 4,
    "interviewing": 1,
    "offer": 1,
    "byStage": [
      { "stage": "todo", "count": 0 },
      { "stage": "applied", "count": 1 },
      { "stage": "exam", "count": 1 }
    ]
  }
}
```

## 10. 模拟面试

### 10.1 获取面试模式

- Method：`GET`
- Path：`/mock-interview/modes`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    { "name": "基础八股", "desc": "CSS / JS / 浏览器基础" },
    { "name": "Vue 专项", "desc": "响应式、组件通信、Router" }
  ]
}
```

### 10.2 按模式随机抽题

- Method：`GET`
- Path：`/mock-interview/questions/random`
- Auth：是

查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `mode` | string | 是 | 模式名称 |

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": "mock_q_001",
    "mode": "Vue 专项",
    "title": "Vue3 响应式原理是什么？",
    "prompt": "请从 Proxy、依赖收集、触发更新和视图渲染四个层次讲清楚。",
    "followUps": ["ref 和 reactive 的区别？", "computed 为什么有缓存？"],
    "hint": "提示：可以按 get 收集、set 触发、effect 重新执行来组织。"
  }
}
```

### 10.3 创建模拟面试会话

- Method：`POST`
- Path：`/mock-interview/sessions`
- Auth：是

请求体：

```json
{
  "mode": "Vue 专项",
  "questionIds": ["mock_q_001"]
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": "mock_001",
    "mode": "Vue 专项",
    "status": "running",
    "startedAt": "2026-05-14T09:30:00+08:00",
    "totalSeconds": 0,
    "questionSeconds": 0,
    "questionIds": ["mock_q_001"]
  }
}
```

### 10.4 更新模拟面试会话

- Method：`PATCH`
- Path：`/mock-interview/sessions/{sessionId}`
- Auth：是

请求体：

```json
{
  "status": "running",
  "totalSeconds": 120,
  "questionSeconds": 35,
  "answerNote": "从 Proxy、track、trigger、effect 四步回答。",
  "scores": {
    "accuracy": 4,
    "completeness": 3,
    "expression": 4,
    "projectLink": 3
  }
}
```

### 10.5 生成面试报告

- Method：`POST`
- Path：`/mock-interview/sessions/{sessionId}/report`
- Auth：是

请求体：

```json
{
  "questionId": "mock_q_001",
  "answerNote": "从 Proxy、track、trigger、effect 四步回答。",
  "scores": {
    "accuracy": 4,
    "completeness": 3,
    "expression": 4,
    "projectLink": 3
  },
  "duration": 300
}
```

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "sessionId": "mock_001",
    "total": 14,
    "question": "Vue3 响应式原理是什么？",
    "weakness": "回答结构还可以更完整，追问需要提前准备例子。",
    "suggestion": "复习 Vue 专项 的核心概念，并把本次作答笔记沉淀进面经。",
    "createdAt": "2026-05-14T09:35:00+08:00"
  }
}
```

### 10.6 获取模拟面试历史

- Method：`GET`
- Path：`/mock-interview/sessions`
- Auth：是

查询参数：`mode`、`status`、`page`、`pageSize`。

### 10.7 获取模拟面试统计

- Method：`GET`
- Path：`/mock-interview/stats`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "modeCount": 5,
    "sessionCount": 2,
    "averageScore": 3.5,
    "totalDuration": 1800
  }
}
```

## 11. 个人中心

### 11.1 获取个人中心概览

- Method：`GET`
- Path：`/profile/overview`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "user": {
      "id": "user_001",
      "name": "前端实习生",
      "email": "name@example.com",
      "goal": "每天完成 2 小时学习与 3 道算法题"
    },
    "overview": {
      "reviewTodoCount": 12,
      "activeApplicationCount": 3,
      "mockInterviewAverageScore": 14
    },
    "activities": [
      {
        "id": "act_001",
        "type": "mock",
        "title": "完成 Vue 专项模拟面试",
        "desc": "生成一份复盘报告，建议补充 diff 和 key 的追问。",
        "createdAt": "2026-05-14T09:30:00+08:00"
      }
    ]
  }
}
```

## 12. 通知提醒

### 12.1 获取通知列表

- Method：`GET`
- Path：`/notifications`
- Auth：是

查询参数：`unreadOnly`、`page`、`pageSize`。

响应数据项：

```json
{
  "id": "notice_001",
  "type": "review",
  "title": "题库复习提醒",
  "content": "事件循环和浏览器缓存仍处于待掌握状态。",
  "read": false,
  "createdAt": "2026-05-14T09:30:00+08:00"
}
```

### 12.2 标记通知已读

- Method：`PATCH`
- Path：`/notifications/{notificationId}/read`
- Auth：是

### 12.3 获取未读通知数

- Method：`GET`
- Path：`/notifications/unread-count`
- Auth：是

响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "count": 3
  }
}
```

## 13. 数据模型建议

### 13.1 User

```json
{
  "id": "user_001",
  "name": "前端实习生",
  "email": "name@example.com",
  "passwordHash": "hashed-password",
  "goal": "每天完成 2 小时学习与 3 道算法题",
  "notifications": true,
  "createdAt": "2026-05-14T09:30:00+08:00",
  "updatedAt": "2026-05-14T09:30:00+08:00"
}
```

### 13.2 Question

```json
{
  "id": "q_js_001",
  "userId": "user_001",
  "title": "介绍一下事件循环",
  "category": "JavaScript",
  "difficulty": "medium",
  "tags": ["event-loop", "promise", "async"],
  "answer": "同步任务先进入调用栈...",
  "followUps": ["Promise.then 属于什么任务？"],
  "pitfalls": ["不要把 async 函数本身说成微任务"],
  "mastered": false,
  "starred": true,
  "lastReviewedAt": "2026-05-13",
  "note": "结合页面渲染时机再复盘一次。"
}
```

### 13.3 AlgorithmProblem

```json
{
  "id": "lc_003",
  "userId": "user_001",
  "title": "无重复字符的最长子串",
  "leetcodeUrl": "https://leetcode.cn/problems/longest-substring-without-repeating-characters/",
  "difficulty": "medium",
  "tags": ["sliding-window", "hash-map"],
  "status": "doing",
  "description": "给定一个字符串，找出其中不含重复字符的最长子串长度。",
  "idea": "使用滑动窗口维护当前无重复区间...",
  "complexity": "时间复杂度 O(n)，空间复杂度 O(k)。",
  "codeDraft": "",
  "notes": "",
  "testCases": []
}
```

### 13.4 Experience

```json
{
  "id": "exp_001",
  "userId": "user_001",
  "company": "字节跳动",
  "role": "前端实习生",
  "city": "上海",
  "date": "2026-04-18",
  "round": "一面",
  "result": "pending",
  "questions": [],
  "review": {
    "good": "项目背景和路由权限讲得比较完整。",
    "stuck": "网络缓存回答不够细。",
    "action": "补强强缓存、协商缓存和部署缓存策略。"
  },
  "markdown": ""
}
```

### 13.5 Application

```json
{
  "id": "app_001",
  "userId": "user_001",
  "company": "腾讯",
  "role": "前端开发实习生",
  "city": "深圳",
  "source": "官网",
  "stage": "interview_1",
  "deadline": "2026-05-30",
  "nextAction": "准备 Vue 项目深挖",
  "notes": "重点复习组件通信和权限路由",
  "sortOrder": 1000
}
```

### 13.6 MockSession

```json
{
  "id": "mock_001",
  "userId": "user_001",
  "mode": "Vue 专项",
  "status": "finished",
  "startedAt": "2026-05-14T09:30:00+08:00",
  "finishedAt": "2026-05-14T09:35:00+08:00",
  "duration": 300,
  "questionIds": ["mock_q_001"],
  "answerNote": "从 Proxy、track、trigger、effect 四步回答。",
  "scores": {
    "accuracy": 4,
    "completeness": 3,
    "expression": 4,
    "projectLink": 3
  },
  "report": {
    "total": 14,
    "weakness": "回答结构还可以更完整。",
    "suggestion": "复习 Vue 专项 的核心概念。"
  }
}
```

## 14. 前后端联调优先级

1. 账号注册、登录、获取当前用户、更新设置。
2. 题库列表、筛选、详情、收藏、掌握状态、笔记保存。
3. 投递看板列表、新增、拖拽移动、撤销失败回滚。
4. 面经列表、新增、编辑、导入导出。
5. 算法题列表、草稿保存、状态更新、测试用例运行。
6. 模拟面试抽题、创建会话、更新评分、生成报告、历史记录。
7. 工作台和个人中心统计聚合接口。

## 15. 实现备注

- 所有业务数据建议按 `userId` 隔离，用户只能访问自己的题库、投递、面经和模拟面试记录。
- 列表接口支持分页；投递看板当前数据量小，也可以先返回全量。
- 前端已经有本地演示数据，后端可先按本文档字段返回 mock 数据，待联调稳定后再接数据库。
- 题目收藏、掌握状态、代码草稿、投递拖拽属于高频轻量更新，建议用 `PATCH` 局部更新。
- 工作台、个人中心统计可以由后端聚合，也可以由前端从多个列表接口派生；正式后端建议提供聚合接口以减少首屏请求数量。

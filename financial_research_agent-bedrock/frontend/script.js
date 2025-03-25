document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const queryInput = document.getElementById('query');
    const submitButton = document.getElementById('submit-btn');
    const loadingContainer = document.getElementById('loading');
    const resultsContainer = document.getElementById('results');
    const summaryElement = document.getElementById('summary');
    const reportElement = document.getElementById('report');
    const questionsElement = document.getElementById('questions');
    const verificationElement = document.getElementById('verification');
    const statusMessage = document.getElementById('status-message');

// API端点配置
// 检测是否在本地环境中运行
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// 根据环境选择API端点
const API_URL = isLocalhost 
    ? 'http://localhost:3000/research'  // 本地测试URL
    : 'https://your-api-gateway-url.amazonaws.com/prod/research';  // 生产URL

console.log(`使用API端点: ${API_URL}`);

    // 提交按钮点击事件
    submitButton.addEventListener('click', async function() {
        const query = queryInput.value.trim();
        
        if (!query) {
            alert('请输入研究查询');
            return;
        }
        
        // 显示加载状态
        loadingContainer.style.display = 'block';
        resultsContainer.style.display = 'none';
        submitButton.disabled = true;
        
        try {
            // 更新状态消息
            updateStatus('规划搜索策略...');
            
            // 调用API
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });
            
            if (!response.ok) {
                throw new Error(`API请求失败: ${response.status}`);
            }
            
            updateStatus('处理搜索结果...');
            
            // 解析响应
            const data = await response.json();
            
            // 显示结果
            displayResults(data);
            
        } catch (error) {
            console.error('错误:', error);
            alert(`处理请求时出错: ${error.message}`);
        } finally {
            // 隐藏加载状态
            loadingContainer.style.display = 'none';
            submitButton.disabled = false;
        }
    });

    // 更新状态消息
    function updateStatus(message) {
        statusMessage.textContent = message;
    }

    // 显示结果
    function displayResults(data) {
        // 显示结果容器
        resultsContainer.style.display = 'block';
        
        // 显示执行摘要
        summaryElement.textContent = data.report.short_summary;
        
        // 显示详细报告（使用marked.js渲染Markdown）
        reportElement.innerHTML = marked.parse(data.report.markdown_report);
        
        // 显示后续问题
        questionsElement.innerHTML = '';
        data.report.follow_up_questions.forEach(question => {
            const li = document.createElement('li');
            li.textContent = question;
            questionsElement.appendChild(li);
        });
        
        // 显示验证结果
        if (data.verification.verified) {
            verificationElement.innerHTML = '<span class="verified">✓ 报告已验证</span>';
        } else {
            verificationElement.innerHTML = `<span class="not-verified">⚠ 验证问题</span><p>${data.verification.issues}</p>`;
        }
    }

    // 添加键盘快捷键
    queryInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && event.ctrlKey) {
            submitButton.click();
        }
    });

    // 添加示例查询
    const exampleQueries = [
        '分析苹果公司最近一个季度的表现',
        '评估特斯拉的财务状况和未来增长前景',
        '比较微软和谷歌的最新财务报告',
        '分析亚马逊在电子商务市场的竞争优势',
        '评估比特币作为投资资产的风险和回报'
    ];

    // 随机选择一个示例查询作为占位符
    queryInput.placeholder = exampleQueries[Math.floor(Math.random() * exampleQueries.length)];
});

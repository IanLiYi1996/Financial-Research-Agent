const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

// 读取配置文件
const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'config.local.json'), 'utf8'));

const app = express();
app.use(cors());
app.use(bodyParser.json());

// 主研究端点
app.post('/research', (req, res) => {
  const query = req.body.query;
  console.log(`收到查询: ${query}`);
  
  // 调用本地Python脚本执行研究流程
  exec(`python local_orchestrator.py "${query}"`, (error, stdout, stderr) => {
    if (error) {
      console.error(`执行错误: ${error}`);
      return res.status(500).json({ error: error.message });
    }
    
    if (stderr) {
      console.error(`标准错误: ${stderr}`);
    }
    
    try {
      const result = JSON.parse(stdout);
      res.json(result);
    } catch (e) {
      console.error(`解析JSON失败: ${e.message}`);
      res.status(500).json({ error: '解析结果失败', details: stdout });
    }
  });
});

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 提供静态文件
app.use(express.static(path.join(__dirname, 'frontend')));

const PORT = config.api.localPort || 3000;
app.listen(PORT, () => {
  console.log(`本地API服务器运行在 http://localhost:${PORT}`);
  console.log(`前端界面可访问: http://localhost:${PORT}`);
});

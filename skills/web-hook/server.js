/**
 * WebHook Server - HTTP 服务器实现
 * 接收外部 Webhook 事件并转发到 OpenClaw
 */

const http = require('http');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG_PATH = path.join(__dirname, 'config.yaml');
const STORE_PATH = path.join(__dirname, 'events.json');
const PORT = process.env.WEBHOOK_PORT || 3456;

// 内存存储（生产环境应使用数据库）
const eventStore = new Map();
const webhookConfigs = new Map();

/**
 * 加载配置文件
 */
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      const yaml = require('js-yaml');
      const config = yaml.load(fs.readFileSync(CONFIG_PATH, 'utf8'));
      if (config.webhooks) {
        Object.entries(config.webhooks).forEach(([name, cfg]) => {
          webhookConfigs.set(name, cfg);
        });
      }
    }
  } catch (err) {
    console.error('[WebHook] Failed to load config:', err.message);
  }
}

/**
 * 验证 HMAC 签名
 */
function verifySignature(payload, signature, secret, algorithm = 'sha256') {
  if (!signature || !secret) return false;
  
  const expected = crypto
    .createHmac(algorithm, secret)
    .update(payload)
    .digest('hex');
  
  // 支持多种签名格式
  const sigMethods = [
    signature,
    signature.replace(/^sha256=/, ''),
    signature.replace(/^SHA256=/, ''),
  ];
  
  // 使用 constant-time 比较，但先检查长度避免崩溃
  return sigMethods.some(sig => {
    try {
      const sigBuf = Buffer.from(sig);
      const expBuf = Buffer.from(expected);
      if (sigBuf.length !== expBuf.length) return false;
      return crypto.timingSafeEqual(expBuf, sigBuf);
    } catch (e) {
      return false;
    }
  });
}

/**
 * 检查事件是否已处理（幂等性）
 */
function isDuplicateEvent(eventId) {
  if (!eventId) return false;
  const exists = eventStore.has(eventId);
  if (exists) {
    console.log('[WebHook] Duplicate event ignored:', eventId);
  }
  return exists;
}

/**
 * 存储事件
 */
function storeEvent(eventId, event) {
  if (eventId) {
    eventStore.set(eventId, {
      ...event,
      receivedAt: Date.now(),
    });
    
    // 保留最近 1000 个事件
    if (eventStore.size > 1000) {
      const firstKey = eventStore.keys().next().value;
      eventStore.delete(firstKey);
    }
  }
}

/**
 * 发送通知到 OpenClaw
 */
function sendNotification(source, event) {
  const config = webhookConfigs.get(source);
  if (!config || !config.enabled) {
    console.log('[WebHook] Notifications disabled for:', source);
    return;
  }
  
  // 构建通知消息
  const eventType = event.event || event.action || 'unknown';
  const message = `🔔 **WebHook: ${source}**\n\n` +
    `事件：${eventType}\n` +
    `时间：${new Date(event.timestamp || Date.now()).toLocaleString('zh-CN')}\n` +
    `详情：${JSON.stringify(event, null, 2).slice(0, 500)}`;
  
  console.log('[WebHook] Sending notification:', message);
  
  // TODO: 集成 OpenClaw message/sessions_send API
  // 目前先记录到日志
}

/**
 * 处理 Webhook 请求
 */
function handleWebhook(req, res, source) {
  let body = '';
  
  req.on('data', chunk => {
    body += chunk.toString();
  });
  
  req.on('end', () => {
    const config = webhookConfigs.get(source);
    
    // 检查来源是否配置
    if (!config) {
      console.log('[WebHook] Unknown source:', source);
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Unknown webhook source' }));
      return;
    }
    
    // 验证签名
    const signatureHeader = config.signatureHeader || 'X-Signature';
    const signature = req.headers[signatureHeader.toLowerCase()];
    
    if (config.secret && !verifySignature(body, signature, config.secret)) {
      console.log('[WebHook] Signature verification failed for:', source);
      res.writeHead(401, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid signature' }));
      return;
    }
    
    // 解析事件
    let event;
    try {
      event = JSON.parse(body);
    } catch (err) {
      console.log('[WebHook] Invalid JSON:', err.message);
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid JSON' }));
      return;
    }
    
    // 检查重复事件
    const eventId = event.event_id || event.id || 
      crypto.createHash('sha256').update(body).digest('hex');
    
    if (isDuplicateEvent(eventId)) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'duplicate_ignored' }));
      return;
    }
    
    // 存储事件
    storeEvent(eventId, {
      source,
      event,
      headers: req.headers,
    });
    
    // 发送通知
    sendNotification(source, event);
    
    // 快速响应
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'received',
      event_id: eventId,
    }));
    
    console.log('[WebHook] Event received from', source, ':', eventId);
  });
}

/**
 * 创建 HTTP 服务器
 */
const server = http.createServer((req, res) => {
  // CORS 支持
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Signature, X-Hub-Signature-256');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }
  
  // 路由：/webhook/:source
  const match = req.url.match(/^\/webhook\/([a-zA-Z0-9_-]+)$/);
  if (match && req.method === 'POST') {
    const source = match[1];
    handleWebhook(req, res, source);
  } else if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'healthy',
      uptime: process.uptime(),
      events: eventStore.size,
    }));
  } else {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
  }
});

// 启动服务器
loadConfig();
server.listen(PORT, () => {
  console.log(`[WebHook] Server running on port ${PORT}`);
  console.log(`[WebHook] Endpoints: /webhook/:source`);
  console.log(`[WebHook] Health check: /health`);
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('[WebHook] Shutting down...');
  server.close(() => {
    console.log('[WebHook] Closed');
    process.exit(0);
  });
});

module.exports = { server, webhookConfigs };

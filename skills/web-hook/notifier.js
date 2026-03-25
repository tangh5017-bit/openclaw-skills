/**
 * WebHook Notifier - OpenClaw 通知输出集成
 * 将 webhook 事件转换为 OpenClaw 消息
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

class WebHookNotifier {
  constructor(options = {}) {
    this.workspace = options.workspace || process.env.OPENCLAW_WORKSPACE;
    this.channel = options.channel || 'heartbeat';
    this.template = options.template || this.defaultTemplate;
    this.aggregationWindow = options.aggregationWindow || 5 * 60 * 1000; // 5 分钟
    this.lastNotification = new Map();
  }

  /**
   * 默认通知模板
   */
  defaultTemplate(source, event) {
    const eventType = event.event?.action || event.event?.type || event.event?.object_kind || 'unknown';
    const timestamp = new Date(event.timestamp || Date.now()).toLocaleString('zh-CN');
    
    let details = '';
    const eventObj = event.event || event;
    
    // 提取关键信息
    if (eventObj.repository?.full_name) {
      details += `仓库：${eventObj.repository.full_name}\n`;
    }
    if (eventObj.ref) {
      details += `分支：${eventObj.ref}\n`;
    }
    if (eventObj.sender?.login) {
      details += `用户：${eventObj.sender.login}\n`;
    }
    if (eventObj.amount) {
      details += `金额：${eventObj.amount / 100} ${eventObj.currency || 'CNY'}\n`;
    }
    
    // 截断过长的详情
    const maxDetails = 500;
    const jsonPreview = JSON.stringify(eventObj, null, 2).slice(0, maxDetails);
    
    return `🔔 **WebHook 通知：${source}**\n\n` +
      `事件：${eventType}\n` +
      `时间：${timestamp}\n` +
      (details ? `${details}\n` : '') +
      `详情：\`\`\`json\n${jsonPreview}\n\`\`\``;
  }

  /**
   * 检查是否需要聚合（避免短时间内重复通知）
   */
  shouldNotify(source, eventType) {
    const key = `${source}:${eventType}`;
    const now = Date.now();
    const lastTime = this.lastNotification.get(key) || 0;
    
    if (now - lastTime < this.aggregationWindow) {
      console.log(`[Notifier] Aggregating notification for ${key}`);
      return false;
    }
    
    this.lastNotification.set(key, now);
    return true;
  }

  /**
   * 发送通知到 OpenClaw
   * 使用 sessions_send 或 message API
   */
  async notify(source, event) {
    const eventType = event.event?.action || event.event?.type || 'unknown';
    
    // 检查聚合
    if (!this.shouldNotify(source, eventType)) {
      return { status: 'aggregated' };
    }

    // 生成消息
    const message = this.template(source, event);
    
    console.log(`[Notifier] Sending notification for ${source}:${eventType}`);
    
    try {
      // 方法 1: 写入文件，由 OpenClaw 心跳读取
      await this.writeToMemory(source, event, message);
      
      // 方法 2: 调用 OpenClaw CLI (如果可用)
      // await this.sendViaCLI(message);
      
      return { status: 'sent', message };
    } catch (err) {
      console.error('[Notifier] Failed to send notification:', err.message);
      return { status: 'error', error: err.message };
    }
  }

  /**
   * 写入记忆文件（推荐方式）
   * OpenClaw 心跳时会读取并通知用户
   */
  async writeToMemory(source, event, message) {
    const today = new Date().toISOString().split('T')[0];
    const memoryPath = path.join(this.workspace, 'memory', `${today}.md`);
    
    const timestamp = new Date().toLocaleString('zh-CN');
    const entry = `\n### 🔔 WebHook 事件 (${timestamp})\n\n` +
      `来源：${source}\n` +
      `事件：${event.event?.action || event.event?.type || 'unknown'}\n` +
      `详情：${JSON.stringify(event.event, null, 2).slice(0, 300)}\n`;
    
    // 检查文件是否存在
    if (fs.existsSync(memoryPath)) {
      // 追加到文件末尾
      fs.appendFileSync(memoryPath, entry);
    } else {
      // 创建新文件
      const header = `# ${today} - WebHook 事件日志\n\n`;
      fs.writeFileSync(memoryPath, header + entry);
    }
    
    console.log(`[Notifier] Written to ${memoryPath}`);
  }

  /**
   * 通过 OpenClaw CLI 发送消息（备选方案）
   */
  async sendViaCLI(message) {
    try {
      // 使用 sessions_send 发送到当前会话
      await execAsync(`openclaw sessions send --message "${message.replace(/"/g, '\\"')}"`);
      console.log('[Notifier] Sent via CLI');
    } catch (err) {
      console.log('[Notifier] CLI not available, using file method');
      throw err;
    }
  }

  /**
   * 批量发送通知
   */
  async notifyBatch(events) {
    const results = [];
    for (const event of events) {
      const result = await this.notify(event.source, event);
      results.push(result);
    }
    return results;
  }
}

module.exports = { WebHookNotifier };

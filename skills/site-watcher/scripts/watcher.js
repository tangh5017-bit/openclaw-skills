#!/usr/bin/env node

/**
 * Site Watcher - 网站监控器
 * 
 * 监控网页变化，发送通知
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const CONFIG_PATH = path.join(__dirname, '..', 'config.yaml');
const DATA_PATH = path.join(__dirname, '..', 'data', 'snapshots.json');

// 简单的 YAML 解析器（避免依赖）
function parseYaml(content) {
  const result = { targets: [] };
  const lines = content.split('\n');
  let currentTarget = null;
  
  for (const line of lines) {
    if (line.trim().startsWith('#') || !line.trim()) continue;
    
    if (line.match(/^targets:/)) continue;
    
    const match = line.match(/^  - (\w+):(?: "([^"]*)")?$/);
    if (match) {
      if (currentTarget) result.targets.push(currentTarget);
      currentTarget = { [match[1]]: match[2] || '' };
    } else if (currentTarget && line.match(/^    \w+:/)) {
      const [key, value] = line.trim().split(/:\s*/);
      currentTarget[key] = value.replace(/"/g, '');
    }
  }
  
  if (currentTarget) result.targets.push(currentTarget);
  return result;
}

// 加载配置
function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    return { targets: [] };
  }
  const content = fs.readFileSync(CONFIG_PATH, 'utf-8');
  return parseYaml(content);
}

// 加载历史快照
function loadSnapshots() {
  if (!fs.existsSync(DATA_PATH)) {
    return {};
  }
  try {
    return JSON.parse(fs.readFileSync(DATA_PATH, 'utf-8'));
  } catch (e) {
    return {};
  }
}

// 保存快照
function saveSnapshots(snapshots) {
  fs.writeFileSync(DATA_PATH, JSON.stringify(snapshots, null, 2));
}

// 获取网页内容
async function fetchPage(url, selector = 'body') {
  try {
    // 使用 curl 获取页面
    const html = execSync(`curl -sL --max-time 30 "${url}"`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'ignore']
    });
    
    // 简单提取选择器内容（支持基本 CSS 选择器）
    if (selector === 'body' || selector === 'html') {
      return html;
    }
    
    // 尝试提取特定元素（简化版，不支持复杂选择器）
    const regex = new RegExp(`<[^>]*\\s*(?:id|class)=["']?${selector.replace(/[.#]/g, '')}["']?[^>]*>([\\s\\S]*?)</`, 'i');
    const match = html.match(regex);
    if (match) {
      return match[1].trim();
    }
    
    // 如果找不到，返回整个页面
    return html;
  } catch (error) {
    console.error(`获取页面失败 ${url}: ${error.message}`);
    return null;
  }
}

// 计算内容哈希
function hashContent(content) {
  return crypto.createHash('md5').update(content).digest('hex');
}

// 提取数值（用于价格等）
function extractValue(content) {
  // 尝试提取价格格式的数字
  const match = content.match(/[\d,]+\.?\d*/);
  if (match) {
    return parseFloat(match[0].replace(/,/g, ''));
  }
  return content;
}

// 检查条件
function checkCondition(value, condition) {
  if (condition === 'any' || !condition) {
    return true;
  }
  
  // 解析条件：value<100, value>50, contains="text"
  const ltMatch = condition.match(/value<(\d+)/);
  if (ltMatch && typeof value === 'number') {
    return value < parseFloat(ltMatch[1]);
  }
  
  const gtMatch = condition.match(/value>(\d+)/);
  if (gtMatch && typeof value === 'number') {
    return value > parseFloat(gtMatch[1]);
  }
  
  const containsMatch = condition.match(/contains="([^"]+)"/);
  if (containsMatch) {
    return String(value).includes(containsMatch[1]);
  }
  
  return false;
}

// 发送通知
function sendNotification(targetName, message) {
  console.log(`🔔 通知：${targetName}`);
  console.log(`   ${message}`);
  
  try {
    // 通过 OpenClaw 发送消息
    execSync(`openclaw message send --message "🔔 **网站监控提醒：${targetName}**\\n\\n${message}"`, {
      stdio: 'ignore'
    });
  } catch (e) {
    console.error('发送通知失败:', e.message);
  }
}

// 检查单个目标
async function checkTarget(target, snapshots) {
  const { name, url, selector, condition, notify } = target;
  
  console.log(`\n📍 检查：${name}`);
  console.log(`   URL: ${url}`);
  
  const content = await fetchPage(url, selector);
  if (!content) {
    console.log('   ❌ 获取失败');
    return;
  }
  
  const currentHash = hashContent(content);
  const previousHash = snapshots[name];
  
  if (!previousHash) {
    // 首次监控
    console.log('   ✅ 首次监控，记录初始状态');
    snapshots[name] = currentHash;
    return;
  }
  
  if (currentHash === previousHash) {
    console.log('   ✓ 无变化');
    return;
  }
  
  // 检测到变化
  console.log('   ⚠️  检测到变化!');
  
  // 检查条件
  const value = extractValue(content);
  if (!checkCondition(value, condition)) {
    console.log('   └─ 不满足触发条件，忽略');
    return;
  }
  
  // 发送通知
  const message = `检测到变化！\nURL: ${url}\n当前值：${value}`;
  sendNotification(name, message);
  
  // 更新快照
  snapshots[name] = currentHash;
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  const config = loadConfig();
  const snapshots = loadSnapshots();
  
  switch (command) {
    case 'add': {
      // 添加监控目标：add "name" "url" --selector ".price"
      const name = args[1];
      const url = args[2];
      
      if (!name || !url) {
        console.log('用法：node watcher.js add <name> <url> [--selector <selector>] [--interval <min>] [--condition <cond>]');
        process.exit(1);
      }
      
      const target = {
        name,
        url,
        selector: 'body',
        interval: 60,
        condition: 'any',
        notify: 'heartbeat',
        enabled: true
      };
      
      // 解析选项
      for (let i = 3; i < args.length; i += 2) {
        if (args[i] === '--selector') target.selector = args[i + 1];
        if (args[i] === '--interval') target.interval = parseInt(args[i + 1]);
        if (args[i] === '--condition') target.condition = args[i + 1];
        if (args[i] === '--notify') target.notify = args[i + 1];
      }
      
      config.targets.push(target);
      
      // 保存配置（简化：追加到文件）
      const yamlContent = `\n  - name: "${target.name}"\n    url: "${target.url}"\n    selector: "${target.selector}"\n    interval: ${target.interval}\n    condition: "${target.condition}"\n    notify: "${target.notify}"\n    enabled: true\n`;
      
      if (!fs.existsSync(CONFIG_PATH)) {
        fs.writeFileSync(CONFIG_PATH, 'targets:\n' + yamlContent);
      } else {
        fs.appendFileSync(CONFIG_PATH, yamlContent);
      }
      
      console.log(`✅ 已添加监控目标：${name}`);
      console.log(`   URL: ${url}`);
      console.log(`   选择器：${target.selector}`);
      console.log(`   间隔：${target.interval} 分钟`);
      break;
    }
    
    case 'list': {
      console.log('📋 监控目标列表:\n');
      if (config.targets.length === 0) {
        console.log('   (空)');
      } else {
        for (const target of config.targets) {
          const status = target.enabled ? '✅' : '⏸️';
          console.log(`${status} ${target.name}`);
          console.log(`   URL: ${target.url}`);
          console.log(`   选择器：${target.selector || 'body'}`);
          console.log(`   间隔：${target.interval} 分钟`);
          console.log(`   条件：${target.condition || 'any'}`);
          console.log();
        }
      }
      break;
    }
    
    case 'check': {
      const name = args[1];
      const target = config.targets.find(t => t.name === name);
      
      if (!target) {
        console.log(`❌ 未找到监控目标：${name}`);
        process.exit(1);
      }
      
      await checkTarget(target, snapshots);
      saveSnapshots(snapshots);
      break;
    }
    
    case 'remove': {
      const name = args[1];
      const index = config.targets.findIndex(t => t.name === name);
      
      if (index === -1) {
        console.log(`❌ 未找到监控目标：${name}`);
        process.exit(1);
      }
      
      config.targets.splice(index, 1);
      delete snapshots[name];
      
      // 重写配置文件
      let yamlContent = 'targets:\n';
      for (const target of config.targets) {
        yamlContent += `  - name: "${target.name}"\n`;
        yamlContent += `    url: "${target.url}"\n`;
        yamlContent += `    selector: "${target.selector}"\n`;
        yamlContent += `    interval: ${target.interval}\n`;
        yamlContent += `    condition: "${target.condition}"\n`;
        yamlContent += `    notify: "${target.notify}"\n`;
        yamlContent += `    enabled: ${target.enabled}\n`;
      }
      
      fs.writeFileSync(CONFIG_PATH, yamlContent);
      saveSnapshots(snapshots);
      
      console.log(`✅ 已删除监控目标：${name}`);
      break;
    }
    
    case 'run': {
      // 运行所有监控
      if (args.includes('--all')) {
        console.log('🚀 运行所有监控任务...\n');
        
        for (const target of config.targets) {
          if (!target.enabled) continue;
          await checkTarget(target, snapshots);
        }
        
        saveSnapshots(snapshots);
        console.log('\n✅ 所有监控任务完成');
      }
      break;
    }
    
    default:
      console.log('Site Watcher - 网站监控器');
      console.log('\n用法:');
      console.log('  node watcher.js add <name> <url> [options]  - 添加监控');
      console.log('  node watcher.js list                        - 列出监控');
      console.log('  node watcher.js check <name>                - 手动检查');
      console.log('  node watcher.js remove <name>               - 删除监控');
      console.log('  node watcher.js run --all                   - 运行所有监控');
      console.log('\n选项:');
      console.log('  --selector <css>   CSS 选择器（默认：body）');
      console.log('  --interval <min>   检查间隔（默认：60）');
      console.log('  --condition <cond> 触发条件（默认：any）');
      console.log('  --notify <channel> 通知渠道（默认：heartbeat）');
      break;
  }
}

main().catch(console.error);

/**
 * WebHook Router - 事件路由和过滤
 * 根据事件类型和来源路由到不同的处理器
 */

const EventEmitter = require('events');

class WebHookRouter extends EventEmitter {
  constructor() {
    super();
    this.routes = new Map();
    this.filters = new Map();
  }

  /**
   * 注册路由处理器
   * @param {string} source - 来源 (github, stripe, etc.)
   * @param {string} eventType - 事件类型 (push, payment, etc.)
   * @param {Function} handler - 处理函数
   */
  register(source, eventType, handler) {
    const key = `${source}:${eventType}`;
    this.routes.set(key, handler);
    console.log(`[Router] Registered handler for ${key}`);
  }

  /**
   * 注册事件过滤器
   * @param {string} source - 来源
   * @param {Function} filter - 过滤函数 (返回 true 表示通过)
   */
  addFilter(source, filter) {
    if (!this.filters.has(source)) {
      this.filters.set(source, []);
    }
    this.filters.get(source).push(filter);
  }

  /**
   * 路由事件
   * @param {string} source - 来源
   * @param {Object} event - 事件对象
   * @returns {Promise<boolean>} - 是否成功处理
   */
  async route(source, event) {
    console.log(`[Router] Routing event from ${source}`);

    // 应用过滤器
    const filters = this.filters.get(source) || [];
    for (const filter of filters) {
      if (!filter(event)) {
        console.log(`[Router] Event filtered out for ${source}`);
        return false;
      }
    }

    // 获取事件类型
    const eventType = this.getEventType(source, event);
    if (!eventType) {
      console.log(`[Router] Unknown event type for ${source}`);
      return false;
    }

    // 查找处理器
    const handlerKey = `${source}:${eventType}`;
    const handler = this.routes.get(handlerKey);

    if (!handler) {
      // 尝试通用处理器
      const genericHandler = this.routes.get(`${source}:*`);
      if (genericHandler) {
        console.log(`[Router] Using generic handler for ${source}`);
        return await genericHandler(event);
      }
      console.log(`[Router] No handler found for ${handlerKey}`);
      return false;
    }

    // 执行处理器
    try {
      await handler(event);
      console.log(`[Router] Event handled successfully: ${handlerKey}`);
      return true;
    } catch (err) {
      console.error(`[Router] Handler error for ${handlerKey}:`, err.message);
      return false;
    }
  }

  /**
   * 获取事件类型
   * @param {string} source - 来源
   * @param {Object} event - 事件对象
   * @returns {string|null}
   */
  getEventType(source, event) {
    // 不同来源的事件类型字段不同
    const typeFields = {
      github: ['action', 'ref'],
      gitlab: ['object_kind', 'event_name'],
      stripe: ['type'],
      custom: ['event', 'action', 'type'],
    };

    const fields = typeFields[source] || typeFields.custom;
    for (const field of fields) {
      if (event[field]) {
        return event[field];
      }
    }

    return null;
  }

  /**
   * 清除所有路由
   */
  clear() {
    this.routes.clear();
    this.filters.clear();
  }
}

// 预定义的过滤器

/**
 * GitHub: 只处理特定分支的 push 事件
 */
function githubBranchFilter(branch) {
  return (event) => {
    if (event.ref) {
      return event.ref === `refs/heads/${branch}`;
    }
    return true;
  };
}

/**
 * Stripe: 只处理特定类型的事件
 */
function stripeEventTypeFilter(types) {
  return (event) => {
    return types.includes(event.type);
  };
}

/**
 * 通用：只处理包含特定字段的事件
 */
function fieldExistsFilter(field) {
  return (event) => {
    return event[field] !== undefined;
  };
}

module.exports = {
  WebHookRouter,
  githubBranchFilter,
  stripeEventTypeFilter,
  fieldExistsFilter,
};

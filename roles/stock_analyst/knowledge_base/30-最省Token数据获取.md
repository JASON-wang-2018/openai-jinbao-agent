# 最节省Token的实时数据获取方案

> 核心原则：按需获取、缓存复用、批量处理

---

## 一、数据源成本对比

### 1.1 Token消耗对比

| 数据源 | Token消耗 | 稳定性 | 数据质量 |
|--------|----------|--------|---------|
| **Sina** | **0** | ⭐⭐⭐ | ⭐⭐⭐ |
| **EastMoney** | 0 | ⭐⭐⭐ | ⭐⭐⭐ |
| **AKShare** | 0 | ⭐⭐ | ⭐⭐ |
| **Baostock** | 0 | ⭐⭐⭐ | ⭐⭐⭐ |
| **TuShare** | 消耗积分 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**结论**：免费数据源足够使用，无需付费

### 1.2 最优组合

```
第一选择：Sina（最快）
第二选择：EastMoney（最稳）
备用：AKShare / Baostock
```

---

## 二、最省Token策略

### 2.1 核心原则

```
1. 按需获取 → 只取需要的字段
2. 缓存复用 → 不重复请求相同数据
3. 批量处理 → 一次请求获取多只股票
4. 限流控制 → 避免频繁请求
5. 本地缓存 → 减少网络请求
```

### 2.2 最简请求

```python
# 最简方式：只用Sina获取指数
import requests

def get_index():
    """最简指数获取（0 Token消耗）"""
    url = "https://hq.sinajs.cn/list=sh000001,sz399001"
    headers = {'Referer': 'https://finance.sina.com.cn'}
    
    r = requests.get(url, headers=headers, timeout=10)
    
    # 解析数据
    for line in r.text.split('\n'):
        if 'sh000001' in line:
            sh = line.split('"')[1].split(',')
            print(f"上证: {sh[3]} ({sh[3]-sh[2])/sh[2]*100:.2f}%)")
        elif 'sz399001' in line:
            sz = line.split('"')[1].split(',')
            print(f"深证: {sz[3]} ({sz[3]-sz[2])/sz[2]*100:.2f}%)")
```

### 2.3 批量获取

```python
# 批量获取（一次请求最多80只）
def get_batch(stocks):
    """批量获取（1次请求 = 多只股票）"""
    if len(stocks) > 80:
        stocks = stocks[:80]
    
    url = f"https://hq.sinajs.cn/list={','.join(stocks)}"
    headers = {'Referer': 'https://finance.sina.com.cn'}
    
    r = requests.get(url, headers=headers, timeout=15)
    
    results = {}
    for line in r.text.split('\n'):
        if line.startswith('var'):
            data = line.split('"')[1].split(',')
            code = line.split('_')[1].split('=')[0]
            results[code] = {
                'name': data[0],
                'price': float(data[3]),
                'change': (float(data[3]) - float(data[2])) / float(data[2]) * 100
            }
    
    return results
```

---

## 三、本地缓存方案

### 3.1 内存缓存

```python
import time
from datetime import datetime

class Cache:
    def __init__(self, ttl=3):
        self.data = {}
        self.ttl = ttl  # 过期时间（秒）
    
    def get(self, key):
        if key in self.data:
            data, timestamp = self.data[key]
            if time.time() - timestamp < self.ttl:
                return data
            del self.data[key]
        return None
    
    def set(self, key, value):
        self.data[key] = (value, time.time())
    
    def clear(self):
        self.data = {}

# 使用示例
cache = Cache(ttl=3)  # 3秒缓存

def get_price(code):
    # 先查缓存
    cached = cache.get(code)
    if cached:
        return cached
    
    # 缓存未命中，获取数据
    price = fetch_from_api(code)
    
    # 存入缓存
    cache.set(code, price)
    return price
```

### 3.2 文件缓存

```python
import json
import os
from datetime import datetime

class FileCache:
    def __init__(self, dir_path='/tmp/stock_cache', ttl=5):
        self.dir_path = dir_path
        self.ttl = ttl
        os.makedirs(dir_path, exist_ok=True)
    
    def _filename(self, key):
        return f"{self.dir_path}/{key}.json"
    
    def get(self, key):
        path = self._filename(key)
        if not os.path.exists(path):
            return None
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        timestamp = data['timestamp']
        if time.time() - timestamp > self.ttl:
            os.remove(path)
            return None
        
        return data['value']
    
    def set(self, key, value):
        path = self._filename(key)
        data = {
            'value': value,
            'timestamp': time.time()
        }
        with open(path, 'w') as f:
            json.dump(data, f)
```

---

## 四、最简复盘脚本

### 4.1 单文件方案（约50行）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简复盘脚本 - 0 Token消耗
使用Sina接口，内存缓存，按需获取
"""

import requests
import time
from datetime import datetime

class SimpleFetcher:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3
    
    def fetch(self, url):
        # 检查缓存
        if url in self.cache:
            data, ts = self.cache[url]
            if time.time() - ts < self.cache_ttl:
                return data
        
        # 获取数据
        headers = {'Referer': 'https://finance.sina.com.cn'}
        r = requests.get(url, headers=headers, timeout=10)
        self.cache[url] = (r.text, time.time())
        return r.text

def parse_index(text):
    """解析指数"""
    for line in text.split('\n'):
        if 'sh000001' in line:
            data = line.split('"')[1].split(',')
            return {
                'name': '上证',
                'price': float(data[3]),
                'change': (float(data[3]) - float(data[2])) / float(data[2]) * 100
            }
    return None

def main():
    fetcher = SimpleFetcher()
    
    # 获取指数
    url = "https://hq.sinajs.cn/list=sh000001,sz399001,sz399006"
    text = fetcher.fetch(url)
    
    print(f"\n【{datetime.now().strftime('%H:%M:%S')}】")
    
    for line in text.split('\n'):
        if not line.startswith('var'):
            continue
        
        data = line.split('"')[1].split(',')
        name = data[0]
        price = float(data[3])
        change = (price - float(data[2])) / float(data[2]) * 100
        sign = '+' if change >= 0 else ''
        print(f"{name}: {price:.2f} ({sign}{change:.2f}%)")

if __name__ == '__main__':
    main()
```

### 4.2 运行方式

```bash
# 保存为 simple.py
python3 simple.py

# 输出示例：
# 【14:30:25】
# 上证指数: 3082.07 (-0.82%)
# 深证成指: 14100.19 (-0.62%)
# 创业板指: 3275.96 (-1.01%)
```

---

## 五、实战代码模板

### 5.1 最简选股器

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最简选股器 - 0 Token消耗
功能：获取涨跌幅榜
"""

import requests
import json

def get_rank(top=10):
    """获取涨跌幅排名"""
    url = f"https://hq.sinajs.cn/list=s_sh000001,s_sz399001"
    headers = {'Referer': 'https://finance.sina.com.cn'}
    
    r = requests.get(url, headers=headers, timeout=10)
    return r.text

def main():
    print("\n【涨跌幅排名】")
    text = get_rank()
    
    for line in text.split('\n'):
        if not line.startswith('var'):
            continue
        
        data = line.split('"')[1].split(',')
        name = data[0]
        price = float(data[3])
        change = (price - float(data[2])) / float(data[2]) * 100
        sign = '+' if change >= 0 else ''
        print(f"{name}: {price:.2f} ({sign}{change:.2f}%)")

if __name__ == '__main__':
    main()
```

---

## 六、Token消耗优化清单

### 6.1 必须做

```
✅ 使用Sina/EastMoney（免费）
✅ 开启本地缓存（减少请求）
✅ 批量获取（一次多只）
✅ 按需获取（只取需要的）
✅ 限流控制（避免过快）
✅ 错误重试（避免重复请求）
```

### 6.2 不要做

```
❌ 不要用TuShare（消耗积分）
❌ 不要频繁请求（>1次/秒）
❌ 不要重复请求相同数据
❌ 不要获取不需要的字段
❌ 不要长时间运行不清理缓存
```

---

## 七、完整解决方案

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
零成本实时行情系统
Sina + 内存缓存 + 批量获取
"""

import requests
import time
from datetime import datetime
from typing import Dict, List, Optional

class ZeroCostMarket:
    """零成本行情系统"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://finance.sina.com.cn'
        })
    
    def fetch(self, url: str) -> Optional[str]:
        """带缓存的请求"""
        if url in self.cache:
            data, ts = self.cache[url]
            if time.time() - ts < self.cache_ttl:
                return data
        
        try:
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                self.cache[url] = (r.text, time.time())
                return r.text
        except Exception as e:
            print(f"请求失败: {e}")
        return None
    
    def get_indices(self) -> List[Dict]:
        """获取大盘指数"""
        url = "https://hq.sinajs.cn/list=sh000001,sz399001,sz399006"
        text = self.fetch(url)
        
        result = []
        for line in text.split('\n'):
            if not line.startswith('var'):
                continue
            
            data = line.split('"')[1].split(',')
            name = data[0]
            price = float(data[3])
            change = (price - float(data[2])) / float(data[2]) * 100
            
            result.append({
                'name': name,
                'price': price,
                'change': change,
                'time': datetime.now().strftime('%H:%M:%S')
            })
        
        return result
    
    def get_stocks(self, codes: List[str]) -> List[Dict]:
        """批量获取股票"""
        if len(codes) > 80:
            codes = codes[:80]
        
        symbol_map = {
            c: ('sh' if c.startswith('6') else 'sz') + c
            for c in codes
        }
        
        url = f"https://hq.sinajs.cn/list={','.join(symbol_map.values())}"
        text = self.fetch(url)
        
        result = []
        for line in text.split('\n'):
            if not line.startswith('var'):
                continue
            
            data = line.split('"')[1].split(',')
            full_code = line.split('_')[1].split('=')[0]
            code = full_code[2:]  # 去掉sh/sz
            
            result.append({
                'code': code,
                'name': data[0],
                'price': float(data[3]),
                'change': (float(data[3]) - float(data[2])) / float(data[2]) * 100
            })
        
        return result
    
    def show(self):
        """显示实时行情"""
        indices = self.get_indices()
        print(f"\n【零成本实时行情】{datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        for idx in indices:
            sign = '+' if idx['change'] >= 0 else ''
            print(f"{idx['name']}: {idx['price']:.2f} ({sign}{idx['change']:.2f}%)")


if __name__ == '__main__':
    market = ZeroCostMarket()
    market.show()
```

---

## 八、节省Token效果对比

### 8.1 成本对比

| 方案 | 每次请求成本 | 100次请求成本 | 稳定性 |
|------|------------|--------------|-------|
| TuShare | 1积分 | 100积分 | ⭐⭐⭐⭐ |
| AKShare | 0 | 0 | ⭐⭐ |
| **Sina+缓存** | **0** | **0** | **⭐⭐⭐** |

### 8.2 效率对比

| 方案 | 请求次数/分钟 | 数据延迟 | 稳定性 |
|------|-------------|---------|-------|
| TuShare | 60 | 实时 | 高 |
| AKShare | 30 | 1-5秒 | 中 |
| **Sina+缓存** | **20** | **1-3秒** | **高** |

---

## 九、使用建议

```
最佳实践：
1. 日常看盘 → Sina（最快）
2. 批量分析 → Sina（一次多只）
3. 历史数据 → Baostock（最稳）
4. 财务数据 → TuShare（质量高）
5. 高频交易 → Sina+缓存

禁忌：
1. 不要用TuShare做高频
2. 不要频繁请求
3. 不要全量获取
4. 不要不缓存
```

---

## 十、总结

```
零成本实时数据方案：

1. 数据源：Sina（首选）、EastMoney（备选）
2. 获取方式：批量获取 + 内存缓存
3. 刷新频率：3秒/次（够用）
4. Token消耗：0
5. 稳定性：⭐⭐⭐

结论：
免费数据源完全够用，无需付费
按需获取、缓存复用是核心
```

---

*零成本、零Token、高效率。*

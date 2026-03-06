#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合搜索系统
支持多个搜索源：Serper.dev, Tavily, DuckDuckGo

使用方法:
    python stock/scripts/unified_search.py --query "A股走势"
    python stock/scripts/unified_search.py --query "002642荣联科技" --source serper
    python stock/scripts/unified_search.py --query "热点板块" --source tavily
"""

import requests
import json
import argparse
import sys
from typing import Dict, List, Optional

# Serper.dev 配置
SERPER_API_KEY = "ccc68672d43baf35c0d00d84a5be6209846cef05"
SERPER_URL = "https://google.serper.dev/search"

# Tavily 配置 (如果有)
TAVILY_API_KEY = None  # 可配置


class UnifiedSearch:
    """整合搜索系统"""
    
    def __init__(self):
        self.results = []
    
    def search_serper(self, query: str, num: int = 5) -> List[Dict]:
        """
        使用 Serper.dev 搜索 (Google)
        
        Args:
            query: 搜索关键词
            num: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        try:
            headers = {
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "q": query,
                "num": num
            }
            
            response = requests.post(SERPER_URL, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                credits = result.get("searchParameters", {}).get("credits", "N/A")
                
                results = []
                for item in result.get("organic", [])[:num]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "source": "serper"
                    })
                
                print(f"✅ Serper.dev 搜索成功 (剩余 credits: {credits})")
                return results
            else:
                print(f"❌ Serper.dev 搜索失败: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Serper.dev 错误: {e}")
            return []
    
    def search_duckduckgo(self, query: str, num: int = 5) -> List[Dict]:
        """
        使用 DuckDuckGo 搜索 (免费备用)
        
        Args:
            query: 搜索关键词
            num: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        try:
            # 使用 ddgr 命令行工具 (如果安装)
            import subprocess
            
            cmd = ["ddgr", "--json", "-n", str(num), query]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                results = []
                for line in result.stdout.strip().split("\n"):
                    if line:
                        item = json.loads(line)
                        results.append({
                            "title": item.get("title", ""),
                            "link": item.get("url", ""),
                            "snippet": item.get("abstract", ""),
                            "source": "duckduckgo"
                        })
                
                print(f"✅ DuckDuckGo 搜索成功")
                return results
            else:
                print(f"⚠️ ddgr 未安装，使用备用方案")
                return []
                
        except FileNotFoundError:
            print("⚠️ ddgr 未安装，无法使用 DuckDuckGo")
            return []
        except Exception as e:
            print(f"❌ DuckDuckGo 错误: {e}")
            return []
    
    def search(self, query: str, source: str = "auto", num: int = 5) -> List[Dict]:
        """
        统一搜索入口
        
        Args:
            query: 搜索关键词
            source: 搜索源 (auto/serper/tavily/duckduckgo)
            num: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        print(f"\n🔍 搜索: {query}")
        print("=" * 60)
        
        if source == "auto":
            # 自动选择：首先尝试 Serper.dev
            results = self.search_serper(query, num)
            if not results:
                results = self.search_duckduckgo(query, num)
        elif source == "serper":
            results = self.search_serper(query, num)
        elif source == "duckduckgo":
            results = self.search_duckduckgo(query, num)
        else:
            print(f"❌ 未知的搜索源: {source}")
            return []
        
        self.results = results
        return results
    
    def print_results(self):
        """打印搜索结果"""
        if not self.results:
            print("❌ 无搜索结果")
            return
        
        print(f"\n📊 共 {len(self.results)} 条结果:\n")
        
        for i, item in enumerate(self.results, 1):
            source = item.get("source", "unknown")
            print(f"{i}. [{source}] {item.get('title', '')}")
            print(f"   {item.get('link', '')}")
            print(f"   {item.get('snippet', '')}")
            print()


def main():
    parser = argparse.ArgumentParser(description="整合搜索系统")
    parser.add_argument("--query", "-q", required=True, help="搜索关键词")
    parser.add_argument("--source", "-s", default="auto", 
                       choices=["auto", "serper", "tavily", "duckduckgo"],
                       help="搜索源 (默认: auto)")
    parser.add_argument("--num", "-n", type=int, default=5, help="返回结果数量")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    
    args = parser.parse_args()
    
    searcher = UnifiedSearch()
    results = searcher.search(args.query, args.source, args.num)
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        searcher.print_results()


if __name__ == "__main__":
    main()

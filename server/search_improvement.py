# === AgenticSeek Search Improvement Module ===
# このモジュールは、Playwright でのブラウザ要素検出を強化します
# api.py に統合して使用

import asyncio
from playwright.async_api import Page, Browser
from typing import Dict, Any, Optional, List
import re

async def find_and_interact_with_search(page: Page, search_query: str, task_description: str = "") -> Dict[str, Any]:
    """
    Google や他のサイトで検索フィールドを見つけて、クエリを入力し実行
    複数の検出方法をトライしてロバスト性を向上
    """
    result = {
        "status": "pending",
        "task": "search",
        "query": search_query,
        "description": task_description,
        "methods_tried": [],
        "errors": [],
        "success": False
    }
    
    try:
        search_methods = [
            {
                "name": "Google standard input (name=q)",
                "input_selector": "input[name='q']",
                "button_selector": "button[name='btnK']",
                "enter_key": True
            },
            {
                "name": "Google form submit (textarea)",
                "input_selector": "textarea[name='q']",
                "button_selector": None,
                "enter_key": True
            },
            {
                "name": "Generic search input",
                "input_selector": "input[type='search']",
                "button_selector": "button[type='submit']",
                "enter_key": False
            },
            {
                "name": "Input with search placeholder",
                "input_selector": "input[placeholder*='search']",
                "button_selector": None,
                "enter_key": True
            },
            {
                "name": "Any input field (fallback)",
                "input_selector": "input[type='text']",
                "button_selector": None,
                "enter_key": True
            }
        ]
        
        for method in search_methods:
            result["methods_tried"].append(method["name"])
            
            try:
                input_selector = method["input_selector"]
                
                # 入力要素にフォーカス
                try:
                    await page.focus(input_selector)
                except Exception as e:
                    continue
                
                # テキストを入力
                await page.fill(input_selector, search_query)
                
                # 検索を実行
                if method["enter_key"]:
                    await page.press(input_selector, "Enter")
                else:
                    button_selector = method["button_selector"]
                    if button_selector:
                        await page.click(button_selector)
                    else:
                        await page.press(input_selector, "Enter")
                
                # 検索結果をロード待機
                try:
                    await page.wait_for_navigation(timeout=10000)
                except:
                    pass
                
                result["status"] = "success"
                result["success"] = True
                result["method_used"] = method["name"]
                return result
                
            except Exception as e:
                result["errors"].append(str(e))
                continue
        
        result["status"] = "failed"
        result["success"] = False
        result["error"] = "All search methods failed"
        
    except Exception as e:
        result["status"] = "error"
        result["success"] = False
        result["error"] = str(e)
    
    return result


# この関数をapi.pyのexecute_agent_task内から呼び出す
# 例：
# if "search for" in task.lower():
#     search_result = await find_and_interact_with_search(page, query)
#     if search_result["success"]:
#         return search_result

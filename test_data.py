from datetime import datetime, date, timedelta
import json
import os
from models import Task
import sheets_utils

def create_test_data():
    """創建並保存測試數據"""
    # 確保任務列表為空
    if os.path.exists(sheets_utils.TASKS_FILE):
        os.remove(sheets_utils.TASKS_FILE)
    
    # 創建測試任務
    tasks = []
    
    # 獲取今天的日期
    today = date.today()
    
    # 項目A - 網站開發
    tasks.append(Task(
        sub_task="設計網站首頁",
        main_task="網站開發",
        priority="高",
        status="已完成",
        start_date=today - timedelta(days=30),
        end_date=today - timedelta(days=20),
        responsible="張小明",
        notes="已完成設計並獲得批准",
        status_update_time=datetime.now() - timedelta(days=19),
    ))
    
    tasks.append(Task(
        sub_task="後端API開發",
        main_task="網站開發",
        priority="高",
        status="進行中",
        start_date=today - timedelta(days=25),
        end_date=today + timedelta(days=5),
        responsible="李大偉",
        notes="正在進行用戶認證功能開發",
        status_update_time=datetime.now() - timedelta(days=2),
    ))
    
    tasks.append(Task(
        sub_task="移動端適配",
        main_task="網站開發",
        priority="中",
        status="未開始",
        start_date=today + timedelta(days=2),
        end_date=today + timedelta(days=15),
        responsible="王小紅",
        notes="等待設計團隊提供移動端設計稿",
    ))
    
    # 項目B - 市場營銷
    tasks.append(Task(
        sub_task="社交媒體宣傳計劃",
        main_task="市場營銷",
        priority="中",
        status="進行中",
        start_date=today - timedelta(days=10),
        end_date=today + timedelta(days=20),
        responsible="陳美玲",
        notes="正在制定Facebook和Instagram的營銷策略",
        status_update_time=datetime.now() - timedelta(days=5),
    ))
    
    tasks.append(Task(
        sub_task="內容創作",
        main_task="市場營銷",
        priority="中",
        status="進行中",
        start_date=today - timedelta(days=15),
        end_date=today + timedelta(days=30),
        responsible="陳美玲",
        notes="正在撰寫博客文章和社交媒體內容",
        status_update_time=datetime.now() - timedelta(days=3),
    ))
    
    # 項目C - 系統維護
    tasks.append(Task(
        sub_task="數據庫備份",
        main_task="系統維護",
        priority="高",
        status="已完成",
        start_date=today - timedelta(days=5),
        end_date=today - timedelta(days=5),
        responsible="李大偉",
        notes="已完成每週例行備份",
        status_update_time=datetime.now() - timedelta(days=5),
    ))
    
    tasks.append(Task(
        sub_task="系統安全更新",
        main_task="系統維護",
        priority="高",
        status="未開始",
        start_date=today + timedelta(days=1),
        end_date=today + timedelta(days=2),
        responsible="李大偉",
        notes="安排在週末進行安全補丁更新",
    ))
    
    # 項目D - 研究
    tasks.append(Task(
        sub_task="市場調研",
        main_task="研究",
        priority="低",
        status="已完成",
        start_date=today - timedelta(days=60),
        end_date=today - timedelta(days=30),
        responsible="王小紅",
        notes="已完成競爭對手分析報告",
        status_update_time=datetime.now() - timedelta(days=30),
    ))
    
    tasks.append(Task(
        sub_task="新技術評估",
        main_task="研究",
        priority="低",
        status="暫停",
        start_date=today - timedelta(days=20),
        end_date=today + timedelta(days=40),
        responsible="張小明",
        notes="評估人工智能在產品中的應用，因資源限制暫時擱置",
        status_update_time=datetime.now() - timedelta(days=10),
    ))
    
    # 項目E - 客戶支持
    tasks.append(Task(
        sub_task="更新幫助文檔",
        main_task="客戶支持",
        priority="中",
        status="未開始",
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=25),
        responsible="陳美玲",
        notes="需要對用戶手冊進行更新，反映新功能",
    ))
    
    # 保存測試數據
    sheets_utils.save_tasks(tasks)
    
    # 更新系統參數
    parameters = {
        'status': ['未開始', '進行中', '已完成', '暫停'],
        'priority': ['低', '中', '高', '緊急'],
        'responsible': ['張小明', '李大偉', '王小紅', '陳美玲'],
        'main_task': ['網站開發', '市場營銷', '系統維護', '研究', '客戶支持']
    }
    
    sheets_utils.save_parameters(parameters)
    
    print(f"已創建 {len(tasks)} 條測試任務")
    return tasks

if __name__ == "__main__":
    create_test_data()
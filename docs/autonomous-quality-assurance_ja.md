# Autonomous Quality Assurance - 自律品質保証

Refinireの第二の柱である自律品質保証は、AIエージェントの出力品質を自動的に評価し、必要に応じて再生成を行う革新的なシステムです。

## 基本概念

従来の手動品質管理から脱却し、AIが自らの出力を評価・改善する自律的な品質保証メカニズムを提供します。

```python
from refinire import create_evaluated_gen_agent, Context
import asyncio

# 品質評価付きエージェント
agent = create_evaluated_gen_agent(
    name="quality_assistant",
    generation_instructions="役立つ回答を生成してください",
    evaluation_instructions="正確性と有用性を評価してください",
    threshold=85.0,  # 85点以上を要求
    model="gpt-4o-mini"
)

# 自動品質管理
result = asyncio.run(agent.run("量子コンピューティングを説明して", Context()))
```

## 簡単な事例

### 1. 基本的な品質評価

```python
from refinire import create_evaluated_gen_agent, Context

# 品質しきい値を設定したエージェント
agent = create_evaluated_gen_agent(
    name="qa_agent",
    generation_instructions="詳細で正確な回答をしてください",
    evaluation_instructions="回答の正確性を1-100で評価",
    threshold=80.0,
    model="gpt-4o-mini"
)

# 自動評価付き実行
result = agent.run_sync("地球温暖化について説明してください", Context())
print(f"回答: {result.shared_state['qa_agent_result']}")
```

### 2. 品質基準のカスタマイズ

```python
# より厳しい評価基準
strict_agent = create_evaluated_gen_agent(
    name="strict_agent",
    generation_instructions="科学的に正確で詳細な回答をしてください",
    evaluation_instructions="""
    以下の基準で評価してください:
    - 科学的正確性 (30点)
    - 詳細度 (25点)  
    - 理解しやすさ (25点)
    - 完全性 (20点)
    合計100点満点で評価
    """,
    threshold=90.0,  # 90点以上要求
    max_retries=3,   # 最大3回再試行
    model="gpt-4o"
)
```

## 中級事例

### 3. ドメイン特化品質評価

```python
class MedicalQAAgent:
    """医療情報専用の品質保証エージェント"""
    
    def __init__(self):
        self.agent = create_evaluated_gen_agent(
            name="medical_qa",
            generation_instructions="""
            医療情報について正確で責任ある回答をしてください。
            必ず以下を含めてください:
            1. 科学的根拠
            2. 適用範囲と制限
            3. 専門医への相談推奨
            """,
            evaluation_instructions="""
            医療情報の品質を以下で評価:
            - 医学的正確性 (40点)
            - 安全性への配慮 (30点)
            - 専門医相談の推奨 (20点)
            - 情報の完全性 (10点)
            """,
            threshold=95.0,  # 医療情報は高い基準
            max_retries=5,
            model="gpt-4o"
        )
    
    def get_medical_info(self, question: str) -> str:
        result = self.agent.run_sync(question, Context())
        return result.shared_state["medical_qa_result"]

# 使用例
medical_agent = MedicalQAAgent()
response = medical_agent.get_medical_info("高血圧の治療法について教えてください")
```

### 4. 多層品質評価システム

```python
class MultiLayerQualitySystem:
    """多層構造の品質評価システム"""
    
    def __init__(self):
        # 基本品質チェック
        self.basic_agent = create_evaluated_gen_agent(
            name="basic_check",
            generation_instructions="基本的な回答をしてください",
            evaluation_instructions="基本的な正確性を評価",
            threshold=70.0,
            model="gpt-4o-mini"
        )
        
        # 詳細品質チェック
        self.detail_agent = create_evaluated_gen_agent(
            name="detail_check", 
            generation_instructions="詳細で高品質な回答をしてください",
            evaluation_instructions="""
            詳細品質を評価:
            - 内容の深さ (30点)
            - 論理的一貫性 (25点)
            - 実用性 (25点)
            - 独創性 (20点)
            """,
            threshold=85.0,
            model="gpt-4o"
        )
        
        # 最終品質チェック
        self.expert_agent = create_evaluated_gen_agent(
            name="expert_check",
            generation_instructions="専門家レベルの回答をしてください",
            evaluation_instructions="""
            専門家レベルの品質評価:
            - 専門知識の正確性 (35点)
            - 最新性 (25点)
            - 包括性 (25点) 
            - 引用・根拠 (15点)
            """,
            threshold=92.0,
            model="gpt-4o"
        )
    
    def get_quality_response(self, question: str, quality_level: str = "basic"):
        """品質レベルに応じた回答生成"""
        context = Context()
        
        if quality_level == "basic":
            result = self.basic_agent.run_sync(question, context)
            return result.shared_state["basic_check_result"]
        elif quality_level == "detail":
            result = self.detail_agent.run_sync(question, context)
            return result.shared_state["detail_check_result"]
        elif quality_level == "expert":
            result = self.expert_agent.run_sync(question, context)
            return result.shared_state["expert_check_result"]
        else:
            raise ValueError("Invalid quality level")

# 使用例
quality_system = MultiLayerQualitySystem()

# レベル別回答取得
basic_answer = quality_system.get_quality_response("AIとは何ですか？", "basic")
expert_answer = quality_system.get_quality_response("AIとは何ですか？", "expert")
```

## 高度な事例

### 5. 自適応品質学習システム

```python
import json
from datetime import datetime
from typing import Dict, List

class AdaptiveQualitySystem:
    """ユーザーフィードバックから学習する自適応品質システム"""
    
    def __init__(self):
        self.feedback_history = []
        self.quality_metrics = {
            "accuracy": 0.8,
            "relevance": 0.8, 
            "completeness": 0.8,
            "clarity": 0.8
        }
        
        self.agent = create_evaluated_gen_agent(
            name="adaptive_agent",
            generation_instructions=self._generate_dynamic_instructions(),
            evaluation_instructions=self._generate_dynamic_evaluation(),
            threshold=self._calculate_dynamic_threshold(),
            model="gpt-4o"
        )
    
    def _generate_dynamic_instructions(self) -> str:
        """フィードバックに基づいて動的に生成指示を調整"""
        base_instructions = "高品質な回答を生成してください。"
        
        # 精度が低い場合
        if self.quality_metrics["accuracy"] < 0.7:
            base_instructions += " 特に正確性に注意してください。"
        
        # 関連性が低い場合
        if self.quality_metrics["relevance"] < 0.7:
            base_instructions += " 質問に直接関連する内容に焦点を当ててください。"
        
        # 完全性が低い場合
        if self.quality_metrics["completeness"] < 0.7:
            base_instructions += " 包括的で完全な回答を心がけてください。"
        
        # 明確性が低い場合
        if self.quality_metrics["clarity"] < 0.7:
            base_instructions += " 明確で分かりやすい表現を使ってください。"
        
        return base_instructions
    
    def _generate_dynamic_evaluation(self) -> str:
        """動的評価基準の生成"""
        weights = {
            "accuracy": max(20, int(30 * (1 + (0.8 - self.quality_metrics["accuracy"])))),
            "relevance": max(20, int(25 * (1 + (0.8 - self.quality_metrics["relevance"])))),
            "completeness": max(15, int(25 * (1 + (0.8 - self.quality_metrics["completeness"])))),
            "clarity": max(15, int(20 * (1 + (0.8 - self.quality_metrics["clarity"]))))
        }
        
        return f"""
        以下の基準で評価してください:
        - 正確性 ({weights["accuracy"]}点)
        - 関連性 ({weights["relevance"]}点)
        - 完全性 ({weights["completeness"]}点)
        - 明確性 ({weights["clarity"]}点)
        合計100点満点
        """
    
    def _calculate_dynamic_threshold(self) -> float:
        """動的しきい値計算"""
        avg_quality = sum(self.quality_metrics.values()) / len(self.quality_metrics)
        # 平均品質が低い場合はしきい値を下げて改善機会を増やす
        if avg_quality < 0.7:
            return 75.0
        elif avg_quality > 0.9:
            return 90.0
        else:
            return 80.0
    
    def process_feedback(self, question: str, response: str, user_rating: int, 
                        feedback_details: Dict[str, int]):
        """ユーザーフィードバックを処理して学習"""
        # フィードバック記録
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "response": response,
            "user_rating": user_rating,
            "details": feedback_details
        }
        self.feedback_history.append(feedback_entry)
        
        # 品質メトリクスの更新（移動平均）
        alpha = 0.1  # 学習率
        for metric, score in feedback_details.items():
            if metric in self.quality_metrics:
                normalized_score = score / 100.0
                self.quality_metrics[metric] = (
                    (1 - alpha) * self.quality_metrics[metric] + 
                    alpha * normalized_score
                )
        
        # エージェント設定の更新
        self.agent = create_evaluated_gen_agent(
            name="adaptive_agent",
            generation_instructions=self._generate_dynamic_instructions(),
            evaluation_instructions=self._generate_dynamic_evaluation(),
            threshold=self._calculate_dynamic_threshold(),
            model="gpt-4o"
        )
    
    def get_adaptive_response(self, question: str) -> tuple[str, Dict]:
        """自適応回答生成"""
        result = self.agent.run_sync(question, Context())
        response = result.shared_state["adaptive_agent_result"]
        
        # 現在の品質設定を返す
        current_settings = {
            "threshold": self._calculate_dynamic_threshold(),
            "quality_metrics": self.quality_metrics.copy(),
            "feedback_count": len(self.feedback_history)
        }
        
        return response, current_settings

# 使用例
adaptive_system = AdaptiveQualitySystem()

# 初回回答
response1, settings1 = adaptive_system.get_adaptive_response("機械学習とは何ですか？")
print(f"回答: {response1}")
print(f"設定: {settings1}")

# ユーザーフィードバック（低評価）
adaptive_system.process_feedback(
    "機械学習とは何ですか？",
    response1,
    3,  # 5段階評価で3
    {
        "accuracy": 60,
        "relevance": 70,
        "completeness": 50,
        "clarity": 80
    }
)

# 学習後の回答（改善されたはず）
response2, settings2 = adaptive_system.get_adaptive_response("機械学習とは何ですか？")
print(f"\n学習後回答: {response2}")
print(f"更新設定: {settings2}")
```

### 6. リアルタイム品質監視システム

```python
import threading
import time
from collections import deque
from typing import Optional

class RealTimeQualityMonitor:
    """リアルタイム品質監視システム"""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.quality_scores = deque(maxlen=window_size)
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.quality_alerts = []
        
        self.agent = create_evaluated_gen_agent(
            name="monitored_agent",
            generation_instructions="監視下での高品質回答を生成",
            evaluation_instructions="品質を厳格に評価",
            threshold=80.0,
            model="gpt-4o-mini"
        )
    
    def start_monitoring(self):
        """品質監視開始"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("品質監視開始")
    
    def stop_monitoring(self):
        """品質監視停止"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("品質監視停止")
    
    def _monitor_loop(self):
        """監視ループ"""
        while self.monitoring_active:
            if len(self.quality_scores) >= 3:
                avg_quality = sum(self.quality_scores) / len(self.quality_scores)
                
                # 品質低下アラート
                if avg_quality < 70:
                    alert = {
                        "timestamp": datetime.now().isoformat(),
                        "type": "QUALITY_DROP",
                        "avg_score": avg_quality,
                        "recent_scores": list(self.quality_scores)
                    }
                    self.quality_alerts.append(alert)
                    print(f"⚠️ 品質低下アラート: 平均スコア {avg_quality:.1f}")
                
                # 品質向上通知
                elif avg_quality > 90:
                    print(f"✅ 高品質維持: 平均スコア {avg_quality:.1f}")
            
            time.sleep(5)  # 5秒間隔で監視
    
    def get_monitored_response(self, question: str) -> str:
        """監視付き回答生成"""
        result = self.agent.run_sync(question, Context())
        response = result.shared_state["monitored_agent_result"]
        
        # 品質スコアを記録（実際の実装では評価スコアを取得）
        # ここでは簡易的にランダムなスコアを使用
        import random
        quality_score = random.uniform(60, 95)
        self.quality_scores.append(quality_score)
        
        print(f"品質スコア: {quality_score:.1f}")
        return response
    
    def get_quality_report(self) -> Dict:
        """品質レポート生成"""
        if not self.quality_scores:
            return {"message": "データ不足"}
        
        scores = list(self.quality_scores)
        return {
            "average_quality": sum(scores) / len(scores),
            "min_quality": min(scores),
            "max_quality": max(scores),
            "recent_scores": scores,
            "total_alerts": len(self.quality_alerts),
            "trend": "improving" if len(scores) >= 2 and scores[-1] > scores[0] else "declining"
        }

# 使用例
monitor = RealTimeQualityMonitor()
monitor.start_monitoring()

# 複数の質問で品質監視
questions = [
    "AIの歴史について教えてください",
    "量子コンピューティングの応用は？",
    "気候変動対策について",
    "プログラミング言語の選び方"
]

for question in questions:
    response = monitor.get_monitored_response(question)
    print(f"Q: {question}")
    print(f"A: {response[:100]}...")
    print("-" * 50)
    time.sleep(2)

# 品質レポート確認
report = monitor.get_quality_report()
print(f"\n品質レポート: {report}")

monitor.stop_monitoring()
```

## メリット

- **自動品質管理**: 人手による品質チェックが不要
- **一貫した品質**: 設定した基準を自動的に維持
- **継続的改善**: フィードバックによる自動学習
- **リアルタイム監視**: 品質低下の即座な検出

自律品質保証により、開発者は品質管理の負担から解放され、より創造的な開発に集中できます。

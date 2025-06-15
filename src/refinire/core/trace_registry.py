#!/usr/bin/env python3
"""
Trace Registry - Storage and search functionality for traces
トレースレジストリ - トレースの保存・検索機能

Provides centralized trace management with search capabilities
集中化されたトレース管理と検索機能を提供
"""

import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import threading


@dataclass
class TraceMetadata:
    """
    Trace metadata for search and management
    検索・管理用のトレースメタデータ
    """
    trace_id: str  # Unique trace identifier / ユニークなトレース識別子
    flow_name: Optional[str]  # Flow name / フロー名
    flow_id: Optional[str]  # Flow instance ID / フローインスタンスID
    agent_names: List[str]  # List of agent names used / 使用されたエージェント名のリスト
    start_time: datetime  # Trace start time / トレース開始時刻
    end_time: Optional[datetime]  # Trace end time / トレース終了時刻
    status: str  # Trace status (running, completed, error) / トレースステータス
    total_spans: int  # Number of spans in trace / トレース内のスパン数
    error_count: int  # Number of error spans / エラースパン数
    duration_seconds: Optional[float]  # Total duration / 総実行時間
    tags: Dict[str, Any]  # Custom tags for filtering / フィルタリング用カスタムタグ
    artifacts: Dict[str, Any]  # Trace artifacts / トレース成果物
    

class TraceRegistry:
    """
    Registry for storing and searching traces
    トレースの保存・検索用レジストリ
    
    Provides functionality to:
    以下の機能を提供：
    - Store trace metadata / トレースメタデータの保存
    - Search by flow name, agent name, tags / フロー名、エージェント名、タグによる検索
    - Filter by time range, status / 時間範囲、ステータスによるフィルタ
    - Export/import trace data / トレースデータのエクスポート/インポート
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize trace registry
        トレースレジストリを初期化
        
        Args:
            storage_path: Path to store trace data / トレースデータの保存パス
        """
        self.traces: Dict[str, TraceMetadata] = {}
        self.storage_path = Path(storage_path) if storage_path else None
        self._lock = threading.Lock()
        
        # Load existing traces if storage path exists
        # 保存パスが存在する場合、既存のトレースを読み込み
        if self.storage_path and self.storage_path.exists():
            self.load_traces()
    
    def register_trace(
        self, 
        trace_id: str,
        flow_name: Optional[str] = None,
        flow_id: Optional[str] = None,
        agent_names: Optional[List[str]] = None,
        tags: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a new trace
        新しいトレースを登録
        
        Args:
            trace_id: Unique trace identifier / ユニークなトレース識別子
            flow_name: Flow name / フロー名
            flow_id: Flow instance ID / フローインスタンスID
            agent_names: List of agent names / エージェント名のリスト
            tags: Custom tags / カスタムタグ
        """
        with self._lock:
            metadata = TraceMetadata(
                trace_id=trace_id,
                flow_name=flow_name,
                flow_id=flow_id,
                agent_names=agent_names or [],
                start_time=datetime.now(),
                end_time=None,
                status="running",
                total_spans=0,
                error_count=0,
                duration_seconds=None,
                tags=tags or {},
                artifacts={}
            )
            self.traces[trace_id] = metadata
            self._save_if_configured()
    
    def update_trace(
        self,
        trace_id: str,
        status: Optional[str] = None,
        total_spans: Optional[int] = None,
        error_count: Optional[int] = None,
        artifacts: Optional[Dict[str, Any]] = None,
        add_agent_names: Optional[List[str]] = None,
        add_tags: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update trace metadata
        トレースメタデータを更新
        
        Args:
            trace_id: Trace identifier / トレース識別子
            status: New status / 新しいステータス
            total_spans: Total span count / 総スパン数
            error_count: Error span count / エラースパン数
            artifacts: Trace artifacts / トレース成果物
            add_agent_names: Additional agent names / 追加エージェント名
            add_tags: Additional tags / 追加タグ
        """
        with self._lock:
            if trace_id not in self.traces:
                return
            
            trace = self.traces[trace_id]
            
            if status:
                trace.status = status
                if status in ["completed", "error"]:
                    trace.end_time = datetime.now()
                    if trace.start_time:
                        trace.duration_seconds = (trace.end_time - trace.start_time).total_seconds()
            
            if total_spans is not None:
                trace.total_spans = total_spans
                
            if error_count is not None:
                trace.error_count = error_count
                
            if artifacts:
                trace.artifacts.update(artifacts)
                
            if add_agent_names:
                trace.agent_names.extend(add_agent_names)
                trace.agent_names = list(set(trace.agent_names))  # Remove duplicates
                
            if add_tags:
                trace.tags.update(add_tags)
            
            self._save_if_configured()
    
    def search_by_flow_name(self, flow_name: str, exact_match: bool = False) -> List[TraceMetadata]:
        """
        Search traces by flow name
        フロー名でトレースを検索
        
        Args:
            flow_name: Flow name to search / 検索するフロー名
            exact_match: Whether to use exact matching / 完全一致を使用するか
            
        Returns:
            List[TraceMetadata]: Matching traces / マッチするトレース
        """
        with self._lock:
            results = []
            for trace in self.traces.values():
                if trace.flow_name:
                    if exact_match:
                        if trace.flow_name == flow_name:
                            results.append(trace)
                    else:
                        if flow_name.lower() in trace.flow_name.lower():
                            results.append(trace)
            return results
    
    def search_by_agent_name(self, agent_name: str, exact_match: bool = False) -> List[TraceMetadata]:
        """
        Search traces by agent name
        エージェント名でトレースを検索
        
        Args:
            agent_name: Agent name to search / 検索するエージェント名
            exact_match: Whether to use exact matching / 完全一致を使用するか
            
        Returns:
            List[TraceMetadata]: Matching traces / マッチするトレース
        """
        with self._lock:
            results = []
            for trace in self.traces.values():
                for trace_agent in trace.agent_names:
                    if exact_match:
                        if trace_agent == agent_name:
                            results.append(trace)
                            break
                    else:
                        if agent_name.lower() in trace_agent.lower():
                            results.append(trace)
                            break
            return results
    
    def search_by_tags(self, tags: Dict[str, Any], match_all: bool = True) -> List[TraceMetadata]:
        """
        Search traces by tags
        タグでトレースを検索
        
        Args:
            tags: Tags to search for / 検索するタグ
            match_all: Whether all tags must match / すべてのタグがマッチする必要があるか
            
        Returns:
            List[TraceMetadata]: Matching traces / マッチするトレース
        """
        with self._lock:
            results = []
            for trace in self.traces.values():
                if match_all:
                    # All search tags must be present and match
                    # すべての検索タグが存在し、マッチする必要がある
                    if all(
                        key in trace.tags and trace.tags[key] == value
                        for key, value in tags.items()
                    ):
                        results.append(trace)
                else:
                    # At least one search tag must match
                    # 少なくとも1つの検索タグがマッチする必要がある
                    if any(
                        key in trace.tags and trace.tags[key] == value
                        for key, value in tags.items()
                    ):
                        results.append(trace)
            return results
    
    def search_by_time_range(
        self, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[TraceMetadata]:
        """
        Search traces by time range
        時間範囲でトレースを検索
        
        Args:
            start_time: Search from this time / この時刻から検索
            end_time: Search until this time / この時刻まで検索
            
        Returns:
            List[TraceMetadata]: Matching traces / マッチするトレース
        """
        with self._lock:
            results = []
            for trace in self.traces.values():
                # Check if trace start time is within range
                # トレース開始時刻が範囲内かチェック
                if start_time and trace.start_time < start_time:
                    continue
                if end_time and trace.start_time > end_time:
                    continue
                results.append(trace)
            return results
    
    def search_by_status(self, status: str) -> List[TraceMetadata]:
        """
        Search traces by status
        ステータスでトレースを検索
        
        Args:
            status: Status to search for / 検索するステータス
            
        Returns:
            List[TraceMetadata]: Matching traces / マッチするトレース
        """
        with self._lock:
            return [trace for trace in self.traces.values() if trace.status == status]
    
    def get_trace(self, trace_id: str) -> Optional[TraceMetadata]:
        """
        Get specific trace by ID
        IDで特定のトレースを取得
        
        Args:
            trace_id: Trace identifier / トレース識別子
            
        Returns:
            TraceMetadata | None: Trace metadata if found / 見つかった場合のトレースメタデータ
        """
        with self._lock:
            return self.traces.get(trace_id)
    
    def get_all_traces(self) -> List[TraceMetadata]:
        """
        Get all traces
        すべてのトレースを取得
        
        Returns:
            List[TraceMetadata]: All traces / すべてのトレース
        """
        with self._lock:
            return list(self.traces.values())
    
    def get_recent_traces(self, hours: int = 24) -> List[TraceMetadata]:
        """
        Get recent traces within specified hours
        指定時間内の最近のトレースを取得
        
        Args:
            hours: Number of hours to look back / 遡る時間数
            
        Returns:
            List[TraceMetadata]: Recent traces / 最近のトレース
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return self.search_by_time_range(start_time=cutoff_time)
    
    def complex_search(
        self,
        flow_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: Optional[int] = None
    ) -> List[TraceMetadata]:
        """
        Complex search with multiple criteria
        複数条件による複雑な検索
        
        Args:
            flow_name: Flow name filter / フロー名フィルタ
            agent_name: Agent name filter / エージェント名フィルタ
            tags: Tags filter / タグフィルタ
            status: Status filter / ステータスフィルタ
            start_time: Start time filter / 開始時刻フィルタ
            end_time: End time filter / 終了時刻フィルタ
            max_results: Maximum number of results / 最大結果数
            
        Returns:
            List[TraceMetadata]: Matching traces / マッチするトレース
        """
        with self._lock:
            results = list(self.traces.values())
            
            # Apply filters
            # フィルタを適用
            if flow_name:
                results = [t for t in results if t.flow_name and flow_name.lower() in t.flow_name.lower()]
            
            if agent_name:
                results = [
                    t for t in results 
                    if any(agent_name.lower() in agent.lower() for agent in t.agent_names)
                ]
            
            if tags:
                results = [
                    t for t in results
                    if all(key in t.tags and t.tags[key] == value for key, value in tags.items())
                ]
            
            if status:
                results = [t for t in results if t.status == status]
            
            if start_time:
                results = [t for t in results if t.start_time >= start_time]
            
            if end_time:
                results = [t for t in results if t.start_time <= end_time]
            
            # Sort by start time (newest first)
            # 開始時刻でソート（新しい順）
            results.sort(key=lambda t: t.start_time, reverse=True)
            
            # Limit results
            # 結果数を制限
            if max_results:
                results = results[:max_results]
            
            return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get trace statistics
        トレース統計を取得
        
        Returns:
            Dict[str, Any]: Statistics / 統計情報
        """
        with self._lock:
            total_traces = len(self.traces)
            if total_traces == 0:
                return {"total_traces": 0}
            
            statuses = {}
            flow_names = set()
            agent_names = set()
            total_spans = 0
            total_errors = 0
            durations = []
            
            for trace in self.traces.values():
                # Status distribution
                # ステータス分布
                statuses[trace.status] = statuses.get(trace.status, 0) + 1
                
                # Collect names
                # 名前を収集
                if trace.flow_name:
                    flow_names.add(trace.flow_name)
                agent_names.update(trace.agent_names)
                
                # Aggregate metrics
                # メトリクスを集計
                total_spans += trace.total_spans
                total_errors += trace.error_count
                
                if trace.duration_seconds is not None:
                    durations.append(trace.duration_seconds)
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            return {
                "total_traces": total_traces,
                "status_distribution": statuses,
                "unique_flow_names": len(flow_names),
                "unique_agent_names": len(agent_names),
                "total_spans": total_spans,
                "total_errors": total_errors,
                "average_duration_seconds": avg_duration,
                "flow_names": list(flow_names),
                "agent_names": list(agent_names)
            }
    
    def export_traces(self, file_path: str, format: str = "json") -> None:
        """
        Export traces to file
        トレースをファイルにエクスポート
        
        Args:
            file_path: Output file path / 出力ファイルパス
            format: Export format (json, csv) / エクスポート形式
        """
        with self._lock:
            if format == "json":
                data = {
                    "export_time": datetime.now().isoformat(),
                    "traces": [asdict(trace) for trace in self.traces.values()]
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported export format: {format}")
    
    def import_traces(self, file_path: str, format: str = "json") -> int:
        """
        Import traces from file
        ファイルからトレースをインポート
        
        Args:
            file_path: Input file path / 入力ファイルパス
            format: Import format (json) / インポート形式
            
        Returns:
            int: Number of imported traces / インポートされたトレース数
        """
        with self._lock:
            if format == "json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                imported_count = 0
                for trace_data in data.get("traces", []):
                    # Convert datetime strings back to datetime objects
                    # 日時文字列をdatetimeオブジェクトに戻す
                    if isinstance(trace_data.get("start_time"), str):
                        trace_data["start_time"] = datetime.fromisoformat(trace_data["start_time"])
                    if isinstance(trace_data.get("end_time"), str):
                        trace_data["end_time"] = datetime.fromisoformat(trace_data["end_time"])
                    
                    trace = TraceMetadata(**trace_data)
                    self.traces[trace.trace_id] = trace
                    imported_count += 1
                
                self._save_if_configured()
                return imported_count
            else:
                raise ValueError(f"Unsupported import format: {format}")
    
    def cleanup_old_traces(self, days: int = 30) -> int:
        """
        Remove traces older than specified days
        指定日数より古いトレースを削除
        
        Args:
            days: Number of days to keep / 保持する日数
            
        Returns:
            int: Number of removed traces / 削除されたトレース数
        """
        with self._lock:
            cutoff_time = datetime.now() - timedelta(days=days)
            old_trace_ids = [
                trace_id for trace_id, trace in self.traces.items()
                if trace.start_time < cutoff_time
            ]
            
            for trace_id in old_trace_ids:
                del self.traces[trace_id]
            
            self._save_if_configured()
            return len(old_trace_ids)
    
    def _save_if_configured(self) -> None:
        """
        Save traces to storage if configured
        設定されている場合、トレースを保存
        """
        if self.storage_path:
            self.save_traces()
    
    def save_traces(self) -> None:
        """
        Save traces to storage
        トレースをストレージに保存
        """
        if not self.storage_path:
            return
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.export_traces(str(self.storage_path), "json")
    
    def load_traces(self) -> int:
        """
        Load traces from storage
        ストレージからトレースを読み込み
        
        Returns:
            int: Number of loaded traces / 読み込まれたトレース数
        """
        if not self.storage_path or not self.storage_path.exists():
            return 0
        
        return self.import_traces(str(self.storage_path), "json")


# Global trace registry instance
# グローバルトレースレジストリインスタンス
_global_registry: Optional[TraceRegistry] = None


def get_global_registry() -> TraceRegistry:
    """
    Get global trace registry instance
    グローバルトレースレジストリインスタンスを取得
    
    Returns:
        TraceRegistry: Global registry instance / グローバルレジストリインスタンス
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = TraceRegistry()
    return _global_registry


def set_global_registry(registry: TraceRegistry) -> None:
    """
    Set global trace registry instance
    グローバルトレースレジストリインスタンスを設定
    
    Args:
        registry: Registry instance to set as global / グローバルに設定するレジストリインスタンス
    """
    global _global_registry
    _global_registry = registry 

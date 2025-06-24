#!/usr/bin/env python3
"""
Debug SourceCodeProvider
SourceCodeProviderのデバッグ
"""

import os
from pathlib import Path
from refinire.agents.providers.source_code import SourceCodeProvider

def main():
    print("🔍 Debugging SourceCodeProvider")
    print("=" * 50)
    
    # 現在のディレクトリを確認
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # プロジェクトルートを確認
    project_root = Path(__file__).parent
    print(f"Project root: {project_root}")
    
    # SourceCodeProviderを作成
    provider = SourceCodeProvider(
        base_path=".",
        max_files=5,
        max_file_size=1000
    )
    
    print(f"Provider base_path: {provider.base_path}")
    print(f"Provider base_path exists: {provider.base_path.exists()}")
    
    # ファイルツリーをスキャン
    print("\n📁 Scanning file tree...")
    try:
        files = provider._scan_file_tree()
        print(f"Found {len(files)} files")
        for i, file in enumerate(files[:10]):  # 最初の10ファイルを表示
            print(f"  {i+1}. {file}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more files")
    except Exception as e:
        print(f"Error scanning files: {e}")
    
    # コンテキストを取得してみる
    print("\n📝 Getting context for 'What is Refinire?'...")
    try:
        # ファイル選択プロセスをデバッグ
        print("Available files:", len(files))
        print("Sample files:", files[:5])
        
        # 関連ファイルの選択をテスト
        relevant_files = provider._select_relevant_files("What is Refinire?", files)
        print(f"Relevant files found: {len(relevant_files)}")
        for i, file in enumerate(relevant_files):
            print(f"  {i+1}. {file}")
        
        context = provider.get_context("What is Refinire?")
        print(f"Context length: {len(context)}")
        print(f"Context preview: {context[:200]}...")
    except Exception as e:
        print(f"Error getting context: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
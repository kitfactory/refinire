#!/usr/bin/env python3
"""
NotificationAgent Examples
NotificationAgentの使用例

This example demonstrates how to use NotificationAgent for sending notifications
through various channels including logs, files, webhooks, and more.
この例では、ログ、ファイル、webhook等の様々なチャネルを通じて
通知を送信するためにNotificationAgentを使用する方法を示します。

SECURITY NOTE: This file contains example/demo URLs only. 
Never commit real webhook URLs, API keys, or secrets to version control.
Use environment variables for production credentials.

セキュリティ注意: このファイルには例/デモ用のURLのみが含まれています。
実際のWebhook URL、APIキー、機密情報をバージョン管理にコミットしないでください。
本番認証情報には環境変数を使用してください。
"""

import sys
import os
import asyncio
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.agents.notification import (
    NotificationAgent, NotificationConfig, NotificationChannel,
    LogChannel, FileChannel, WebhookChannel, SlackChannel, TeamsChannel,
    create_log_notifier, create_file_notifier, create_webhook_notifier,
    create_slack_notifier, create_teams_notifier, create_multi_channel_notifier
)
from refinire.context import Context


async def example_1_log_notifications():
    """
    Example 1: Simple log notifications.
    例1: シンプルなログ通知。
    """
    print("\n" + "="*60)
    print("Example 1: Log Notifications")
    print("例1: ログ通知")
    print("="*60)
    
    # Create log notifier using utility function
    # ユーティリティ関数を使ってログ通知エージェントを作成
    log_notifier = create_log_notifier("system_logger", "INFO")
    
    # Sample notifications
    # 通知のサンプル
    notifications = [
        "System startup completed successfully",
        "Database connection established",
        "User authentication service is running",
        "All services are operational"
    ]
    
    print("Sending log notifications:")
    print("ログ通知を送信中:")
    
    ctx = Context()
    for i, notification in enumerate(notifications, 1):
        print(f"\n{i}. Sending: {notification}")
        
        # Set custom subject for this notification
        # この通知用にカスタム件名を設定
        log_notifier.set_subject(f"System Status #{i}", ctx)
        
        result_ctx = await log_notifier.run(notification, ctx)
        
        status = result_ctx.shared_state.get("system_logger_status")
        success_count = result_ctx.shared_state.get("system_logger_success_count", 0)
        total_count = result_ctx.shared_state.get("system_logger_total_count", 0)
        
        print(f"   Status: {status} ({success_count}/{total_count} channels)")


async def example_2_file_notifications():
    """
    Example 2: File-based notifications.
    例2: ファイルベースの通知。
    """
    print("\n" + "="*60)
    print("Example 2: File Notifications")
    print("例2: ファイル通知")
    print("="*60)
    
    # Create temporary file for notifications
    # 通知用の一時ファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create file notifier
        # ファイル通知エージェントを作成
        file_notifier = create_file_notifier("audit_logger", temp_path)
        
        # Sample audit events
        # 監査イベントのサンプル
        audit_events = [
            "User 'admin' logged in from IP 192.168.1.100",
            "File 'sensitive_data.xlsx' was accessed by user 'john.doe'",
            "Configuration change: max_connections increased to 1000",
            "Backup process completed successfully - 2.5GB archived"
        ]
        
        print(f"Writing notifications to file: {temp_path}")
        print(f"ファイルに通知を書き込み中: {temp_path}")
        
        ctx = Context()
        for i, event in enumerate(audit_events, 1):
            print(f"\n{i}. Recording: {event[:50]}{'...' if len(event) > 50 else ''}")
            
            # Set audit subject
            # 監査件名を設定
            file_notifier.set_subject(f"AUDIT-{i:03d}", ctx)
            
            result_ctx = await file_notifier.run(event, ctx)
            
            status = result_ctx.shared_state.get("audit_logger_status")
            print(f"   Status: {status}")
        
        # Display file contents
        # ファイル内容を表示
        print(f"\nFile contents:")
        print(f"ファイル内容:")
        print("-" * 40)
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        print("-" * 40)
    
    finally:
        # Clean up temporary file
        # 一時ファイルをクリーンアップ
        os.unlink(temp_path)


async def example_3_multi_channel_notifications():
    """
    Example 3: Multi-channel notifications.
    例3: マルチチャネル通知。
    """
    print("\n" + "="*60)
    print("Example 3: Multi-Channel Notifications")
    print("例3: マルチチャネル通知")
    print("="*60)
    
    # Create temporary file for one of the channels
    # チャネルの一つ用に一時ファイルを作成
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create multi-channel notifier
        # マルチチャネル通知エージェントを作成
        channels = [
            {"type": "log", "name": "console_log", "log_level": "INFO"},
            {"type": "log", "name": "error_log", "log_level": "ERROR"},
            {"type": "file", "name": "file_log", "file_path": temp_path, "include_timestamp": True}
        ]
        
        multi_notifier = create_multi_channel_notifier("alert_system", channels)
        
        # Sample critical alerts
        # 重要アラートのサンプル
        alerts = [
            "CRITICAL: Database connection lost - attempting reconnection",
            "WARNING: High memory usage detected - 85% of available RAM",
            "INFO: Scheduled maintenance window starting in 30 minutes",
            "ERROR: Failed to process payment for order #12345"
        ]
        
        print("Sending alerts through multiple channels:")
        print("複数チャネルを通じてアラートを送信中:")
        
        ctx = Context()
        for i, alert in enumerate(alerts, 1):
            severity = alert.split(":")[0]
            message = alert.split(":", 1)[1].strip()
            
            print(f"\n{i}. [{severity}] {message}")
            
            # Set alert subject with severity
            # 重要度付きのアラート件名を設定
            multi_notifier.set_subject(f"ALERT-{severity}-{i:03d}", ctx)
            
            result_ctx = await multi_notifier.run(alert, ctx)
            
            status = result_ctx.shared_state.get("alert_system_status")
            success_count = result_ctx.shared_state.get("alert_system_success_count", 0)
            total_count = result_ctx.shared_state.get("alert_system_total_count", 0)
            
            print(f"   Delivery: {status} ({success_count}/{total_count} channels)")
            
            # Show detailed results
            # 詳細結果を表示
            result = result_ctx.shared_state.get("alert_system_result", {})
            if result.get("errors"):
                print(f"   Errors: {len(result['errors'])}")
        
        # Display file log contents
        # ファイルログ内容を表示
        print(f"\nFile log contents:")
        print(f"ファイルログ内容:")
        print("-" * 50)
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        print("-" * 50)
    
    finally:
        # Clean up temporary file
        # 一時ファイルをクリーンアップ
        os.unlink(temp_path)


async def example_4_webhook_notifications():
    """
    Example 4: Webhook notifications (simulated).
    例4: Webhook通知（シミュレート）。
    """
    print("\n" + "="*60)
    print("Example 4: Webhook Notifications (Simulated)")
    print("例4: Webhook通知（シミュレート）")
    print("="*60)
    
    # Create webhook notifier (URL is simulated)
    # Webhook通知エージェントを作成（URLはシミュレート）
    webhook_notifier = create_webhook_notifier(
        "integration_webhook",
        "https://api.example.com/webhooks/notifications"
    )
    
    # Sample integration events
    # 統合イベントのサンプル
    events = [
        "New customer registration: john.doe@example.com",
        "Order completed: #ORD-2024-001 - $299.99",
        "Support ticket created: #TKT-456 - Login issues",
        "Payment processed: $149.50 for subscription renewal"
    ]
    
    print("Sending webhook notifications:")
    print("Webhook通知を送信中:")
    print("(Note: These are simulated - no actual HTTP requests)")
    print("（注意：これらはシミュレートです - 実際のHTTPリクエストは送信されません）")
    
    ctx = Context()
    for i, event in enumerate(events, 1):
        event_type = event.split(":")[0]
        
        print(f"\n{i}. Event: {event}")
        
        # Set event-specific subject
        # イベント固有の件名を設定
        webhook_notifier.set_subject(f"Event-{event_type.replace(' ', '')}-{i}", ctx)
        
        try:
            # This will fail because the URL is fake, but we can see the attempt
            # URLが偽物なので失敗しますが、試行を確認できます
            result_ctx = await webhook_notifier.run(event, ctx)
            
            status = result_ctx.shared_state.get("integration_webhook_status")
            print(f"   Status: {status}")
            
            # Show webhook payload that would be sent
            # 送信されるであろうWebhookペイロードを表示
            webhook_channel = webhook_notifier.get_channels()[0]
            payload = webhook_channel.payload_template.format(
                message=event.replace('"', '\\"'),
                subject=f"Event-{event_type.replace(' ', '')}-{i}",
                timestamp="2024-01-01T12:00:00Z"
            )
            print(f"   Payload: {payload}")
            
        except Exception as e:
            print(f"   Expected error (simulated): {type(e).__name__}")


async def example_5_slack_teams_notifications():
    """
    Example 5: Slack and Teams notifications (simulated).
    例5: SlackとTeams通知（シミュレート）。
    """
    print("\n" + "="*60)
    print("Example 5: Slack & Teams Notifications (Simulated)")
    print("例5: SlackとTeams通知（シミュレート）")
    print("="*60)
    
    # Create Slack notifier
    # Slack通知エージェントを作成
    # NOTE: Use environment variable SLACK_WEBHOOK_URL in production
    # 注意：本番環境では環境変数SLACK_WEBHOOK_URLを使用してください
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/services/EXAMPLE/DUMMY/WEBHOOK_URL_FOR_DEMO_ONLY')
    slack_notifier = create_slack_notifier(
        "team_slack",
        slack_webhook_url,
        "#general"
    )
    
    # Create Teams notifier
    # Teams通知エージェントを作成
    teams_notifier = create_teams_notifier(
        "team_teams",
        "https://outlook.office.com/webhook/00000000-0000-0000-0000-000000000000@00000000-0000-0000-0000-000000000000/IncomingWebhook/00000000000000000000000000000000/00000000-0000-0000-0000-000000000000"
    )
    
    # Sample team notifications
    # チーム通知のサンプル
    team_updates = [
        "🚀 Deployment to production completed successfully!",
        "📊 Weekly metrics report is now available",
        "🔧 Scheduled maintenance window: Tonight 2-4 AM",
        "🎉 New team member Sarah joined the development team"
    ]
    
    print("Sending team notifications:")
    print("チーム通知を送信中:")
    print("(Note: These are simulated - no actual webhooks sent)")
    print("（注意：これらはシミュレートです - 実際のWebhookは送信されません）")
    print("SECURITY: Use environment variables for real webhook URLs")
    print("セキュリティ: 実際のWebhook URLには環境変数を使用してください")
    
    ctx = Context()
    for i, update in enumerate(team_updates, 1):
        print(f"\n{i}. Update: {update}")
        
        # Send to Slack
        # Slackに送信
        print("   → Slack:")
        slack_notifier.set_subject(f"Team Update #{i}", ctx)
        
        try:
            result_ctx = await slack_notifier.run(update, ctx)
            status = result_ctx.shared_state.get("team_slack_status")
            print(f"     Status: {status}")
            
            # Show Slack payload
            # Slackペイロードを表示
            slack_channel = slack_notifier.get_channels()[0]
            slack_payload = slack_channel.payload_template.format(
                message=update.replace('"', '\\"')
            )
            print(f"     Payload: {slack_payload}")
            
        except Exception as e:
            print(f"     Expected error: {type(e).__name__}")
        
        # Send to Teams
        # Teamsに送信
        print("   → Teams:")
        teams_notifier.set_subject(f"Team Update #{i}", ctx)
        
        try:
            result_ctx = await teams_notifier.run(update, ctx)
            status = result_ctx.shared_state.get("team_teams_status")
            print(f"     Status: {status}")
            
            # Show Teams payload (first 100 chars)
            # Teamsペイロードを表示（最初の100文字）
            teams_channel = teams_notifier.get_channels()[0]
            teams_payload = teams_channel.payload_template.format(
                message=update.replace('"', '\\"'),
                subject=f"Team Update #{i}"
            )
            print(f"     Payload: {teams_payload[:100]}...")
            
        except Exception as e:
            print(f"     Expected error: {type(e).__name__}")


async def example_6_custom_notification_channel():
    """
    Example 6: Custom notification channel.
    例6: カスタム通知チャネル。
    """
    print("\n" + "="*60)
    print("Example 6: Custom Notification Channel")
    print("例6: カスタム通知チャネル")
    print("="*60)
    
    # Create custom notification channel
    # カスタム通知チャネルを作成
    class DatabaseNotificationChannel(NotificationChannel):
        """Custom channel that simulates database logging."""
        
        def __init__(self, name: str = "database_channel"):
            super().__init__(name)
            self.notifications = []  # Simulate database storage
        
        async def send(self, message: str, subject: str = None, context: Context = None) -> bool:
            """Simulate storing notification in database."""
            try:
                notification_record = {
                    "id": len(self.notifications) + 1,
                    "subject": subject or "No Subject",
                    "message": message,
                    "timestamp": "2024-01-01T12:00:00Z",
                    "status": "sent"
                }
                
                self.notifications.append(notification_record)
                print(f"     [DB] Stored notification #{notification_record['id']}")
                return True
                
            except Exception as e:
                print(f"     [DB] Error: {e}")
                return False
        
        def get_notifications(self):
            """Get all stored notifications."""
            return self.notifications.copy()
    
    # Create notification agent with custom channel
    # カスタムチャネルを持つ通知エージェントを作成
    config = NotificationConfig(
        name="custom_notifier",
        default_subject="Custom Notification"
    )
    
    db_channel = DatabaseNotificationChannel("database_logger")
    log_channel = LogChannel("console_logger", "INFO")
    
    custom_notifier = NotificationAgent(config, [db_channel, log_channel])
    
    # Sample notifications
    # 通知のサンプル
    notifications = [
        "User profile updated successfully",
        "New comment posted on article #123",
        "Password reset requested for user@example.com",
        "Monthly report generation completed"
    ]
    
    print("Sending notifications through custom channel:")
    print("カスタムチャネルを通じて通知を送信中:")
    
    ctx = Context()
    for i, notification in enumerate(notifications, 1):
        print(f"\n{i}. Processing: {notification}")
        
        custom_notifier.set_subject(f"Event-{i:03d}", ctx)
        
        result_ctx = await custom_notifier.run(notification, ctx)
        
        status = result_ctx.shared_state.get("custom_notifier_status")
        success_count = result_ctx.shared_state.get("custom_notifier_success_count", 0)
        total_count = result_ctx.shared_state.get("custom_notifier_total_count", 0)
        
        print(f"   Status: {status} ({success_count}/{total_count} channels)")
    
    # Display stored notifications
    # 保存された通知を表示
    print(f"\nStored notifications in database:")
    print(f"データベースに保存された通知:")
    print("-" * 50)
    for record in db_channel.get_notifications():
        print(f"ID: {record['id']} | Subject: {record['subject']}")
        print(f"Message: {record['message']}")
        print(f"Time: {record['timestamp']} | Status: {record['status']}")
        print("-" * 50)


async def example_7_notification_error_handling():
    """
    Example 7: Error handling and fail-fast behavior.
    例7: エラーハンドリングとfail-fast動作。
    """
    print("\n" + "="*60)
    print("Example 7: Error Handling & Fail-Fast")
    print("例7: エラーハンドリングとFail-Fast")
    print("="*60)
    
    # Create notifier with fail-fast enabled
    # fail-fastを有効にした通知エージェントを作成
    config_fail_fast = NotificationConfig(
        name="fail_fast_notifier",
        channels=[
            {"type": "email", "name": "email_channel"},  # Will fail (not configured)
            {"type": "log", "name": "log_channel", "log_level": "INFO"},  # Would succeed
            {"type": "file", "name": "file_channel", "file_path": "test.log"}  # Would succeed
        ],
        fail_fast=True
    )
    
    fail_fast_notifier = NotificationAgent(config_fail_fast)
    
    # Create notifier without fail-fast
    # fail-fastなしの通知エージェントを作成
    config_continue = NotificationConfig(
        name="continue_notifier",
        channels=[
            {"type": "email", "name": "email_channel"},  # Will fail (not configured)
            {"type": "log", "name": "log_channel", "log_level": "INFO"},  # Will succeed
            {"type": "file", "name": "file_channel", "file_path": "test.log"}  # Will succeed
        ],
        fail_fast=False
    )
    
    continue_notifier = NotificationAgent(config_continue)
    
    test_message = "Test notification with mixed channel success/failure"
    
    print("Testing fail-fast behavior:")
    print("fail-fast動作をテスト中:")
    
    # Test fail-fast notifier
    # fail-fast通知エージェントをテスト
    print(f"\n1. Fail-fast enabled:")
    ctx = Context()
    result_ctx = await fail_fast_notifier.run(test_message, ctx)
    
    status = result_ctx.shared_state.get("fail_fast_notifier_status")
    success_count = result_ctx.shared_state.get("fail_fast_notifier_success_count", 0)
    total_count = result_ctx.shared_state.get("fail_fast_notifier_total_count", 0)
    result = result_ctx.shared_state.get("fail_fast_notifier_result", {})
    
    print(f"   Status: {status}")
    print(f"   Success: {success_count}/{total_count} channels")
    print(f"   Errors: {len(result.get('errors', []))}")
    
    # Test continue notifier
    # 継続通知エージェントをテスト
    print(f"\n2. Fail-fast disabled:")
    ctx = Context()
    result_ctx = await continue_notifier.run(test_message, ctx)
    
    status = result_ctx.shared_state.get("continue_notifier_status")
    success_count = result_ctx.shared_state.get("continue_notifier_success_count", 0)
    total_count = result_ctx.shared_state.get("continue_notifier_total_count", 0)
    result = result_ctx.shared_state.get("continue_notifier_result", {})
    
    print(f"   Status: {status}")
    print(f"   Success: {success_count}/{total_count} channels")
    print(f"   Errors: {len(result.get('errors', []))}")
    
    # Show error details
    # エラー詳細を表示
    if result.get('errors'):
        print(f"   Error details:")
        for error in result['errors'][:2]:  # Show first 2 errors
            print(f"     - {error}")
    
    # Clean up test file
    # テストファイルをクリーンアップ
    try:
        os.unlink("test.log")
    except FileNotFoundError:
        pass


def example_production_setup():
    """
    Example of production-ready setup with environment variables.
    環境変数を使用した本番対応セットアップの例。
    """
    print("\n" + "="*60)
    print("Production Setup Example (Environment Variables)")
    print("本番セットアップ例（環境変数）")
    print("="*60)
    
    print("To use real webhooks in production, set these environment variables:")
    print("本番で実際のWebhookを使用するには、以下の環境変数を設定してください:")
    print()
    print("export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/REAL/WEBHOOK'")
    print("export TEAMS_WEBHOOK_URL='https://outlook.office.com/webhook/YOUR/REAL/WEBHOOK'")
    print("export API_WEBHOOK_URL='https://your-api.com/webhooks/notifications'")
    print()
    print("Then use them in your code like this:")
    print("そして、コード内で以下のように使用します:")
    print()
    print("    import os")
    print("    slack_url = os.getenv('SLACK_WEBHOOK_URL')")
    print("    if not slack_url:")
    print("        raise ValueError('SLACK_WEBHOOK_URL environment variable not set')")
    print("    slack_notifier = create_slack_notifier('production_slack', slack_url)")
    print()


async def main():
    """
    Main function to run all examples.
    全ての例を実行するメイン関数。
    """
    print("NotificationAgent Examples")
    print("NotificationAgent使用例")
    print("=" * 80)
    
    examples = [
        example_1_log_notifications,
        example_2_file_notifications,
        example_3_multi_channel_notifications,
        example_4_webhook_notifications,
        example_5_slack_teams_notifications,
        example_6_custom_notification_channel,
        example_7_notification_error_handling
    ]
    
    # Show production setup example (non-async)
    # 本番セットアップ例を表示（非同期でない）
    example_production_setup()
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
            print(f"エラー in {example.__name__}: {e}")
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("全ての例が完了しました！")
    print("\nNote: Webhook examples are simulated and don't send real HTTP requests.")
    print("注意: Webhookの例はシミュレートされており、実際のHTTPリクエストは送信されません。")


if __name__ == "__main__":
    asyncio.run(main()) 

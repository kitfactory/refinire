"""
NotificationAgent implementation for sending notifications through various channels.

NotificationAgentは様々なチャネルを通じて通知を送信するエージェントです。
メール、Webhook、ログなどの複数の通知方法をサポートしています。
"""

import logging
import json
import smtplib
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, List, Optional, Dict, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import urllib.request
import urllib.parse

from .flow.context import Context
from .flow.step import Step

logger = logging.getLogger(__name__)


class NotificationChannel(ABC):
    """
    Abstract base class for notification channels.
    通知チャネルの抽象基底クラス。
    """
    
    def __init__(self, name: str, enabled: bool = True):
        """
        Initialize notification channel.
        通知チャネルを初期化します。
        
        Args:
            name: Channel name / チャネル名
            enabled: Whether channel is enabled / チャネルが有効かどうか
        """
        self.name = name
        self.enabled = enabled
    
    @abstractmethod
    async def send(self, message: str, subject: str = None, context: Context = None) -> bool:
        """
        Send notification through this channel.
        このチャネルを通じて通知を送信します。
        
        Args:
            message: Notification message / 通知メッセージ
            subject: Message subject / メッセージ件名
            context: Execution context / 実行コンテキスト
            
        Returns:
            bool: True if sent successfully / 送信が成功した場合True
        """
        pass


class LogChannel(NotificationChannel):
    """
    Notification channel that logs messages.
    メッセージをログに記録する通知チャネル。
    """
    
    def __init__(self, name: str = "log_channel", log_level: str = "INFO"):
        """
        Initialize log channel.
        ログチャネルを初期化します。
        
        Args:
            name: Channel name / チャネル名
            log_level: Log level (DEBUG, INFO, WARNING, ERROR) / ログレベル
        """
        super().__init__(name)
        self.log_level = log_level.upper()
    
    async def send(self, message: str, subject: str = None, context: Context = None) -> bool:
        """Send notification via logging."""
        try:
            log_message = f"[NOTIFICATION] {subject}: {message}" if subject else f"[NOTIFICATION] {message}"
            
            if self.log_level == "DEBUG":
                logger.debug(log_message)
            elif self.log_level == "INFO":
                logger.info(log_message)
            elif self.log_level == "WARNING":
                logger.warning(log_message)
            elif self.log_level == "ERROR":
                logger.error(log_message)
            else:
                logger.info(log_message)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send log notification: {e}")
            return False


class EmailChannel(NotificationChannel):
    """
    Notification channel for email delivery.
    メール配信用の通知チャネル。
    """
    
    def __init__(self, name: str = "email_channel", smtp_server: str = None,
                 smtp_port: int = 587, username: str = None, password: str = None,
                 from_email: str = None, to_emails: List[str] = None,
                 use_tls: bool = True):
        """
        Initialize email channel.
        メールチャネルを初期化します。
        
        Args:
            name: Channel name / チャネル名
            smtp_server: SMTP server address / SMTPサーバーアドレス
            smtp_port: SMTP server port / SMTPサーバーポート
            username: SMTP username / SMTPユーザー名
            password: SMTP password / SMTPパスワード
            from_email: Sender email address / 送信者メールアドレス
            to_emails: List of recipient email addresses / 受信者メールアドレスのリスト
            use_tls: Whether to use TLS encryption / TLS暗号化を使用するかどうか
        """
        super().__init__(name)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails or []
        self.use_tls = use_tls
    
    async def send(self, message: str, subject: str = None, context: Context = None) -> bool:
        """Send notification via email."""
        if not self.smtp_server or not self.from_email or not self.to_emails:
            logger.warning("Email channel not properly configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            msg['Subject'] = subject or "Notification"
            
            # Add message body
            msg.attach(MIMEText(message, 'plain'))
            
            # Connect to server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {len(self.to_emails)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False


class WebhookChannel(NotificationChannel):
    """
    Notification channel for webhook delivery.
    Webhook配信用の通知チャネル。
    """
    
    def __init__(self, name: str = "webhook_channel", webhook_url: str = None,
                 method: str = "POST", headers: Dict[str, str] = None,
                 payload_template: str = None):
        """
        Initialize webhook channel.
        Webhookチャネルを初期化します。
        
        Args:
            name: Channel name / チャネル名
            webhook_url: Webhook URL / Webhook URL
            method: HTTP method (POST, PUT) / HTTPメソッド
            headers: Additional HTTP headers / 追加HTTPヘッダー
            payload_template: JSON payload template / JSONペイロードテンプレート
        """
        super().__init__(name)
        self.webhook_url = webhook_url
        self.method = method.upper()
        self.headers = headers or {"Content-Type": "application/json"}
        self.payload_template = payload_template or '{{"message": "{message}", "subject": "{subject}", "timestamp": "{timestamp}"}}'
    
    async def send(self, message: str, subject: str = None, context: Context = None) -> bool:
        """Send notification via webhook."""
        if not self.webhook_url:
            logger.warning("Webhook URL not configured")
            return False
        
        try:
            # Prepare payload
            timestamp = datetime.now().isoformat()
            
            # Escape quotes in message and subject for JSON
            escaped_message = message.replace('"', '\\"').replace('\n', '\\n')
            escaped_subject = (subject or "").replace('"', '\\"').replace('\n', '\\n')
            
            payload = self.payload_template.format(
                message=escaped_message,
                subject=escaped_subject,
                timestamp=timestamp
            )
            
            # Validate JSON format
            try:
                json.loads(payload)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON payload: {e}, payload: {payload}")
                return False
            
            # Create request
            data = payload.encode('utf-8')
            req = urllib.request.Request(
                self.webhook_url,
                data=data,
                headers=self.headers,
                method=self.method
            )
            
            # Send request
            with urllib.request.urlopen(req, timeout=30) as response:
                if 200 <= response.status < 300:
                    logger.info(f"Webhook notification sent successfully to {self.webhook_url}")
                    return True
                else:
                    logger.warning(f"Webhook responded with status {response.status}")
                    return False
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False


class SlackChannel(WebhookChannel):
    """
    Specialized webhook channel for Slack notifications.
    Slack通知用の特化したWebhookチャネル。
    """
    
    def __init__(self, name: str = "slack_channel", webhook_url: str = None,
                 channel: str = None, username: str = "NotificationBot"):
        """
        Initialize Slack channel.
        Slackチャネルを初期化します。
        
        Args:
            name: Channel name / チャネル名
            webhook_url: Slack webhook URL / Slack webhook URL
            channel: Slack channel name / Slackチャネル名
            username: Bot username / ボットユーザー名
        """
        if channel:
            slack_payload = '{{"text": "{{message}}", "channel": "{}", "username": "{}"}}'.format(channel, username)
        else:
            slack_payload = '{{"text": "{message}"}}'
        
        super().__init__(
            name=name,
            webhook_url=webhook_url,
            payload_template=slack_payload
        )


class TeamsChannel(WebhookChannel):
    """
    Specialized webhook channel for Microsoft Teams notifications.
    Microsoft Teams通知用の特化したWebhookチャネル。
    """
    
    def __init__(self, name: str = "teams_channel", webhook_url: str = None):
        """
        Initialize Teams channel.
        Teamsチャネルを初期化します。
        
        Args:
            name: Channel name / チャネル名
            webhook_url: Teams webhook URL / Teams webhook URL
        """
        teams_payload = '''{{
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "{subject}",
            "sections": [{{
                "activityTitle": "{subject}",
                "text": "{message}"
            }}]
        }}'''
        
        super().__init__(
            name=name,
            webhook_url=webhook_url,
            payload_template=teams_payload
        )


class FileChannel(NotificationChannel):
    """
    Notification channel that writes to a file.
    ファイルに書き込む通知チャネル。
    """
    
    def __init__(self, name: str = "file_channel", file_path: str = None,
                 append_mode: bool = True, include_timestamp: bool = True):
        """
        Initialize file channel.
        ファイルチャネルを初期化します。
        
        Args:
            name: Channel name / チャネル名
            file_path: Path to output file / 出力ファイルパス
            append_mode: Whether to append to file / ファイルに追記するかどうか
            include_timestamp: Whether to include timestamp / タイムスタンプを含めるかどうか
        """
        super().__init__(name)
        self.file_path = file_path or "notifications.log"
        self.append_mode = append_mode
        self.include_timestamp = include_timestamp
    
    async def send(self, message: str, subject: str = None, context: Context = None) -> bool:
        """Send notification to file."""
        try:
            mode = "a" if self.append_mode else "w"
            
            with open(self.file_path, mode, encoding='utf-8') as f:
                timestamp = datetime.now().isoformat() if self.include_timestamp else ""
                subject_part = f"[{subject}]" if subject else ""
                
                if self.include_timestamp and subject:
                    line = f"{timestamp} {subject_part} {message}\n"
                elif self.include_timestamp:
                    line = f"{timestamp} {message}\n"
                elif subject:
                    line = f"{subject_part} {message}\n"
                else:
                    line = f"{message}\n"
                
                f.write(line)
            
            logger.info(f"File notification written to {self.file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write file notification: {e}")
            return False


class NotificationResult:
    """
    Result of notification operation.
    通知操作の結果。
    """
    
    def __init__(self, total_channels: int = 0, successful_channels: int = 0,
                 failed_channels: List[str] = None, errors: List[str] = None):
        """
        Initialize notification result.
        通知結果を初期化します。
        
        Args:
            total_channels: Total number of channels / 総チャネル数
            successful_channels: Number of successful channels / 成功したチャネル数
            failed_channels: List of failed channel names / 失敗したチャネル名のリスト
            errors: List of error messages / エラーメッセージのリスト
        """
        self.total_channels = total_channels
        self.successful_channels = successful_channels
        self.failed_channels = failed_channels or []
        self.errors = errors or []
        self.timestamp = datetime.now()
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_channels == 0:
            return 100.0
        return (self.successful_channels / self.total_channels) * 100
    
    @property
    def is_success(self) -> bool:
        """Check if all notifications were successful."""
        return self.successful_channels == self.total_channels
    
    def add_error(self, channel_name: str, error: str):
        """Add an error for a specific channel."""
        self.failed_channels.append(channel_name)
        self.errors.append(f"[{channel_name}] {error}")
    
    def __str__(self) -> str:
        return f"NotificationResult({self.successful_channels}/{self.total_channels} successful, {len(self.errors)} errors)"


class NotificationConfig(BaseModel):
    """
    Configuration for NotificationAgent.
    NotificationAgentの設定。
    """
    
    name: str = Field(description="Name of the notification agent / 通知エージェントの名前")
    
    channels: List[Dict[str, Any]] = Field(
        default=[],
        description="List of notification channel configurations / 通知チャネル設定のリスト"
    )
    
    default_subject: str = Field(
        default="Notification",
        description="Default subject for notifications / 通知のデフォルト件名"
    )
    
    fail_fast: bool = Field(
        default=False,
        description="Stop on first channel failure / 最初のチャネル失敗で停止"
    )
    
    store_result: bool = Field(
        default=True,
        description="Store notification result in context / 通知結果をコンテキストに保存"
    )
    
    require_all_success: bool = Field(
        default=False,
        description="Require all channels to succeed / 全てのチャネルの成功を要求"
    )
    
    @field_validator("channels")
    @classmethod
    def channels_not_empty(cls, v):
        """Validate that at least one channel is configured."""
        if not v:
            logger.warning("No notification channels configured")
        return v


class NotificationAgent(Step):
    """
    Notification agent for sending notifications through various channels.
    様々なチャネルを通じて通知を送信する通知エージェント。
    
    The NotificationAgent supports multiple notification channels including
    email, webhooks, Slack, Teams, logging, and file output.
    NotificationAgentはメール、webhook、Slack、Teams、ログ、ファイル出力を含む
    複数の通知チャネルをサポートしています。
    """
    
    def __init__(self, config: NotificationConfig, custom_channels: List[NotificationChannel] = None):
        """
        Initialize NotificationAgent.
        NotificationAgentを初期化します。
        
        Args:
            config: Notification configuration / 通知設定
            custom_channels: Optional custom notification channels / オプションのカスタム通知チャネル
        """
        super().__init__(name=config.name)
        self.config = config
        self.notification_channels = self._build_notification_channels(custom_channels or [])
    
    def _build_notification_channels(self, custom_channels: List[NotificationChannel]) -> List[NotificationChannel]:
        """
        Build notification channels from configuration and custom channels.
        設定とカスタムチャネルから通知チャネルを構築します。
        """
        channels = list(custom_channels)
        
        # Build channels from configuration
        # 設定からチャネルを構築
        for channel_config in self.config.channels:
            channel_type = channel_config.get("type")
            channel_name = channel_config.get("name", channel_type)
            enabled = channel_config.get("enabled", True)
            
            if channel_type == "log":
                log_level = channel_config.get("log_level", "INFO")
                channels.append(LogChannel(channel_name, log_level))
                
            elif channel_type == "email":
                email_channel = EmailChannel(
                    name=channel_name,
                    smtp_server=channel_config.get("smtp_server"),
                    smtp_port=channel_config.get("smtp_port", 587),
                    username=channel_config.get("username"),
                    password=channel_config.get("password"),
                    from_email=channel_config.get("from_email"),
                    to_emails=channel_config.get("to_emails", []),
                    use_tls=channel_config.get("use_tls", True)
                )
                email_channel.enabled = enabled
                channels.append(email_channel)
                
            elif channel_type == "webhook":
                webhook_channel = WebhookChannel(
                    name=channel_name,
                    webhook_url=channel_config.get("webhook_url"),
                    method=channel_config.get("method", "POST"),
                    headers=channel_config.get("headers"),
                    payload_template=channel_config.get("payload_template")
                )
                webhook_channel.enabled = enabled
                channels.append(webhook_channel)
                
            elif channel_type == "slack":
                slack_channel = SlackChannel(
                    name=channel_name,
                    webhook_url=channel_config.get("webhook_url"),
                    channel=channel_config.get("channel"),
                    username=channel_config.get("username", "NotificationBot")
                )
                slack_channel.enabled = enabled
                channels.append(slack_channel)
                
            elif channel_type == "teams":
                teams_channel = TeamsChannel(
                    name=channel_name,
                    webhook_url=channel_config.get("webhook_url")
                )
                teams_channel.enabled = enabled
                channels.append(teams_channel)
                
            elif channel_type == "file":
                file_channel = FileChannel(
                    name=channel_name,
                    file_path=channel_config.get("file_path"),
                    append_mode=channel_config.get("append_mode", True),
                    include_timestamp=channel_config.get("include_timestamp", True)
                )
                file_channel.enabled = enabled
                channels.append(file_channel)
                
            else:
                logger.warning(f"Unknown channel type: {channel_type}")
        
        return channels
    
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute the notification logic.
        通知ロジックを実行します。
        
        Args:
            user_input: Notification message / 通知メッセージ
            ctx: Execution context / 実行コンテキスト
            
        Returns:
            Context: Updated context with notification results / 通知結果を含む更新されたコンテキスト
        """
        # Update step info
        # ステップ情報を更新
        ctx.update_step_info(self.name)
        
        try:
            # Determine message to send
            # 送信するメッセージを決定
            message = user_input
            if message is None:
                message = ctx.get_user_input()
            
            if not message:
                logger.warning(f"No message provided for notification in {self.name}")
                message = "Empty notification message"
            
            # Get subject from context or use default
            # コンテキストから件名を取得するか、デフォルトを使用
            subject = ctx.shared_state.get(f"{self.name}_subject", self.config.default_subject)
            
            # Send notifications
            # 通知を送信
            notification_result = await self._send_notifications(message, subject, ctx)
            
            # Store result in context if requested
            # 要求された場合は結果をコンテキストに保存
            if self.config.store_result:
                ctx.shared_state[f"{self.name}_result"] = {
                    "total_channels": notification_result.total_channels,
                    "successful_channels": notification_result.successful_channels,
                    "failed_channels": notification_result.failed_channels,
                    "errors": notification_result.errors,
                    "success_rate": notification_result.success_rate,
                    "timestamp": notification_result.timestamp.isoformat()
                }
            
            # Handle notification failure
            # 通知失敗を処理
            if self.config.require_all_success and not notification_result.is_success:
                error_summary = f"Notification failed: {len(notification_result.failed_channels)} channels failed"
                raise ValueError(error_summary)
            
            if notification_result.is_success:
                logger.info(f"NotificationAgent '{self.name}': All notifications sent successfully")
                ctx.shared_state[f"{self.name}_status"] = "success"
            else:
                logger.warning(f"NotificationAgent '{self.name}': {notification_result.successful_channels}/{notification_result.total_channels} notifications sent")
                ctx.shared_state[f"{self.name}_status"] = "partial_success"
            
            # Store individual channel results for easy access
            # 簡単なアクセスのために個別のチャネル結果を保存
            ctx.shared_state[f"{self.name}_success_count"] = notification_result.successful_channels
            ctx.shared_state[f"{self.name}_total_count"] = notification_result.total_channels
            
            return ctx
            
        except Exception as e:
            logger.error(f"NotificationAgent '{self.name}' error: {e}")
            
            if self.config.store_result:
                ctx.shared_state[f"{self.name}_result"] = {
                    "total_channels": 0,
                    "successful_channels": 0,
                    "failed_channels": [],
                    "errors": [str(e)],
                    "success_rate": 0.0,
                    "timestamp": datetime.now().isoformat()
                }
                ctx.shared_state[f"{self.name}_status"] = "error"
            
            if self.config.require_all_success:
                raise
            
            return ctx
    
    async def _send_notifications(self, message: str, subject: str, context: Context) -> NotificationResult:
        """
        Send notifications through all configured channels.
        設定された全てのチャネルを通じて通知を送信します。
        """
        enabled_channels = [ch for ch in self.notification_channels if ch.enabled]
        result = NotificationResult(total_channels=len(enabled_channels))
        
        for channel in enabled_channels:
            try:
                success = await channel.send(message, subject, context)
                
                if success:
                    result.successful_channels += 1
                    logger.debug(f"Notification sent successfully via {channel.name}")
                else:
                    result.add_error(channel.name, "Channel send method returned False")
                    
                    if self.config.fail_fast:
                        break
                        
            except Exception as e:
                error_message = f"Channel '{channel.name}' execution error: {e}"
                result.add_error(channel.name, error_message)
                logger.warning(error_message)
                
                if self.config.fail_fast:
                    break
        
        return result
    
    def add_channel(self, channel: NotificationChannel):
        """
        Add a notification channel to the agent.
        エージェントに通知チャネルを追加します。
        """
        self.notification_channels.append(channel)
    
    def get_channels(self) -> List[NotificationChannel]:
        """
        Get all notification channels.
        全ての通知チャネルを取得します。
        """
        return self.notification_channels.copy()
    
    def set_subject(self, subject: str, context: Context):
        """
        Set notification subject in context for next notification.
        次の通知用にコンテキストで通知件名を設定します。
        """
        context.shared_state[f"{self.name}_subject"] = subject


# Utility functions for creating common notification agents
# 一般的な通知エージェントを作成するためのユーティリティ関数

def create_log_notifier(name: str = "log_notifier", log_level: str = "INFO") -> NotificationAgent:
    """
    Create a notification agent that logs messages.
    メッセージをログに記録する通知エージェントを作成します。
    """
    config = NotificationConfig(
        name=name,
        channels=[{"type": "log", "name": "log_channel", "log_level": log_level}]
    )
    return NotificationAgent(config)


def create_file_notifier(name: str = "file_notifier", file_path: str = "notifications.log") -> NotificationAgent:
    """
    Create a notification agent that writes to files.
    ファイルに書き込む通知エージェントを作成します。
    """
    config = NotificationConfig(
        name=name,
        channels=[{"type": "file", "name": "file_channel", "file_path": file_path}]
    )
    return NotificationAgent(config)


def create_webhook_notifier(name: str = "webhook_notifier", webhook_url: str = None) -> NotificationAgent:
    """
    Create a notification agent that sends webhooks.
    Webhookを送信する通知エージェントを作成します。
    """
    config = NotificationConfig(
        name=name,
        channels=[{"type": "webhook", "name": "webhook_channel", "webhook_url": webhook_url}]
    )
    return NotificationAgent(config)


def create_slack_notifier(name: str = "slack_notifier", webhook_url: str = None, 
                         channel: str = None) -> NotificationAgent:
    """
    Create a notification agent for Slack.
    Slack用の通知エージェントを作成します。
    """
    config = NotificationConfig(
        name=name,
        channels=[{
            "type": "slack",
            "name": "slack_channel",
            "webhook_url": webhook_url,
            "channel": channel
        }]
    )
    return NotificationAgent(config)


def create_teams_notifier(name: str = "teams_notifier", webhook_url: str = None) -> NotificationAgent:
    """
    Create a notification agent for Microsoft Teams.
    Microsoft Teams用の通知エージェントを作成します。
    """
    config = NotificationConfig(
        name=name,
        channels=[{"type": "teams", "name": "teams_channel", "webhook_url": webhook_url}]
    )
    return NotificationAgent(config)


def create_multi_channel_notifier(name: str = "multi_notifier", 
                                 channels: List[Dict[str, Any]] = None) -> NotificationAgent:
    """
    Create a notification agent with multiple channels.
    複数チャネルを持つ通知エージェントを作成します。
    """
    config = NotificationConfig(
        name=name,
        channels=channels or [
            {"type": "log", "name": "log", "log_level": "INFO"},
            {"type": "file", "name": "file", "file_path": "notifications.log"}
        ]
    )
    return NotificationAgent(config) 

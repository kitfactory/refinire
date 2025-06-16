#!/usr/bin/env python3
"""
Test NotificationAgent implementation.

NotificationAgentの実装をテストします。
"""

import pytest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.agents.notification import (
    NotificationAgent, NotificationConfig, NotificationChannel, NotificationResult,
    LogChannel, EmailChannel, WebhookChannel, SlackChannel, TeamsChannel, FileChannel,
    create_log_notifier, create_file_notifier, create_webhook_notifier,
    create_slack_notifier, create_teams_notifier, create_multi_channel_notifier
)
from refinire import Context


class TestNotificationResult:
    """Test cases for NotificationResult class."""
    
    def test_notification_result_creation(self):
        """Test NotificationResult creation."""
        result = NotificationResult(
            total_channels=5,
            successful_channels=3,
            failed_channels=["channel1", "channel2"],
            errors=["Error 1", "Error 2"]
        )
        
        assert result.total_channels == 5
        assert result.successful_channels == 3
        assert len(result.failed_channels) == 2
        assert len(result.errors) == 2
    
    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        result = NotificationResult(total_channels=4, successful_channels=3)
        assert result.success_rate == 75.0
        
        result = NotificationResult(total_channels=0, successful_channels=0)
        assert result.success_rate == 100.0
    
    def test_is_success_property(self):
        """Test is_success property."""
        result = NotificationResult(total_channels=3, successful_channels=3)
        assert result.is_success == True
        
        result = NotificationResult(total_channels=3, successful_channels=2)
        assert result.is_success == False
    
    def test_add_error(self):
        """Test adding errors."""
        result = NotificationResult()
        result.add_error("test_channel", "Test error")
        
        assert "test_channel" in result.failed_channels
        assert any("Test error" in error for error in result.errors)


class TestLogChannel:
    """Test cases for LogChannel."""
    
    def test_log_channel_creation(self):
        """Test LogChannel creation."""
        channel = LogChannel("test_log", "DEBUG")
        assert channel.name == "test_log"
        assert channel.log_level == "DEBUG"
        assert channel.enabled == True
    
    @pytest.mark.asyncio
    async def test_log_channel_send(self):
        """Test LogChannel send method."""
        channel = LogChannel("test_log", "INFO")
        ctx = Context()
        
        with patch('refinire.agents.notification.logger') as mock_logger:
            result = await channel.send("Test message", "Test subject", ctx)
            
            assert result == True
            mock_logger.info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_log_channel_send_without_subject(self):
        """Test LogChannel send method without subject."""
        channel = LogChannel("test_log", "WARNING")
        ctx = Context()
        
        with patch('refinire.agents.notification.logger') as mock_logger:
            result = await channel.send("Test message", None, ctx)
            
            assert result == True
            mock_logger.warning.assert_called_once()


class TestEmailChannel:
    """Test cases for EmailChannel."""
    
    def test_email_channel_creation(self):
        """Test EmailChannel creation."""
        channel = EmailChannel(
            name="test_email",
            smtp_server="smtp.example.com",
            smtp_port=587,
            username="user@example.com",
            password="password",
            from_email="sender@example.com",
            to_emails=["recipient@example.com"]
        )
        
        assert channel.name == "test_email"
        assert channel.smtp_server == "smtp.example.com"
        assert channel.smtp_port == 587
        assert channel.from_email == "sender@example.com"
        assert len(channel.to_emails) == 1
    
    @pytest.mark.asyncio
    async def test_email_channel_send_success(self):
        """Test EmailChannel send method success."""
        channel = EmailChannel(
            smtp_server="smtp.example.com",
            from_email="sender@example.com",
            to_emails=["recipient@example.com"]
        )
        
        ctx = Context()
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = await channel.send("Test message", "Test subject", ctx)
            
            assert result == True
            mock_server.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_email_channel_send_not_configured(self):
        """Test EmailChannel send method when not configured."""
        channel = EmailChannel()
        ctx = Context()
        
        result = await channel.send("Test message", "Test subject", ctx)
        assert result == False


class TestWebhookChannel:
    """Test cases for WebhookChannel."""
    
    def test_webhook_channel_creation(self):
        """Test WebhookChannel creation."""
        channel = WebhookChannel(
            name="test_webhook",
            webhook_url="https://example.com/webhook",
            method="POST",
            headers={"Authorization": "Bearer token"}
        )
        
        assert channel.name == "test_webhook"
        assert channel.webhook_url == "https://example.com/webhook"
        assert channel.method == "POST"
        assert "Authorization" in channel.headers
    
    @pytest.mark.asyncio
    async def test_webhook_channel_send_success(self):
        """Test WebhookChannel send method success."""
        channel = WebhookChannel(
            webhook_url="https://example.com/webhook"
        )
        
        ctx = Context()
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            result = await channel.send("Test message", "Test subject", ctx)
            
            assert result == True
            mock_urlopen.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_webhook_channel_send_not_configured(self):
        """Test WebhookChannel send method when not configured."""
        channel = WebhookChannel()
        ctx = Context()
        
        result = await channel.send("Test message", "Test subject", ctx)
        assert result == False


class TestSlackChannel:
    """Test cases for SlackChannel."""
    
    def test_slack_channel_creation(self):
        """Test SlackChannel creation."""
        channel = SlackChannel(
            webhook_url="https://hooks.slack.com/services/xxx",
            channel="#general",
            username="TestBot"
        )
        
        assert channel.webhook_url == "https://hooks.slack.com/services/xxx"
        assert "general" in channel.payload_template
        assert "TestBot" in channel.payload_template
    
    @pytest.mark.asyncio
    async def test_slack_channel_send(self):
        """Test SlackChannel send method."""
        channel = SlackChannel(
            webhook_url="https://hooks.slack.com/services/xxx"
        )
        
        ctx = Context()
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_urlopen.return_value.__enter__.return_value = mock_response
            

            
            result = await channel.send("Test message", "Test subject", ctx)
            
            assert result == True


class TestTeamsChannel:
    """Test cases for TeamsChannel."""
    
    def test_teams_channel_creation(self):
        """Test TeamsChannel creation."""
        channel = TeamsChannel(
            webhook_url="https://outlook.office.com/webhook/xxx"
        )
        
        assert channel.webhook_url == "https://outlook.office.com/webhook/xxx"
        assert "MessageCard" in channel.payload_template
    
    @pytest.mark.asyncio
    async def test_teams_channel_send(self):
        """Test TeamsChannel send method."""
        channel = TeamsChannel(
            webhook_url="https://outlook.office.com/webhook/xxx"
        )
        
        ctx = Context()
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_urlopen.return_value.__enter__.return_value = mock_response
            

            
            result = await channel.send("Test message", "Test subject", ctx)
            
            assert result == True


class TestFileChannel:
    """Test cases for FileChannel."""
    
    def test_file_channel_creation(self):
        """Test FileChannel creation."""
        channel = FileChannel(
            name="test_file",
            file_path="test.log",
            append_mode=True,
            include_timestamp=True
        )
        
        assert channel.name == "test_file"
        assert channel.file_path == "test.log"
        assert channel.append_mode == True
        assert channel.include_timestamp == True
    
    @pytest.mark.asyncio
    async def test_file_channel_send(self):
        """Test FileChannel send method."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            channel = FileChannel(
                file_path=temp_path,
                include_timestamp=False
            )
            
            ctx = Context()
            result = await channel.send("Test message", "Test subject", ctx)
            
            assert result == True
            
            # Verify file content
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "Test message" in content
                assert "Test subject" in content
        
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_file_channel_send_with_timestamp(self):
        """Test FileChannel send method with timestamp."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            channel = FileChannel(
                file_path=temp_path,
                include_timestamp=True
            )
            
            ctx = Context()
            result = await channel.send("Test message", None, ctx)
            
            assert result == True
            
            # Verify file content
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "Test message" in content
                # Should have timestamp
                assert len(content.split()) > 2
        
        finally:
            os.unlink(temp_path)


class TestNotificationConfig:
    """Test cases for NotificationConfig class."""
    
    def test_notification_config_creation(self):
        """Test NotificationConfig creation."""
        config = NotificationConfig(
            name="test_notifier",
            channels=[{"type": "log", "name": "log_channel"}],
            default_subject="Test Subject",
            fail_fast=True
        )
        
        assert config.name == "test_notifier"
        assert len(config.channels) == 1
        assert config.default_subject == "Test Subject"
        assert config.fail_fast == True
    
    def test_notification_config_defaults(self):
        """Test NotificationConfig default values."""
        config = NotificationConfig(name="test")
        
        assert config.name == "test"
        assert config.channels == []
        assert config.default_subject == "Notification"
        assert config.fail_fast == False
        assert config.store_result == True
        assert config.require_all_success == False


class TestNotificationAgent:
    """Test cases for NotificationAgent class."""
    
    @pytest.fixture
    def log_config(self):
        """Create log notification configuration."""
        return NotificationConfig(
            name="log_notifier",
            channels=[{"type": "log", "name": "log_channel", "log_level": "INFO"}]
        )
    
    @pytest.fixture
    def multi_config(self):
        """Create multi-channel notification configuration."""
        return NotificationConfig(
            name="multi_notifier",
            channels=[
                {"type": "log", "name": "log1", "log_level": "INFO"},
                {"type": "log", "name": "log2", "log_level": "WARNING"},
                {"type": "file", "name": "file1", "file_path": "test.log"}
            ]
        )
    
    @pytest.mark.asyncio
    async def test_notification_agent_log_channel(self, log_config):
        """Test NotificationAgent with log channel."""
        agent = NotificationAgent(log_config)
        ctx = Context()
        
        with patch('refinire.agents.notification.logger') as mock_logger:
            result_ctx = await agent.run("Test notification", ctx)
            
            assert result_ctx.shared_state["log_notifier_status"] == "success"
            assert result_ctx.shared_state["log_notifier_success_count"] == 1
            assert result_ctx.shared_state["log_notifier_total_count"] == 1
            mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_notification_agent_file_channel(self):
        """Test NotificationAgent with file channel."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            config = NotificationConfig(
                name="file_notifier",
                channels=[{"type": "file", "name": "file_channel", "file_path": temp_path}]
            )
            
            agent = NotificationAgent(config)
            ctx = Context()
            
            result_ctx = await agent.run("Test file notification", ctx)
            
            assert result_ctx.shared_state["file_notifier_status"] == "success"
            
            # Verify file content
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "Test file notification" in content
        
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_notification_agent_webhook_channel(self):
        """Test NotificationAgent with webhook channel."""
        config = NotificationConfig(
            name="webhook_notifier",
            channels=[{"type": "webhook", "name": "webhook_channel", "webhook_url": "https://example.com/webhook"}]
        )
        
        agent = NotificationAgent(config)
        ctx = Context()
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_urlopen.return_value.__enter__.return_value = mock_response
            

            
            result_ctx = await agent.run("Test webhook notification", ctx)
            
            assert result_ctx.shared_state["webhook_notifier_status"] == "success"
            mock_urlopen.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_notification_agent_multi_channel(self, multi_config):
        """Test NotificationAgent with multiple channels."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Update config with actual temp file path
            multi_config.channels[2]["file_path"] = temp_path
            
            agent = NotificationAgent(multi_config)
            ctx = Context()
            
            with patch('refinire.agents.notification.logger') as mock_logger:
                result_ctx = await agent.run("Test multi notification", ctx)
                
                assert result_ctx.shared_state["multi_notifier_status"] == "success"
                assert result_ctx.shared_state["multi_notifier_success_count"] == 3
                assert result_ctx.shared_state["multi_notifier_total_count"] == 3
                
                # Verify log calls
                mock_logger.info.assert_called()
                mock_logger.warning.assert_called()
                
                # Verify file content
                with open(temp_path, 'r') as f:
                    content = f.read()
                    assert "Test multi notification" in content
        
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_notification_agent_custom_subject(self, log_config):
        """Test NotificationAgent with custom subject."""
        agent = NotificationAgent(log_config)
        ctx = Context()
        
        # Set custom subject
        agent.set_subject("Custom Subject", ctx)
        
        with patch('refinire.agents.notification.logger') as mock_logger:
            result_ctx = await agent.run("Test notification", ctx)
            
            assert result_ctx.shared_state["log_notifier_status"] == "success"
            # Check if custom subject was used in log message
            mock_logger.info.assert_called()
            # The custom subject should be in the log channel's call, not the agent's success message
            # Find the log call that contains the notification
            log_calls = [call.args[0] for call in mock_logger.info.call_args_list]
            notification_calls = [call for call in log_calls if "Custom Subject" in call]
            assert len(notification_calls) > 0
    
    @pytest.mark.asyncio
    async def test_notification_agent_fail_fast(self):
        """Test NotificationAgent with fail_fast option."""
        config = NotificationConfig(
            name="fail_fast_notifier",
            channels=[
                {"type": "email", "name": "email1"},  # Will fail (not configured)
                {"type": "log", "name": "log1", "log_level": "INFO"}  # Would succeed
            ],
            fail_fast=True
        )
        
        agent = NotificationAgent(config)
        ctx = Context()
        
        with patch('refinire.agents.notification.logger') as mock_logger:
            result_ctx = await agent.run("Test notification", ctx)
            
            # Should have partial success due to fail_fast
            assert result_ctx.shared_state["fail_fast_notifier_status"] == "partial_success"
            assert result_ctx.shared_state["fail_fast_notifier_success_count"] == 0
            assert result_ctx.shared_state["fail_fast_notifier_total_count"] == 2
    
    @pytest.mark.asyncio
    async def test_notification_agent_require_all_success(self):
        """Test NotificationAgent with require_all_success option."""
        config = NotificationConfig(
            name="require_all_notifier",
            channels=[
                {"type": "email", "name": "email1"},  # Will fail (not configured)
                {"type": "log", "name": "log1", "log_level": "INFO"}
            ],
            require_all_success=True
        )
        
        agent = NotificationAgent(config)
        ctx = Context()
        
        with pytest.raises(ValueError):
            await agent.run("Test notification", ctx)
    
    @pytest.mark.asyncio
    async def test_notification_agent_custom_channels(self):
        """Test NotificationAgent with custom channels."""
        config = NotificationConfig(name="custom_notifier")
        
        # Create custom channel  
        custom_channel = Mock(spec=NotificationChannel)
        custom_channel.name = "custom_channel"
        custom_channel.enabled = True
        
        # Create async mock for send method
        async def mock_send(message, subject, context):
            return True
        custom_channel.send = Mock(side_effect=mock_send)
        
        agent = NotificationAgent(config, [custom_channel])
        ctx = Context()
        
        result_ctx = await agent.run("Test notification", ctx)
        
        assert result_ctx.shared_state["custom_notifier_status"] == "success"
        custom_channel.send.assert_called_once()
    
    def test_notification_agent_add_channel(self, log_config):
        """Test adding channels to NotificationAgent."""
        agent = NotificationAgent(log_config)
        initial_count = len(agent.get_channels())
        
        new_channel = LogChannel("new_log_channel")
        agent.add_channel(new_channel)
        
        assert len(agent.get_channels()) == initial_count + 1
        assert new_channel in agent.get_channels()


class TestNotificationUtilities:
    """Test cases for notification utility functions."""
    
    def test_create_log_notifier(self):
        """Test create_log_notifier utility function."""
        notifier = create_log_notifier("test_log", "DEBUG")
        
        assert notifier.config.name == "test_log"
        channels = notifier.get_channels()
        assert len(channels) == 1
        assert isinstance(channels[0], LogChannel)
        assert channels[0].log_level == "DEBUG"
    
    def test_create_file_notifier(self):
        """Test create_file_notifier utility function."""
        notifier = create_file_notifier("test_file", "test.log")
        
        assert notifier.config.name == "test_file"
        channels = notifier.get_channels()
        assert len(channels) == 1
        assert isinstance(channels[0], FileChannel)
        assert channels[0].file_path == "test.log"
    
    def test_create_webhook_notifier(self):
        """Test create_webhook_notifier utility function."""
        notifier = create_webhook_notifier("test_webhook", "https://example.com/webhook")
        
        assert notifier.config.name == "test_webhook"
        channels = notifier.get_channels()
        assert len(channels) == 1
        assert isinstance(channels[0], WebhookChannel)
        assert channels[0].webhook_url == "https://example.com/webhook"
    
    def test_create_slack_notifier(self):
        """Test create_slack_notifier utility function."""
        notifier = create_slack_notifier("test_slack", "https://hooks.slack.com/xxx", "#general")
        
        assert notifier.config.name == "test_slack"
        channels = notifier.get_channels()
        assert len(channels) == 1
        assert isinstance(channels[0], SlackChannel)
        assert channels[0].webhook_url == "https://hooks.slack.com/xxx"
    
    def test_create_teams_notifier(self):
        """Test create_teams_notifier utility function."""
        notifier = create_teams_notifier("test_teams", "https://outlook.office.com/webhook/xxx")
        
        assert notifier.config.name == "test_teams"
        channels = notifier.get_channels()
        assert len(channels) == 1
        assert isinstance(channels[0], TeamsChannel)
        assert channels[0].webhook_url == "https://outlook.office.com/webhook/xxx"
    
    def test_create_multi_channel_notifier(self):
        """Test create_multi_channel_notifier utility function."""
        custom_channels = [
            {"type": "log", "name": "log1", "log_level": "INFO"},
            {"type": "file", "name": "file1", "file_path": "test.log"}
        ]
        
        notifier = create_multi_channel_notifier("test_multi", custom_channels)
        
        assert notifier.config.name == "test_multi"
        channels = notifier.get_channels()
        assert len(channels) == 2
    
    @pytest.mark.asyncio
    async def test_utility_notifiers_integration(self):
        """Test that utility notifiers work end-to-end."""
        # Test log notifier
        log_notifier = create_log_notifier("log_test", "INFO")
        ctx = Context()
        
        with patch('refinire.agents.notification.logger') as mock_logger:
            result_ctx = await log_notifier.run("Test log message", ctx)
            assert result_ctx.shared_state["log_test_status"] == "success"
            mock_logger.info.assert_called()
        
        # Test file notifier
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            file_notifier = create_file_notifier("file_test", temp_path)
            ctx = Context()
            
            result_ctx = await file_notifier.run("Test file message", ctx)
            assert result_ctx.shared_state["file_test_status"] == "success"
            
            with open(temp_path, 'r') as f:
                content = f.read()
                assert "Test file message" in content
        
        finally:
            os.unlink(temp_path)
        
        # Test webhook notifier
        webhook_notifier = create_webhook_notifier("webhook_test", "https://example.com/webhook")
        ctx = Context()
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_urlopen.return_value.__enter__.return_value = mock_response
            

            
            result_ctx = await webhook_notifier.run("Test webhook message", ctx)
            assert result_ctx.shared_state["webhook_test_status"] == "success"
            mock_urlopen.assert_called_once() 

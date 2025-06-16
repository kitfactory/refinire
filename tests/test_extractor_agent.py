#!/usr/bin/env python3
"""
Test ExtractorAgent implementation.

ExtractorAgentの実装をテストします。
"""

import pytest
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.agents.extractor import (
    ExtractorAgent, ExtractorConfig, ExtractionRule, ExtractionResult,
    RegexExtractionRule, EmailExtractionRule, PhoneExtractionRule, URLExtractionRule,
    DateExtractionRule, HTMLExtractionRule, JSONExtractionRule, LLMExtractionRule,
    CustomFunctionExtractionRule, SimpleHTMLParser,
    create_contact_extractor, create_html_extractor, create_json_extractor
)
from refinire import Context


class TestExtractionRules:
    """Test cases for individual extraction rules."""
    
    def test_regex_extraction_rule_single(self):
        """Test RegexExtractionRule with single match."""
        rule = RegexExtractionRule("test_regex", r"\d{3}-\d{3}-\d{4}", multiple=False)
        ctx = Context()
        
        result = rule.extract("Call me at 123-456-7890 for details", ctx)
        assert result == "123-456-7890"
        
        result = rule.extract("No phone number here", ctx)
        assert result is None
    
    def test_regex_extraction_rule_multiple(self):
        """Test RegexExtractionRule with multiple matches."""
        rule = RegexExtractionRule("test_regex", r"\d+", multiple=True)
        ctx = Context()
        
        result = rule.extract("Numbers: 123, 456, 789", ctx)
        assert result == ["123", "456", "789"]
        
        result = rule.extract("No numbers here", ctx)
        assert result == []
    
    def test_email_extraction_rule(self):
        """Test EmailExtractionRule."""
        rule = EmailExtractionRule("email_extractor")
        ctx = Context()
        
        text = "Contact us at support@example.com or admin@test.org"
        result = rule.extract(text, ctx)
        assert "support@example.com" in result
        assert "admin@test.org" in result
        
        result = rule.extract("No emails here", ctx)
        assert result == []
    
    def test_phone_extraction_rule(self):
        """Test PhoneExtractionRule."""
        rule = PhoneExtractionRule("phone_extractor")
        ctx = Context()
        
        text = "Call 123-456-7890 or (555) 123-4567"
        result = rule.extract(text, ctx)
        assert len(result) >= 1  # Should find at least one phone number
    
    def test_url_extraction_rule(self):
        """Test URLExtractionRule."""
        rule = URLExtractionRule("url_extractor")
        ctx = Context()
        
        text = "Visit https://example.com or http://test.org for more info"
        result = rule.extract(text, ctx)
        assert "https://example.com" in result
        assert "http://test.org" in result
        
        result = rule.extract("No URLs here", ctx)
        assert result == []
    
    def test_date_extraction_rule(self):
        """Test DateExtractionRule."""
        rule = DateExtractionRule("date_extractor")
        ctx = Context()
        
        text = "Meeting on 2023-12-25 or 01/15/2024"
        result = rule.extract(text, ctx)
        assert len(result) >= 1  # Should find at least one date
    
    def test_html_extraction_rule_text(self):
        """Test HTMLExtractionRule for text extraction."""
        rule = HTMLExtractionRule("title_extractor", tag="title", multiple=False)
        ctx = Context()
        
        html = "<html><head><title>Test Page</title></head><body>Content</body></html>"
        result = rule.extract(html, ctx)
        assert result == "Test Page"
    
    def test_html_extraction_rule_multiple(self):
        """Test HTMLExtractionRule for multiple elements."""
        rule = HTMLExtractionRule("link_extractor", tag="a", multiple=True)
        ctx = Context()
        
        html = '''
        <html>
        <body>
            <a>Link 1</a>
            <a>Link 2</a>
            <a>Link 3</a>
        </body>
        </html>
        '''
        result = rule.extract(html, ctx)
        assert "Link 1" in result
        assert "Link 2" in result
        assert "Link 3" in result
    
    def test_html_extraction_rule_attribute(self):
        """Test HTMLExtractionRule for attribute extraction."""
        rule = HTMLExtractionRule("href_extractor", tag="a", attribute="href", multiple=True)
        ctx = Context()
        
        html = '''
        <html>
        <body>
            <a href="http://example.com">Link 1</a>
            <a href="http://test.org">Link 2</a>
        </body>
        </html>
        '''
        result = rule.extract(html, ctx)
        assert "http://example.com" in result
        assert "http://test.org" in result
    
    def test_json_extraction_rule_simple(self):
        """Test JSONExtractionRule with simple path."""
        rule = JSONExtractionRule("name_extractor", "user.name", multiple=False)
        ctx = Context()
        
        json_data = '{"user": {"name": "John Doe", "age": 30}}'
        result = rule.extract(json_data, ctx)
        assert result == "John Doe"
    
    def test_json_extraction_rule_wildcard(self):
        """Test JSONExtractionRule with wildcard."""
        rule = JSONExtractionRule("name_extractor", "users.*.name", multiple=True)
        ctx = Context()
        
        json_data = '''
        {
            "users": [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25}
            ]
        }
        '''
        result = rule.extract(json_data, ctx)
        assert "John" in result
        assert "Jane" in result
    
    def test_json_extraction_rule_nested(self):
        """Test JSONExtractionRule with nested path."""
        rule = JSONExtractionRule("city_extractor", "user.address.city", multiple=False)
        ctx = Context()
        
        json_data = '''
        {
            "user": {
                "name": "John",
                "address": {
                    "city": "New York",
                    "state": "NY"
                }
            }
        }
        '''
        result = rule.extract(json_data, ctx)
        assert result == "New York"
    
    def test_custom_function_extraction_rule(self):
        """Test CustomFunctionExtractionRule."""
        def extract_numbers(data, context):
            import re
            numbers = re.findall(r'\d+', data)
            return [int(n) for n in numbers]
        
        rule = CustomFunctionExtractionRule("number_extractor", extract_numbers)
        ctx = Context()
        
        result = rule.extract("I have 5 apples and 10 oranges", ctx)
        assert result == [5, 10]


class TestSimpleHTMLParser:
    """Test cases for SimpleHTMLParser."""
    
    def test_simple_html_parser_text(self):
        """Test SimpleHTMLParser for text extraction."""
        parser = SimpleHTMLParser("title")
        html = "<html><head><title>Test Title</title></head></html>"
        parser.feed(html)
        
        assert parser.results == ["Test Title"]
    
    def test_simple_html_parser_attribute(self):
        """Test SimpleHTMLParser for attribute extraction."""
        parser = SimpleHTMLParser("a", "href")
        html = '<a href="http://example.com">Link</a>'
        parser.feed(html)
        
        assert parser.results == ["http://example.com"]
    
    def test_simple_html_parser_multiple(self):
        """Test SimpleHTMLParser for multiple elements."""
        parser = SimpleHTMLParser("p")
        html = "<div><p>Para 1</p><p>Para 2</p></div>"
        parser.feed(html)
        
        assert "Para 1" in parser.results
        assert "Para 2" in parser.results


class TestExtractionResult:
    """Test cases for ExtractionResult class."""
    
    def test_extraction_result_success(self):
        """Test ExtractionResult with successful extraction."""
        data = {"emails": ["test@example.com"], "phones": ["123-456-7890"]}
        result = ExtractionResult(data)
        
        assert result.success == True
        assert len(result.errors) == 0
        assert result.get_extracted("emails") == ["test@example.com"]
    
    def test_extraction_result_with_errors(self):
        """Test ExtractionResult with errors."""
        result = ExtractionResult({}, success=False, errors=["Error 1"])
        result.add_error("Error 2")
        
        assert result.success == False
        assert len(result.errors) == 2
        assert "Error 1" in result.errors
        assert "Error 2" in result.errors
    
    def test_extraction_result_with_warnings(self):
        """Test ExtractionResult with warnings."""
        result = ExtractionResult({"data": "value"})
        result.add_warning("Warning message")
        
        assert result.success == True
        assert len(result.warnings) == 1
        assert "Warning message" in result.warnings


class TestExtractorConfig:
    """Test cases for ExtractorConfig class."""
    
    def test_extractor_config_creation(self):
        """Test ExtractorConfig creation."""
        config = ExtractorConfig(
            name="test_extractor",
            rules=[{"type": "email", "name": "email_rule"}],
            input_format="text"
        )
        
        assert config.name == "test_extractor"
        assert len(config.rules) == 1
        assert config.input_format == "text"
    
    def test_extractor_config_defaults(self):
        """Test ExtractorConfig default values."""
        config = ExtractorConfig(name="test")
        
        assert config.name == "test"
        assert config.rules == []
        assert config.input_format == "auto"
        assert config.store_result == True
        assert config.fail_on_error == False
    
    def test_extractor_config_validation(self):
        """Test ExtractorConfig validation."""
        with pytest.raises(ValueError):
            ExtractorConfig(name="test", input_format="invalid")


class TestExtractorAgent:
    """Test cases for ExtractorAgent class."""
    
    @pytest.fixture
    def contact_extractor_config(self):
        """Create contact extractor configuration."""
        return ExtractorConfig(
            name="contact_extractor",
            rules=[
                {"type": "email", "name": "emails"},
                {"type": "phone", "name": "phones"},
                {"type": "url", "name": "urls"}
            ]
        )
    
    @pytest.fixture
    def html_extractor_config(self):
        """Create HTML extractor configuration."""
        return ExtractorConfig(
            name="html_extractor",
            rules=[
                {"type": "html", "name": "titles", "tag": "title", "multiple": False},
                {"type": "html", "name": "links", "tag": "a", "multiple": True}
            ]
        )
    
    @pytest.fixture
    def json_extractor_config(self):
        """Create JSON extractor configuration."""
        return ExtractorConfig(
            name="json_extractor",
            rules=[
                {"type": "json", "name": "name", "path": "user.name", "multiple": False},
                {"type": "json", "name": "emails", "path": "user.emails.*", "multiple": True}
            ]
        )
    
    @pytest.mark.asyncio
    async def test_extractor_agent_contact_extraction(self, contact_extractor_config):
        """Test ExtractorAgent with contact information."""
        extractor = ExtractorAgent(contact_extractor_config)
        ctx = Context()
        
        text = """
        Contact Information:
        Email: support@example.com, admin@test.org
        Phone: 123-456-7890
        Website: https://example.com
        """
        
        result_ctx = await extractor.run(text, ctx)
        
        assert result_ctx.shared_state["contact_extractor_status"] == "success"
        
        # Check extracted emails
        emails = result_ctx.shared_state.get("contact_extractor_emails", [])
        assert isinstance(emails, list)
        assert "support@example.com" in emails
        
        # Check extracted URLs
        urls = result_ctx.shared_state.get("contact_extractor_urls", [])
        assert isinstance(urls, list)
        assert "https://example.com" in urls
    
    @pytest.mark.asyncio
    async def test_extractor_agent_html_extraction(self, html_extractor_config):
        """Test ExtractorAgent with HTML content."""
        extractor = ExtractorAgent(html_extractor_config)
        ctx = Context()
        
        html_content = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <a>Link 1</a>
            <a>Link 2</a>
        </body>
        </html>
        """
        
        result_ctx = await extractor.run(html_content, ctx)
        
        assert result_ctx.shared_state["html_extractor_status"] == "success"
        
        # Check extracted title
        title = result_ctx.shared_state.get("html_extractor_titles")
        assert title == "Test Page"
        
        # Check extracted links
        links = result_ctx.shared_state.get("html_extractor_links", [])
        assert "Link 1" in links
        assert "Link 2" in links
    
    @pytest.mark.asyncio
    async def test_extractor_agent_json_extraction(self, json_extractor_config):
        """Test ExtractorAgent with JSON content."""
        extractor = ExtractorAgent(json_extractor_config)
        ctx = Context()
        
        json_content = '''
        {
            "user": {
                "name": "John Doe",
                "emails": ["john@example.com", "john.doe@test.org"]
            }
        }
        '''
        
        result_ctx = await extractor.run(json_content, ctx)
        
        assert result_ctx.shared_state["json_extractor_status"] == "success"
        
        # Check extracted name
        name = result_ctx.shared_state.get("json_extractor_name")
        assert name == "John Doe"
        
        # Check extracted emails
        emails = result_ctx.shared_state.get("json_extractor_emails", [])
        assert "john@example.com" in emails
        assert "john.doe@test.org" in emails
    
    @pytest.mark.asyncio
    async def test_extractor_agent_custom_rules(self):
        """Test ExtractorAgent with custom extraction rules."""
        def extract_hashtags(data, context):
            import re
            return re.findall(r'#\w+', data)
        
        config = ExtractorConfig(name="social_extractor")
        custom_rule = CustomFunctionExtractionRule("hashtags", extract_hashtags)
        extractor = ExtractorAgent(config, [custom_rule])
        
        ctx = Context()
        text = "Love this #awesome #python #coding tutorial!"
        
        result_ctx = await extractor.run(text, ctx)
        
        assert result_ctx.shared_state["social_extractor_status"] == "success"
        hashtags = result_ctx.shared_state.get("social_extractor_hashtags", [])
        assert "#awesome" in hashtags
        assert "#python" in hashtags
        assert "#coding" in hashtags
    
    @pytest.mark.asyncio
    async def test_extractor_agent_fail_on_error(self):
        """Test ExtractorAgent with fail_on_error option."""
        config = ExtractorConfig(
            name="failing_extractor",
            rules=[{"type": "invalid_type", "name": "invalid_rule"}],
            fail_on_error=True
        )
        extractor = ExtractorAgent(config)
        ctx = Context()
        
        # Should not raise exception, but should log warning
        result_ctx = await extractor.run("test data", ctx)
        
        # Should complete but with warnings about unknown rule type
        assert "failing_extractor_status" in result_ctx.shared_state
    
    def test_extractor_agent_add_rule(self):
        """Test adding extraction rules to ExtractorAgent."""
        config = ExtractorConfig(name="test_extractor")
        extractor = ExtractorAgent(config)
        
        initial_count = len(extractor.get_rules())
        
        new_rule = EmailExtractionRule("new_email_rule")
        extractor.add_rule(new_rule)
        
        assert len(extractor.get_rules()) == initial_count + 1
        assert new_rule in extractor.get_rules()


class TestExtractorUtilities:
    """Test cases for extractor utility functions."""
    
    def test_create_contact_extractor(self):
        """Test create_contact_extractor utility function."""
        extractor = create_contact_extractor("test_contact")
        
        assert extractor.name == "test_contact"
        rules = extractor.get_rules()
        rule_names = [rule.name for rule in rules]
        assert "emails" in rule_names
        assert "phones" in rule_names
        assert "urls" in rule_names
    
    def test_create_html_extractor(self):
        """Test create_html_extractor utility function."""
        tags = {"titles": "title", "paragraphs": "p"}
        extractor = create_html_extractor("test_html", tags)
        
        assert extractor.name == "test_html"
        rules = extractor.get_rules()
        assert len(rules) == 2
    
    def test_create_json_extractor(self):
        """Test create_json_extractor utility function."""
        paths = {"name": "user.name", "email": "user.email"}
        extractor = create_json_extractor("test_json", paths)
        
        assert extractor.name == "test_json"
        rules = extractor.get_rules()
        assert len(rules) == 2
    
    @pytest.mark.asyncio
    async def test_utility_extractors_integration(self):
        """Test that utility extractors work end-to-end."""
        # Test contact extractor
        contact_extractor = create_contact_extractor()
        ctx = Context()
        
        text = "Contact: admin@example.com, https://example.com"
        result_ctx = await contact_extractor.run(text, ctx)
        assert result_ctx.shared_state["contact_extractor_status"] == "success"
        
        # Test HTML extractor
        html_extractor = create_html_extractor("html_test", {"titles": "title"})
        html = "<html><head><title>Test</title></head></html>"
        ctx = Context()
        
        result_ctx = await html_extractor.run(html, ctx)
        assert result_ctx.shared_state["html_test_status"] == "success"
        
        # Test JSON extractor
        json_extractor = create_json_extractor("json_test", {"name": "user.name"})
        json_data = '{"user": {"name": "John"}}'
        ctx = Context()
        
        result_ctx = await json_extractor.run(json_data, ctx)
        assert result_ctx.shared_state["json_test_status"] == "success" 

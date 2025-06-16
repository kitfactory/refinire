#!/usr/bin/env python3
"""
ExtractorAgent Examples
ExtractorAgentの使用例

This example demonstrates how to use ExtractorAgent for information extraction
from various types of unstructured data including text, HTML, and JSON.
この例では、テキスト、HTML、JSONなどの様々な非構造化データから
情報抽出を行うためにExtractorAgentを使用する方法を示します。
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire.agents.extractor import (
    ExtractorAgent, ExtractorConfig, ExtractionRule,
    RegexExtractionRule, EmailExtractionRule, PhoneExtractionRule, URLExtractionRule,
    HTMLExtractionRule, JSONExtractionRule, CustomFunctionExtractionRule,
    create_contact_extractor, create_html_extractor, create_json_extractor
)
from refinire.flow.context import Context


async def example_1_contact_extraction():
    """
    Example 1: Extract contact information from text.
    例1: テキストから連絡先情報を抽出。
    """
    print("\n" + "="*60)
    print("Example 1: Contact Information Extraction")
    print("例1: 連絡先情報抽出")
    print("="*60)
    
    # Create contact extractor using utility function
    # ユーティリティ関数を使って連絡先エクストラクターを作成
    contact_extractor = create_contact_extractor("contact_info")
    
    # Sample business card text
    # 名刺テキストのサンプル
    business_card_text = """
    John Smith
    Senior Software Engineer
    
    Tech Solutions Inc.
    Email: john.smith@techsolutions.com
    Personal: j.smith@gmail.com
    Phone: (555) 123-4567
    Mobile: +1-555-987-6543
    
    Website: https://www.techsolutions.com
    LinkedIn: https://linkedin.com/in/johnsmith
    GitHub: https://github.com/johnsmith
    
    Address: 123 Tech Street, Silicon Valley, CA 94025
    """
    
    print("Extracting from business card text:")
    print("名刺テキストから抽出中:")
    print(f"Input text length: {len(business_card_text)} characters")
    
    ctx = Context()
    result_ctx = await contact_extractor.run(business_card_text, ctx)
    
    status = result_ctx.shared_state.get("contact_info_status")
    print(f"\nExtraction status: {status}")
    
    # Display extracted information
    # 抽出された情報を表示
    emails = result_ctx.shared_state.get("contact_info_emails", [])
    phones = result_ctx.shared_state.get("contact_info_phones", [])
    urls = result_ctx.shared_state.get("contact_info_urls", [])
    
    print(f"\nExtracted emails ({len(emails)}):")
    for email in emails:
        print(f"  - {email}")
    
    print(f"\nExtracted phone numbers ({len(phones)}):")
    for phone in phones:
        print(f"  - {phone}")
    
    print(f"\nExtracted URLs ({len(urls)}):")
    for url in urls:
        print(f"  - {url}")


async def example_2_html_extraction():
    """
    Example 2: Extract information from HTML content.
    例2: HTMLコンテンツから情報を抽出。
    """
    print("\n" + "="*60)
    print("Example 2: HTML Content Extraction")
    print("例2: HTMLコンテンツ抽出")
    print("="*60)
    
    # Create HTML extractor for common web page elements
    # 一般的なWebページ要素用のHTMLエクストラクターを作成
    html_extractor = create_html_extractor("webpage_info", {
        "title": "title",
        "headings": "h1",
        "paragraphs": "p",
        "links": "a"
    })
    
    # Sample HTML content
    # HTMLコンテンツのサンプル
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Company News - Tech Solutions Inc.</title>
    </head>
    <body>
        <h1>Latest Company Updates</h1>
        <h1>Product Launches</h1>
        
        <p>We are excited to announce our new AI-powered analytics platform.</p>
        <p>This revolutionary tool will help businesses make data-driven decisions.</p>
        <p>Contact our sales team for more information about pricing and features.</p>
        
        <a href="https://example.com/products">View Products</a>
        <a href="https://example.com/contact">Contact Sales</a>
        <a href="https://example.com/support">Get Support</a>
    </body>
    </html>
    """
    
    print("Extracting from HTML content:")
    print("HTMLコンテンツから抽出中:")
    
    ctx = Context()
    result_ctx = await html_extractor.run(html_content, ctx)
    
    status = result_ctx.shared_state.get("webpage_info_status")
    print(f"\nExtraction status: {status}")
    
    # Display extracted information
    # 抽出された情報を表示
    title = result_ctx.shared_state.get("webpage_info_title")
    headings = result_ctx.shared_state.get("webpage_info_headings", [])
    paragraphs = result_ctx.shared_state.get("webpage_info_paragraphs", [])
    links = result_ctx.shared_state.get("webpage_info_links", [])
    
    print(f"\nPage title: {title}")
    
    print(f"\nHeadings ({len(headings)}):")
    for i, heading in enumerate(headings, 1):
        print(f"  {i}. {heading}")
    
    print(f"\nParagraphs ({len(paragraphs)}):")
    for i, para in enumerate(paragraphs, 1):
        print(f"  {i}. {para[:100]}{'...' if len(para) > 100 else ''}")
    
    print(f"\nLinks ({len(links)}):")
    for i, link in enumerate(links, 1):
        print(f"  {i}. {link}")


async def example_3_json_extraction():
    """
    Example 3: Extract information from JSON data.
    例3: JSONデータから情報を抽出。
    """
    print("\n" + "="*60)
    print("Example 3: JSON Data Extraction")
    print("例3: JSONデータ抽出")
    print("="*60)
    
    # Create JSON extractor for user profile data
    # ユーザープロファイルデータ用のJSONエクストラクターを作成
    json_extractor = create_json_extractor("user_profile", {
        "name": "profile.name",
        "email": "profile.contact.email",
        "skills": "profile.skills.*",
        "projects": "profile.projects.*.name"
    })
    
    # Sample JSON data
    # JSONデータのサンプル
    json_data = """
    {
        "profile": {
            "id": 12345,
            "name": "Alice Johnson",
            "contact": {
                "email": "alice.johnson@example.com",
                "phone": "+1-555-234-5678"
            },
            "skills": ["Python", "JavaScript", "Machine Learning", "Data Analysis"],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "status": "completed",
                    "technologies": ["React", "Node.js", "MongoDB"]
                },
                {
                    "name": "Analytics Dashboard",
                    "status": "in-progress",
                    "technologies": ["Python", "Pandas", "Plotly"]
                },
                {
                    "name": "Mobile App",
                    "status": "planning",
                    "technologies": ["React Native", "Firebase"]
                }
            ]
        }
    }
    """
    
    print("Extracting from JSON profile data:")
    print("JSONプロファイルデータから抽出中:")
    
    ctx = Context()
    result_ctx = await json_extractor.run(json_data, ctx)
    
    status = result_ctx.shared_state.get("user_profile_status")
    print(f"\nExtraction status: {status}")
    
    # Display extracted information
    # 抽出された情報を表示
    name = result_ctx.shared_state.get("user_profile_name")
    email = result_ctx.shared_state.get("user_profile_email")
    skills = result_ctx.shared_state.get("user_profile_skills", [])
    projects = result_ctx.shared_state.get("user_profile_projects", [])
    
    print(f"\nUser name: {name}")
    print(f"Email: {email}")
    
    print(f"\nSkills ({len(skills)}):")
    for skill in skills:
        print(f"  - {skill}")
    
    print(f"\nProjects ({len(projects)}):")
    for project in projects:
        print(f"  - {project}")


async def example_4_custom_extraction():
    """
    Example 4: Custom extraction rules with business logic.
    例4: ビジネスロジックを持つカスタム抽出ルール。
    """
    print("\n" + "="*60)
    print("Example 4: Custom Extraction Rules")
    print("例4: カスタム抽出ルール")
    print("="*60)
    
    # Define custom extraction functions
    # カスタム抽出関数を定義
    def extract_hashtags(text, context):
        """Extract hashtags from social media text."""
        import re
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    
    def extract_mentions(text, context):
        """Extract user mentions from social media text."""
        import re
        mentions = re.findall(r'@\w+', text)
        return mentions
    
    def extract_prices(text, context):
        """Extract price information."""
        import re
        # Pattern for prices like $99.99, $1,234.56, etc.
        price_pattern = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        prices = re.findall(price_pattern, text)
        return prices
    
    # Create extractor with custom rules
    # カスタムルールを持つエクストラクターを作成
    config = ExtractorConfig(name="social_media_extractor")
    
    custom_rules = [
        CustomFunctionExtractionRule("hashtags", extract_hashtags),
        CustomFunctionExtractionRule("mentions", extract_mentions),
        CustomFunctionExtractionRule("prices", extract_prices)
    ]
    
    social_extractor = ExtractorAgent(config, custom_rules)
    
    # Sample social media posts
    # ソーシャルメディア投稿のサンプル
    social_posts = [
        "Just bought the new #iPhone for $999.99! Thanks @Apple for the amazing #technology #innovation",
        "Great deal on #Python courses! Only $49.99 this week. Check it out @CodeAcademy #programming #learning",
        "Lunch with @friend_name at the new restaurant. Cost us $45.50 total. #foodie #lunch #downtown"
    ]
    
    for i, post in enumerate(social_posts, 1):
        print(f"\nAnalyzing post {i}:")
        print(f"投稿{i}を分析中:")
        print(f"Text: {post}")
        
        ctx = Context()
        result_ctx = await social_extractor.run(post, ctx)
        
        hashtags = result_ctx.shared_state.get("social_media_extractor_hashtags", [])
        mentions = result_ctx.shared_state.get("social_media_extractor_mentions", [])
        prices = result_ctx.shared_state.get("social_media_extractor_prices", [])
        
        print(f"  Hashtags: {hashtags}")
        print(f"  Mentions: {mentions}")
        print(f"  Prices: {prices}")


async def example_5_regex_patterns():
    """
    Example 5: Advanced regex pattern extraction.
    例5: 高度な正規表現パターン抽出。
    """
    print("\n" + "="*60)
    print("Example 5: Advanced Regex Pattern Extraction")
    print("例5: 高度な正規表現パターン抽出")
    print("="*60)
    
    # Create extractor with specific regex patterns
    # 特定の正規表現パターンを持つエクストラクターを作成
    config = ExtractorConfig(
        name="document_extractor",
        rules=[
            {
                "type": "regex",
                "name": "credit_cards",
                "pattern": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
                "multiple": True
            },
            {
                "type": "regex", 
                "name": "ssn",
                "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
                "multiple": True
            },
            {
                "type": "regex",
                "name": "ip_addresses",
                "pattern": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
                "multiple": True
            },
            {
                "type": "regex",
                "name": "invoice_numbers",
                "pattern": r"INV-\d{6}",
                "multiple": True
            }
        ]
    )
    
    document_extractor = ExtractorAgent(config)
    
    # Sample document text
    # 文書テキストのサンプル
    document_text = """
    CONFIDENTIAL BUSINESS DOCUMENT
    
    Customer Payment Information:
    Credit Card: 4532-1234-5678-9012
    Backup Card: 5432 9876 5432 1098
    
    Employee Records:
    John Doe - SSN: 123-45-6789
    Jane Smith - SSN: 987-65-4321
    
    System Information:
    Database Server: 192.168.1.100
    Web Server: 10.0.0.50
    Load Balancer: 172.16.0.1
    
    Invoice References:
    Order #1: INV-123456
    Order #2: INV-789012
    Order #3: INV-345678
    """
    
    print("Extracting sensitive information from document:")
    print("文書から機密情報を抽出中:")
    print(f"Document length: {len(document_text)} characters")
    
    ctx = Context()
    result_ctx = await document_extractor.run(document_text, ctx)
    
    status = result_ctx.shared_state.get("document_extractor_status")
    print(f"\nExtraction status: {status}")
    
    # Display extracted information (masked for security)
    # 抽出された情報を表示（セキュリティのためマスク）
    credit_cards = result_ctx.shared_state.get("document_extractor_credit_cards", [])
    ssns = result_ctx.shared_state.get("document_extractor_ssn", [])
    ips = result_ctx.shared_state.get("document_extractor_ip_addresses", [])
    invoices = result_ctx.shared_state.get("document_extractor_invoice_numbers", [])
    
    print(f"\nCredit Cards found ({len(credit_cards)}):")
    for cc in credit_cards:
        masked = cc[:4] + "-****-****-" + cc[-4:]
        print(f"  - {masked}")
    
    print(f"\nSSN found ({len(ssns)}):")
    for ssn in ssns:
        masked = "***-**-" + ssn[-4:]
        print(f"  - {masked}")
    
    print(f"\nIP Addresses ({len(ips)}):")
    for ip in ips:
        print(f"  - {ip}")
    
    print(f"\nInvoice Numbers ({len(invoices)}):")
    for inv in invoices:
        print(f"  - {inv}")


async def example_6_mixed_content_extraction():
    """
    Example 6: Extract from mixed content types.
    例6: 混在コンテンツタイプからの抽出。
    """
    print("\n" + "="*60)
    print("Example 6: Mixed Content Type Extraction")
    print("例6: 混在コンテンツタイプ抽出")
    print("="*60)
    
    # Create comprehensive extractor
    # 包括的なエクストラクターを作成
    config = ExtractorConfig(
        name="comprehensive_extractor",
        rules=[
            {"type": "email", "name": "emails"},
            {"type": "phone", "name": "phones"},
            {"type": "url", "name": "urls"},
            {"type": "date", "name": "dates"},
            {"type": "html", "name": "html_links", "tag": "a", "multiple": True},
            {"type": "json", "name": "user_names", "path": "users.*.name", "multiple": True}
        ]
    )
    
    comprehensive_extractor = ExtractorAgent(config)
    
    # Mixed content sample
    # 混在コンテンツのサンプル
    mixed_content = """
    Meeting Report - 2024-01-15
    
    Attendees:
    - John Smith (john.smith@company.com, 555-123-4567)
    - Jane Doe (jane.doe@company.com, 555-987-6543)
    
    Next meeting: 2024-01-22
    
    Resources:
    Website: https://company.com/projects
    Documentation: https://docs.company.com
    
    HTML snippet from email:
    <html>
    <body>
        <a href="https://calendar.company.com">Calendar</a>
        <a href="https://tasks.company.com">Tasks</a>
    </body>
    </html>
    
    User data (JSON):
    {
        "users": [
            {"name": "Alice Johnson", "role": "developer"},
            {"name": "Bob Wilson", "role": "designer"},
            {"name": "Carol Brown", "role": "manager"}
        ]
    }
    """
    
    print("Extracting from mixed content:")
    print("混在コンテンツから抽出中:")
    
    ctx = Context()
    result_ctx = await comprehensive_extractor.run(mixed_content, ctx)
    
    status = result_ctx.shared_state.get("comprehensive_extractor_status")
    print(f"\nExtraction status: {status}")
    
    # Display all extracted information
    # 全ての抽出された情報を表示
    extraction_types = [
        ("emails", "Email addresses"),
        ("phones", "Phone numbers"),
        ("urls", "URLs"),
        ("dates", "Dates"),
        ("html_links", "HTML links"),
        ("user_names", "User names from JSON")
    ]
    
    for key, description in extraction_types:
        data = result_ctx.shared_state.get(f"comprehensive_extractor_{key}", [])
        print(f"\n{description} ({len(data) if isinstance(data, list) else 1 if data else 0}):")
        if isinstance(data, list):
            for item in data:
                print(f"  - {item}")
        else:
            if data:
                print(f"  - {data}")


async def main():
    """
    Main function to run all examples.
    全ての例を実行するメイン関数。
    """
    print("ExtractorAgent Examples")
    print("ExtractorAgent使用例")
    print("=" * 80)
    
    examples = [
        example_1_contact_extraction,
        example_2_html_extraction,
        example_3_json_extraction,
        example_4_custom_extraction,
        example_5_regex_patterns,
        example_6_mixed_content_extraction
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
            print(f"エラー in {example.__name__}: {e}")
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("全ての例が完了しました！")


if __name__ == "__main__":
    asyncio.run(main()) 

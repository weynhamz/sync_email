#!/usr/bin/env python3
"""
Gmail Search Demo - Shows how Gmail vs standard search is selected
"""

from sync_mail import is_gmail_server


def demo_search_selection():
    """Demonstrate search method selection logic."""
    print("🔍 Gmail Search vs Standard IMAP Search Demo")
    print("=" * 55)
    
    # Test different server configurations
    test_configs = [
        {
            "name": "Gmail with Gmail Query",
            "server": "imap.gmail.com",
            "criteria": {
                "gmail_query": "from:sender@example.com after:2024/1/1 -label:spam",
                "subject": "Test Email",
                "from": "sender@example.com"
            }
        },
        {
            "name": "Gmail without Gmail Query", 
            "server": "imap.gmail.com",
            "criteria": {
                "subject": "Test Email",
                "from": "sender@example.com",
                "date_after": "01-Jan-2024"
            }
        },
        {
            "name": "Outlook with Mixed Criteria",
            "server": "imap.outlook.com",
            "criteria": {
                "gmail_query": "from:sender@example.com after:2024/1/1",  # Will be ignored
                "subject": "Test Email", 
                "from": "sender@example.com",
                "date_after": "01-Jan-2024"
            }
        },
        {
            "name": "Yahoo Standard Search",
            "server": "imap.mail.yahoo.com",
            "criteria": {
                "subject": "Newsletter",
                "from": "news@company.com",
                "body": "unsubscribe"
            }
        }
    ]
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n{i}. {config['name']}")
        print(f"   Server: {config['server']}")
        print(f"   Is Gmail: {is_gmail_server(config['server'])}")
        
        criteria = config['criteria']
        server = config['server']
        
        # Determine search method (same logic as in sync_mail.py)
        is_gmail = is_gmail_server(server)
        has_gmail_query = 'gmail_query' in criteria
        
        if is_gmail and has_gmail_query:
            print(f"   🚀 Will use Gmail search: {criteria['gmail_query']}")
            print(f"   📝 Gmail query will take precedence")
        else:
            # Build standard IMAP search
            search_terms = []
            if 'subject' in criteria:
                search_terms.append(f'SUBJECT "{criteria["subject"]}"')
            if 'from' in criteria:
                search_terms.append(f'FROM "{criteria["from"]}"')
            if 'date_after' in criteria:
                search_terms.append(f'SINCE "{criteria["date_after"]}"')
            if 'body' in criteria:
                search_terms.append(f'BODY "{criteria["body"]}"')
            
            if not search_terms:
                search_terms = ['ALL']
            
            search_string = ' '.join(search_terms)
            search_type = "Gmail fallback" if is_gmail else "Standard IMAP"
            print(f"   📧 Will use {search_type} search: {search_string}")
        
        if is_gmail and 'gmail_query' in criteria and any(k in criteria for k in ['subject', 'from', 'date_after']):
            print(f"   💡 Note: Standard criteria present but Gmail query takes precedence")
    
    print("\n" + "=" * 55)
    print("Key Points:")
    print("• Gmail servers automatically use X-GM-RAW when 'gmail_query' is provided")
    print("• Gmail search falls back to standard IMAP if X-GM-RAW fails")  
    print("• Non-Gmail servers always use standard IMAP search")
    print("• Gmail queries support powerful operators: labels, categories, dates, etc.")
    print("• Standard IMAP is more limited but works with all email providers")


def show_gmail_query_examples():
    """Show practical Gmail query examples."""
    print("\n🎯 Practical Gmail Query Examples")
    print("=" * 40)
    
    examples = [
        {
            "use_case": "Sync work emails from last month",
            "query": "label:work after:2024/6/1 -label:archived"
        },
        {
            "use_case": "Process automated notifications", 
            "query": "from:notifications@github.com is:unread newer_than:7d"
        },
        {
            "use_case": "Find emails with large attachments",
            "query": "has:attachment larger:10MB after:2024/1/1"
        },
        {
            "use_case": "Sync important emails excluding spam",
            "query": "is:important -label:spam -label:trash -is:unread"
        },
        {
            "use_case": "Process emails from specific domain",
            "query": "from:@company.com category:primary -category:promotions"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['use_case']}:")
        print(f"   gmail_query: \"{example['query']}\"")
    
    print(f"\n💡 See GMAIL_SEARCH.md for comprehensive Gmail search documentation")


if __name__ == "__main__":
    demo_search_selection()
    show_gmail_query_examples()
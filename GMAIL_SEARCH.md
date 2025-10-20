# Gmail Search Guide

This guide explains how to use Gmail's powerful search syntax with the Email Sync tool.

## 🎯 Overview

When connecting to Gmail servers (`imap.gmail.com`), the Email Sync tool automatically uses Gmail's native search syntax (X-GM-RAW) for more powerful and accurate email filtering. This provides the same search capabilities as Gmail's web interface.

## 📁 Gmail Folder Optimization

**Important:** When using Gmail search with `gmail_query`, the script automatically optimizes folder selection:

- **Automatic All Mail Access**: Uses `[Gmail]/All Mail` folder for comprehensive search across all labels/folders
- **Fallback Handling**: Falls back to your configured folder if `[Gmail]/All Mail` is not accessible  
- **Cross-Label Search**: Gmail searches work across the entire mailbox, not just a single label

This means your `folder` configuration (like `"INBOX"`) acts as a fallback, but Gmail searches typically access all your mail regardless of labels.

## 📝 Gmail Search Syntax

### Basic Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `from:` | Sender email address | `from:boss@company.com` |
| `to:` | Recipient email address | `to:team@company.com` |
| `cc:` | CC recipient | `cc:manager@company.com` |
| `bcc:` | BCC recipient | `bcc:archive@company.com` |
| `subject:` | Subject line text | `subject:"Project Update"` |

### Date Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `after:` | Emails after date | `after:2024/1/15` |
| `before:` | Emails before date | `before:2024/12/31` |
| `older_than:` | Older than period | `older_than:30d` |
| `newer_than:` | Newer than period | `newer_than:7d` |

**Date Formats:**
- `YYYY/MM/DD` - `2024/3/15`
- `YYYY/M/D` - `2024/3/5` 
- Relative: `1d`, `2w`, `3m`, `1y` (days, weeks, months, years)

### Content Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `has:attachment` | Has attachments | `has:attachment` |
| `has:nouserlabels` | No user labels | `has:nouserlabels` |
| `is:important` | Marked important | `is:important` |
| `is:starred` | Starred emails | `is:starred` |
| `is:unread` | Unread emails | `is:unread` |
| `is:read` | Read emails | `is:read` |

### Label Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `label:` | Has specific label | `label:work` |
| `-label:` | Excludes label | `-label:spam` |
| `category:` | In category | `category:updates` |

**Common Labels:**
- `label:inbox`, `label:sent`, `label:drafts`
- `label:important`, `label:starred`
- `label:spam`, `label:trash`

**Categories:**
- `category:primary`, `category:social`, `category:updates`
- `category:forums`, `category:promotions`

### Advanced Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `filename:` | Attachment filename | `filename:pdf` |
| `larger:` | Size larger than | `larger:10MB` |
| `smaller:` | Size smaller than | `smaller:1MB` |
| `deliveredto:` | Delivered to address | `deliveredto:alias@gmail.com` |

### Boolean Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `OR` | Either condition | `from:a@b.com OR from:c@d.com` |
| `AND` | Both conditions | `from:boss@company.com AND has:attachment` |
| `-` | Exclude/NOT | `-label:spam -is:unread` |
| `()` | Grouping | `(from:a@b.com OR to:a@b.com) after:2024/1/1` |

## 🔧 Configuration Examples

### Simple Searches

**Find emails from specific sender:**
```json
{
  "search_criteria": {
    "gmail_query": "from:notifications@github.com"
  }
}
```

**Find emails with attachments:**
```json
{
  "search_criteria": {
    "gmail_query": "has:attachment"
  }
}
```

**Find unread emails from last week:**
```json
{
  "search_criteria": {
    "gmail_query": "is:unread newer_than:7d"
  }
}
```

### Date Range Searches

**Emails in specific date range:**
```json
{
  "search_criteria": {
    "gmail_query": "after:2024/1/1 before:2024/6/30"
  }
}
```

**Emails from last month:**
```json
{
  "search_criteria": {
    "gmail_query": "newer_than:1m older_than:1w"
  }
}
```

### Label and Category Searches

**Work emails excluding spam:**
```json
{
  "search_criteria": {
    "gmail_query": "label:work -label:spam -label:trash"
  }
}
```

**Newsletter and update emails:**
```json
{
  "search_criteria": {
    "gmail_query": "category:updates OR category:promotions"
  }
}
```

### Complex Searches

**Important emails from specific domain with attachments:**
```json
{
  "search_criteria": {
    "gmail_query": "from:@company.com is:important has:attachment -label:archived"
  }
}
```

**Emails from multiple senders in date range:**
```json
{
  "search_criteria": {
    "gmail_query": "(from:boss@company.com OR from:client@partner.com) after:2024/6/1 -is:unread"
  }
}
```

**Large emails with PDFs:**
```json
{
  "search_criteria": {
    "gmail_query": "filename:pdf larger:5MB after:2024/1/1"
  }
}
```

## 🔄 Fallback Behavior

If Gmail search fails or is not available, the tool automatically falls back to standard IMAP search:

```json
{
  "search_criteria": {
    "gmail_query": "from:sender@example.com after:2024/1/1",
    "subject": "Fallback Subject",
    "from": "sender@example.com",
    "date_after": "01-Jan-2024"
  }
}
```

## 💡 Best Practices

### 1. **Use Specific Queries**
```json
// Good - specific and efficient
"gmail_query": "from:automated@service.com label:notifications after:2024/1/1"

// Avoid - too broad, may match many emails  
"gmail_query": "has:attachment"
```

### 2. **Exclude Unwanted Content**
```json
// Exclude spam, trash, and archived emails
"gmail_query": "from:important@company.com -label:spam -label:trash -label:archived"
```

### 3. **Use Date Ranges for Performance**
```json
// Limit search to recent emails for better performance
"gmail_query": "from:sender@example.com after:2024/6/1"
```

### 4. **Test Queries in Gmail First**
Before using in the sync tool, test your queries in Gmail's web interface search box to ensure they return the expected results.

### 5. **Combine with Labels for Organization**
```json
// Process emails that are already labeled for sync
"gmail_query": "label:to-sync -label:synced"
```

## 🚨 Important Notes

1. **Gmail Search Priority**: When `gmail_query` is specified for Gmail servers, it takes precedence over standard IMAP criteria.

2. **Quotation Marks**: Use quotes for phrases: `subject:"Exact Subject Line"`

3. **Case Sensitivity**: Gmail search is generally case-insensitive.

4. **Label Names**: Use actual label names as they appear in Gmail. Spaces should be replaced with dashes or use quotes: `label:"My Label"` or `label:my-label`

5. **Special Characters**: Escape special characters in email addresses if needed.

## 📋 Quick Reference

**Most Common Gmail Queries for Email Sync:**

```bash
# Emails from specific sender, recent
from:sender@domain.com after:2024/6/1

# Unread emails with attachments  
is:unread has:attachment

# Emails in specific label, excluding processed ones
label:to-process -label:processed

# Emails from domain, excluding newsletters
from:@company.com -category:promotions

# Important emails in date range
is:important after:2024/1/1 before:2024/12/31
```

This powerful search capability makes Gmail email management much more precise and efficient compared to standard IMAP search limitations.
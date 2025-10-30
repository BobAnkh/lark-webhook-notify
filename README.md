# Lark Webhook Notify

A Python library for sending rich notifications to Lark (Feishu) webhooks with configurable templates and hierarchical configuration management.

## Features

- **Hierarchical Configuration**: TOML file -> Environment variables -> CLI arguments
- **Multiple Templates**: Legacy, modern, simple message, and alert templates
- **Rich Notifications**: Collapsible panels, status indicators, markdown support
- **Secure**: Proper HMAC-SHA256 signature generation
- **CLI Interface**: Command-line tool for quick notifications
- **Python API**: Comprehensive programmatic interface

## Installation

```bash
# Install from PyPI
pip install lark-webhook-notify
# Or if you are using uv
uv add lark-webhook-notify
```

## Quick Start

### 1. Configuration

Create a configuration file or set environment variables:

```toml
# lark_webhook.toml
lark_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL"
lark_webhook_secret = "YOUR_WEBHOOK_SECRET"
```

Or use environment variables:

```bash
export LARK_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL"
export LARK_WEBHOOK_SECRET="YOUR_WEBHOOK_SECRET"
```

### 2. Python API

```python
from lark_webhook_notify import send_task_notification, send_alert, send_simple_message

# Send task notification (cauldron compatible)
send_task_notification(
    task_name="deployment",
    status=0,  # 0=success, 1+=failed, None=running
    desc="Deploy application to production",
    group="artifacts",
    prefix="prod-deploy"
)

# Send alert notification
send_alert(
    alert_title="System Alert",
    alert_message="High memory usage detected on server",
    severity="warning"  # info, warning, error, critical
)

# Send simple message
send_simple_message(
    title="Build Complete",
    content="Application v2.1.0 built successfully ",
    color="green"
)
```

### 3. CLI Usage

```bash
# Task notifications
lark-weebhook-notify task "build-project" --desc "Building application" --status 0

# Alert notifications
lark-weebhook-notify alert "Service Down" "Database connection failed" --severity critical

# Simple messages
lark-weebhook-notify message "Hello" "This is a test message" --color blue

# List available templates
lark-weebhook-notify templates

# Test connection
lark-weebhook-notify test
```

## Configuration

### Configuration Hierarchy

Settings are loaded in order of precedence (highest to lowest):

1. **Command line arguments** / direct parameters
2. **Environment variables** (`LARK_WEBHOOK_URL`, `LARK_WEBHOOK_SECRET`)
3. **TOML file** (`lark_webhook.toml` by default)
4. **Default values**

### Configuration Files

#### TOML Configuration

```toml
# lark_webhook.toml
lark_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL"
lark_webhook_secret = "YOUR_WEBHOOK_SECRET"
```

#### Environment Variables

```bash
# Required
export LARK_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_URL"
export LARK_WEBHOOK_SECRET="YOUR_WEBHOOK_SECRET"
```

#### Custom Configuration

```python
from lark_webhook_notify import create_settings, LarkWebhookNotifier

# Custom TOML file
settings = create_settings(toml_file="/path/to/custom.toml")

# Direct parameters (highest priority)
settings = create_settings(
    webhook_url="https://example.com/webhook",
    webhook_secret="custom-secret"
)
```

## Templates

### Available Templates

| Template  | Description                                                    |
| --------- | -------------------------------------------------------------- |
| `start`   | Task start notifications                                       |
| `task`    | Rich card with collapsible panels to report the result of task |
| `legacy`  | Simple template (old version compatible)                       |
| `message` | Basic text message                                             |
| `alert`   | Severity-based styling                                         |
| `raw`     | Raw card content passthrough                                   |

## Blocks-Based Template Composition

To make building and customizing templates easier, the library provides a small set of reusable block helpers in `lark_webhook_notify.blocks`. Each function returns a dict matching Lark’s interactive card schema, and templates compose these blocks to form a complete card.

Blocks to use:

- `markdown(content, text_align='left', text_size='normal', margin='0px 0px 0px 0px')`
- `column(elements, width='auto', vertical_spacing='8px', horizontal_align='left', vertical_align='top', weight=None)`
- `column_set(columns, background_style='grey-100', horizontal_spacing='12px', horizontal_align='left', margin='0px 0px 0px 0px')`
- `collapsible_panel(title_markdown_content, elements, expanded=False, background_color='grey-200', border_color='grey', corner_radius='5px', vertical_spacing='8px', padding='8px 8px 8px 8px')`
- `header(title=..., template=..., subtitle=None, text_tag_list=None, padding=None)`
- `text_tag(text, color)`
- `config_textsize_normal_v2()`
- `card(elements=[...], header=..., schema='2.0', config=None)`
- `template_reference(template_id=..., template_version_name=..., template_variable={...})`

Example usage:

```python
from lark_webhook_notify.blocks import (
    markdown, column, column_set, collapsible_panel,
    header, card, text_tag, config_textsize_normal_v2,
)

elements = [
    markdown("Task metadata here..."),
    column_set([
        column([markdown("**Group**\nartifacts", text_align="center", text_size="normal_v2")], width="auto"),
        column([markdown("**Prefix**\ns3://bucket/path", text_align="center", text_size="normal_v2")], width="weighted", weight=1),
    ]),
    collapsible_panel(
        title_markdown_content="**<font color='grey-800'>Result Overview</font>**",
        elements=[markdown("- OK\n- Done", text_size="normal_v2")],
        expanded=False,
    ),
]

hdr = header(
    title="Task Completion Notification",
    subtitle="",
    template="green",
    text_tag_list=[text_tag("Completed", "green")],
)

content = card(elements=elements, header=hdr, schema='2.0', config=config_textsize_normal_v2())
```

You can send this `content` via `LarkWebhookNotifier.send_raw_content`. Built-in templates internally use these blocks, so extending or writing new templates is straightforward.

### Debug Mode

Enable debug logging for detailed information:

```bash
# CLI
lark-webhook-notify --debug test
```

```python
# Python
import logging
logging.getLogger("lark-webhook-notify").setLevel(logging.DEBUG)
```

### Getting Help

- Check the [Issues](https://github.com/BobAnkh/lark-webhook-notify/issues) page
- Review this documentation
- Enable debug mode for detailed error information

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure code passes linting (`uvx ruff check`) and format (`uvx ruff format`)
5. Submit a pull request

## License

Apache-2.0 License. See [LICENSE](LICENSE) for details.

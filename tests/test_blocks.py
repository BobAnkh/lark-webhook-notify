import json

from lark_webhook_notify.blocks import (
    markdown,
    column,
    column_set,
    collapsible_panel,
    header,
    card,
    text_tag,
    config_textsize_normal_v2,
    template_reference,
)


def test_markdown_defaults():
    blk = markdown("hello")
    assert blk["tag"] == "markdown"
    assert blk["content"] == "hello"
    assert blk["text_align"] == "left"
    assert blk["text_size"] == "normal"
    assert blk["margin"] == "0px 0px 0px 0px"


def test_markdown_custom():
    blk = markdown("hi", text_align="center", text_size="normal_v2", margin="1px")
    assert blk == {
        "tag": "markdown",
        "content": "hi",
        "text_align": "center",
        "text_size": "normal_v2",
        "margin": "1px",
    }


def test_header_optional_fields_omitted():
    h = header(title="Title", template="blue")
    assert h == {"title": {"tag": "plain_text", "content": "Title"}, "template": "blue"}

    # with optional fields
    ttag = text_tag("Running", "wathet")
    h2 = header(
        title="Title",
        template="wathet",
        subtitle="",
        text_tag_list=[ttag],
        padding="4px",
    )
    assert h2["subtitle"] == {"tag": "plain_text", "content": ""}
    assert h2["text_tag_list"] == [ttag]
    assert h2["padding"] == "4px"


def test_columns_and_set():
    c1 = column([markdown("A")], width="auto")
    c2 = column([markdown("B")], width="weighted", weight=1)
    cs = column_set([c1, c2])
    assert cs["tag"] == "column_set"
    assert len(cs["columns"]) == 2
    assert cs["columns"][1]["width"] == "weighted"
    assert cs["columns"][1]["weight"] == 1


def test_collapsible_panel_structure():
    p = collapsible_panel(
        "**Title**", [markdown("details", text_size="normal_v2")], expanded=False
    )
    assert p["tag"] == "collapsible_panel"
    assert p["expanded"] is False
    assert p["header"]["title"]["content"] == "**Title**"
    assert p["elements"][0]["text_size"] == "normal_v2"


def test_card_assembly_with_config():
    cfg = config_textsize_normal_v2()
    h = header(title="Hdr", template="green")
    c = card(elements=[markdown("X")], header=h, schema="2.0", config=cfg)
    # Ensure serializable and contains required sections
    json.dumps(c, ensure_ascii=False)
    assert c["schema"] == "2.0"
    assert c["header"]["title"]["content"] == "Hdr"
    assert c["body"]["elements"][0]["content"] == "X"
    assert c["config"]["style"]["text_size"]["normal_v2"]["mobile"] == "heading"


def test_template_reference_shape():
    ref = template_reference(
        template_id="TID",
        template_version_name="1.0.0",
        template_variable={"a": 1},
    )
    assert ref["type"] == "template"
    assert ref["data"]["template_id"] == "TID"
    assert ref["data"]["template_version_name"] == "1.0.0"
    assert ref["data"]["template_variable"]["a"] == 1

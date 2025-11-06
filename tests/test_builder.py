"""Tests for CardBuilder and workflow templates."""

import pytest
from lark_webhook_notify import (
    CardBuilder,
    GenericCardTemplate,
    WorkflowTemplates,
    create_custom_template,
)


class TestCardBuilder:
    """Test suite for CardBuilder class."""

    def test_simple_builder(self):
        """Test creating a simple template with builder."""
        template = (
            CardBuilder()
            .header("Test Title", status="success", color="green")
            .metadata("Key", "Value")
            .build()
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["schema"] == "2.0"
        assert "header" in card
        assert "body" in card

    def test_multiple_metadata(self):
        """Test adding multiple metadata rows."""
        template = (
            CardBuilder()
            .header("Test")
            .metadata("Key1", "Value1")
            .metadata("Key2", "Value2")
            .metadata("Key3", "Value3")
            .build()
        )

        card = template.generate()
        # Should have 3 metadata elements
        assert len(card["body"]["elements"]) == 3

    def test_columns(self):
        """Test column set functionality."""
        template = (
            CardBuilder()
            .header("Test")
            .columns()
            .column("Left", "Value1", width="auto")
            .column("Right", "Value2", width="weighted")
            .end_columns()
            .build()
        )

        card = template.generate()
        elements = card["body"]["elements"]
        assert len(elements) == 1
        assert elements[0]["tag"] == "column_set"

    def test_multiple_column_sets(self):
        """Test multiple column sets."""
        template = (
            CardBuilder()
            .header("Test")
            .columns()
            .column("A", "1")
            .column("B", "2")
            .end_columns()
            .columns()
            .column("C", "3")
            .column("D", "4")
            .end_columns()
            .build()
        )

        card = template.generate()
        elements = card["body"]["elements"]
        assert len(elements) == 2
        assert all(el["tag"] == "column_set" for el in elements)

    def test_collapsible(self):
        """Test collapsible panel functionality."""
        template = (
            CardBuilder()
            .header("Test")
            .collapsible("Title", "Content", expanded=False)
            .build()
        )

        card = template.generate()
        elements = card["body"]["elements"]
        assert len(elements) == 1
        assert elements[0]["tag"] == "collapsible_panel"
        assert elements[0]["expanded"] is False

    def test_multiple_collapsibles(self):
        """Test multiple collapsible panels."""
        template = (
            CardBuilder()
            .header("Test")
            .collapsible("Section 1", "Content 1", expanded=False)
            .collapsible("Section 2", "Content 2", expanded=True)
            .collapsible("Section 3", "Content 3", expanded=False)
            .build()
        )

        card = template.generate()
        elements = card["body"]["elements"]
        assert len(elements) == 3
        assert all(el["tag"] == "collapsible_panel" for el in elements)

    def test_markdown(self):
        """Test markdown block functionality."""
        template = (
            CardBuilder()
            .header("Test")
            .markdown("## Title")
            .markdown("Content")
            .build()
        )

        card = template.generate()
        elements = card["body"]["elements"]
        assert len(elements) == 2
        assert all(el["tag"] == "markdown" for el in elements)

    def test_divider(self):
        """Test divider functionality."""
        template = (
            CardBuilder()
            .header("Test")
            .markdown("Before")
            .divider()
            .markdown("After")
            .build()
        )

        card = template.generate()
        elements = card["body"]["elements"]
        assert len(elements) == 3

    def test_mixed_elements(self):
        """Test mixing different element types."""
        template = (
            CardBuilder()
            .header("Test", status="success")
            .metadata("Key", "Value")
            .columns()
            .column("A", "1")
            .column("B", "2")
            .end_columns()
            .markdown("Some text")
            .collapsible("Details", "More info")
            .build()
        )

        card = template.generate()
        elements = card["body"]["elements"]
        assert len(elements) == 4  # metadata, columns, markdown, collapsible

    def test_status_color_auto_detection(self):
        """Test automatic color detection from status."""
        test_cases = [
            ("running", "wathet"),
            ("success", "green"),
            ("completed", "green"),
            ("failed", "red"),
            ("error", "red"),
            ("warning", "orange"),
            ("info", "blue"),
        ]

        for status, expected_color in test_cases:
            template = CardBuilder().header("Test", status=status).build()
            card = template.generate()
            assert card["header"]["template"] == expected_color

    def test_language_setting(self):
        """Test language configuration."""
        template = CardBuilder(language="en").header("Test", status="success").build()

        assert template.language == "en"

    def test_unclosed_columns_error(self):
        """Test that unclosed column context raises error."""
        with pytest.raises(ValueError, match="Unclosed column context"):
            CardBuilder().header("Test").columns().column("A", "1").build()

    def test_column_without_context_error(self):
        """Test that column without context raises error."""
        with pytest.raises(
            ValueError, match="Call .columns\\(\\) before .column\\(\\)"
        ):
            CardBuilder().header("Test").column("A", "1").end_columns()

    def test_end_columns_without_context_error(self):
        """Test that end_columns without context raises error."""
        with pytest.raises(ValueError, match="No column context to end"):
            CardBuilder().header("Test").end_columns()

    def test_metadata_block(self):
        """Test metadata_block helper."""
        template = (
            CardBuilder()
            .header("Test")
            .metadata_block(task_name="my-task", duration="5m", status="complete")
            .build()
        )

        card = template.generate()
        elements = card["body"]["elements"]
        assert len(elements) == 1
        assert "Task Name" in elements[0]["content"]
        assert "Duration" in elements[0]["content"]
        assert "Status" in elements[0]["content"]

    def test_add_raw_block(self):
        """Test adding raw blocks."""
        from lark_webhook_notify.blocks import markdown

        raw_block = markdown("**Raw Content**")

        template = CardBuilder().header("Test").add_block(raw_block).build()

        card = template.generate()
        elements = card["body"]["elements"]
        assert len(elements) == 1
        assert elements[0]["tag"] == "markdown"
        assert "Raw Content" in elements[0]["content"]


class TestWorkflowTemplates:
    """Test suite for WorkflowTemplates factory class."""

    def test_network_submission_start(self):
        """Test network submission start template."""
        template = WorkflowTemplates.network_submission_start(
            network_set_name="test-networks",
            network_type="dynamic",
            group="test-group",
            prefix="s3://test/",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "wathet"  # running status

    def test_network_submission_complete(self):
        """Test network submission complete template."""
        template = WorkflowTemplates.network_submission_complete(
            network_set_name="test-networks",
            submitted_count=100,
            group="test-group",
            prefix="s3://test/",
            duration="5 minutes",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "green"  # success status

    def test_network_submission_failure(self):
        """Test network submission failure template."""
        template = WorkflowTemplates.network_submission_failure(
            network_set_name="test-networks",
            error_message="Connection timeout",
            submitted_count=50,
            group="test-group",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "red"  # failed status

    def test_config_upload_complete(self):
        """Test configuration upload template."""
        template = WorkflowTemplates.config_upload_complete(
            config_name="test-config",
            file_count=3,
            labels=["file1.json", "file2.yaml"],
            desc="Test configuration",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "green"

    def test_task_submission_start(self):
        """Test task submission start template."""
        template = WorkflowTemplates.job_submission_start(
            job_title="test-tasks",
            desc="Test task set description",
            group="test-group",
            prefix="s3://test/",
            metadata={
                "network_set_name": "test-networks",
                "iterations": 5,
                "config_name": "test-config",
            },
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "wathet"

    def test_task_submission_complete(self):
        """Test task submission complete template."""
        template = WorkflowTemplates.job_submission_complete(
            job_title="test-tasks",
            submitted_count=500,
            desc="Test task set description",
            group="test-group",
            prefix="s3://test/",
            duration="5 minutes",
            msg="| Task | Count |\n|:---|---:|\n| Total | 500 |",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "wathet"

    def test_task_submission_failure(self):
        """Test task submission failure template."""
        template = WorkflowTemplates.job_submission_failure(
            job_title="test-tasks",
            error_message="Scheduler unavailable",
            submitted_count=250,
            group="test-group",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "red"

    def test_task_set_progress(self):
        """Test task set progress template."""
        template = WorkflowTemplates.task_set_progress(
            task_sets_progress={
                "task-set-1": {"complete": 50, "total": 100},
                "task-set-2": {"complete": 75, "total": 100},
                "task-set-3": {"complete": 100, "total": 100},
            },
            overall_status="running",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "blue"

    def test_result_collection_start(self):
        """Test result collection start template."""
        template = WorkflowTemplates.result_collection_start(
            task_set_names=["task-set-1", "task-set-2", "task-set-3"],
            group="test-group",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "purple"

    def test_result_collection_complete(self):
        """Test result collection complete template."""
        template = WorkflowTemplates.result_collection_complete(
            task_set_names=["test-tasks"],
            job_title="test-tasks",
            group="test-group",
            prefix="s3://test/",
            msg="Collected 500 rows with 25 columns. Duration: 10 minutes",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "purple"

    def test_comparison_complete(self):
        """Test comparison complete template."""
        template = WorkflowTemplates.comparison_complete(
            comparison_name="baseline_vs_optimized",
            task_set_count=2,
            result_rows=45,
            result_columns=15,
            comparison_table="| Metric | Value |\n|:---|---:|\n| Improvement | 15.3% |",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "orange"

    def test_job_complete(self):
        """Test job complete template."""
        template = WorkflowTemplates.job_complete(
            job_title="test-job",
            success=True,
            status=0,
            group="test-group",
            prefix="s3://test/",
            desc="Test job description",
            msg="Job completed successfully",
            duration="5 minutes",
        )

        assert isinstance(template, GenericCardTemplate)
        card = template.generate()
        assert card["header"]["template"] == "green"


class TestCreateCustomTemplate:
    """Test suite for create_custom_template helper."""

    def test_create_custom_template(self):
        """Test create_custom_template helper function."""
        builder = create_custom_template()

        assert isinstance(builder, CardBuilder)
        assert builder._language == "zh"

    def test_create_custom_template_with_language(self):
        """Test create_custom_template with specific language."""
        builder = create_custom_template(language="en")

        assert isinstance(builder, CardBuilder)
        assert builder._language == "en"


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_complex_workflow_card(self):
        """Test creating a complex workflow card."""
        template = (
            CardBuilder()
            .header("Experiment Workflow Complete", status="success")
            .metadata("Experiment ID", "EXP-001")
            .metadata("Duration", "5.5 hours")
            .divider()
            .collapsible("Stage 1", "Network generation complete", expanded=False)
            .collapsible("Stage 2", "Tasks submitted", expanded=False)
            .collapsible("Stage 3", "Results collected", expanded=True)
            .divider()
            .columns()
            .column("Success Rate", "99%", width="auto")
            .column("Total Tasks", "500", width="auto")
            .end_columns()
            .build()
        )

        card = template.generate()
        assert card["schema"] == "2.0"
        assert "header" in card
        assert "body" in card
        elements = card["body"]["elements"]
        # metadata(2) + divider + collapsible(3) + divider + columns = 8
        assert len(elements) == 8

    def test_all_workflow_stages(self):
        """Test creating templates for all workflow stages."""
        templates = [
            WorkflowTemplates.network_submission_start(
                network_set_name="net-set",
                network_type="dynamic",
                group="group",
                prefix="prefix",
            ),
            WorkflowTemplates.network_submission_complete(
                network_set_name="net-set",
                submitted_count=100,
                group="group",
                prefix="prefix",
            ),
            WorkflowTemplates.job_submission_start(
                job_title="task-set",
                desc="test description",
                group="group",
                prefix="prefix",
            ),
            WorkflowTemplates.job_submission_complete(
                job_title="task-set",
                submitted_count=500,
                group="group",
                prefix="prefix",
            ),
            WorkflowTemplates.result_collection_complete(
                task_set_names=["task-set"], group="group", prefix="prefix"
            ),
            WorkflowTemplates.comparison_complete(
                comparison_name="comparison",
                task_set_count=2,
                result_rows=45,
                result_columns=15,
            ),
        ]

        for template in templates:
            assert isinstance(template, GenericCardTemplate)
            card = template.generate()
            assert card["schema"] == "2.0"
            assert "header" in card
            assert "body" in card

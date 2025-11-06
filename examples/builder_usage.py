"""Examples demonstrating the CardBuilder and WorkflowTemplates usage.

This file provides comprehensive examples of how to use the new flexible
template builder system for creating custom Lark notifications.
"""

from lark_webhook_notify import (
    CardBuilder,
    WorkflowTemplates,
    create_custom_template,
)


def example_1_simple_custom_template():
    """Example 1: Create a simple custom template with the builder."""
    print("=" * 60)
    print("Example 1: Simple Custom Template")
    print("=" * 60)

    template = (
        CardBuilder()
        .header("Task Complete", status="success", color="green")
        .metadata("Task Name", "data-processing")
        .metadata("Duration", "5 minutes")
        .metadata("Status Code", 0)
        .build()
    )

    print("Template created successfully!")
    print(f"Template type: {type(template).__name__}")
    return template


def example_2_multiple_collapsibles():
    """Example 2: Template with multiple collapsible sections."""
    print("\n" + "=" * 60)
    print("Example 2: Multiple Collapsible Sections")
    print("=" * 60)

    template = (
        CardBuilder()
        .header("Multi-Stage Analysis Results", status="success", color="green")
        .metadata("Analysis Name", "Performance Comparison")
        .metadata("Datasets Analyzed", 3)
        .metadata("Total Samples", 1500)
        .columns()
        .column("Group", "experiment-2024", width="auto")
        .column("Prefix", "s3://results/comparison/", width="weighted")
        .end_columns()
        # Multiple collapsible sections
        .collapsible(
            "Stage 1: Data Collection",
            "✓ Collected 1500 samples from 3 datasets\n✓ Validation complete\n✓ No missing data",
            expanded=False,
        )
        .collapsible(
            "Stage 2: Statistical Analysis",
            "✓ Mean improvement: 15.3%\n✓ P-value: 0.001\n✓ Effect size: 0.85",
            expanded=False,
        )
        .collapsible(
            "Stage 3: Results Summary",
            "| Metric | Before | After | Improvement |\n"
            "|:---|---:|---:|---:|\n"
            "| Throughput | 1000 | 1153 | +15.3% |\n"
            "| Latency | 50ms | 42ms | -16.0% |",
            expanded=True,
        )
        .build()
    )

    print("Template with multiple collapsibles created!")
    return template


def example_3_dynamic_metadata():
    """Example 3: Template with dynamically added metadata."""
    print("\n" + "=" * 60)
    print("Example 3: Dynamic Metadata")
    print("=" * 60)

    # Simulate dynamic data
    task_results = {
        "Network Count": 50,
        "Success Rate": "98%",
        "Failed Tasks": 1,
        "Average Duration": "3.5s",
        "Peak Memory": "2.1 GB",
    }

    builder = CardBuilder().header(
        "Task Batch Results", status="success", color="green"
    )

    # Add metadata dynamically
    for key, value in task_results.items():
        builder.metadata(key, value)

    builder.columns().column("Group", "production", width="auto").column(
        "Prefix", "s3://prod/results/", width="weighted"
    ).end_columns()

    template = builder.build()

    print(f"Template with {len(task_results)} dynamic metadata fields created!")
    return template


def example_4_multiple_column_sets():
    """Example 4: Template with multiple column sets."""
    print("\n" + "=" * 60)
    print("Example 4: Multiple Column Sets")
    print("=" * 60)

    template = (
        CardBuilder()
        .header("Network Comparison Results", status="success", color="green")
        .markdown("## Dataset Information")
        # First column set - Dataset info
        .columns()
        .column("Dataset A", "baseline-v1", width="auto")
        .column("Dataset B", "optimized-v2", width="auto")
        .column("Common Networks", "45", width="auto")
        .end_columns()
        .markdown("## Performance Summary")
        # Second column set - Performance metrics
        .columns()
        .column("Mean Improvement", "+15.3%", width="auto")
        .column("P-Value", "0.001", width="auto")
        .column("Effect Size", "0.85", width="weighted")
        .end_columns()
        .markdown("## Storage Information")
        # Third column set - Storage info
        .columns()
        .column("Group", "research-team", width="auto")
        .column("Prefix", "s3://results/comparison-2024/", width="weighted")
        .end_columns()
        .collapsible(
            "Detailed Statistics",
            "| Metric | Baseline | Optimized | Change |\n"
            "|:---|---:|---:|---:|\n"
            "| Throughput | 1000 ops/s | 1153 ops/s | +15.3% |\n"
            "| Latency | 50.0 ms | 42.0 ms | -16.0% |\n"
            "| Error Rate | 2.1% | 0.3% | -85.7% |",
            expanded=False,
        )
        .build()
    )

    print("Template with multiple column sets created!")
    return template


def example_5_low_level_blocks():
    """Example 5: Mixing high-level helpers with low-level blocks."""
    print("\n" + "=" * 60)
    print("Example 5: Low-Level Block Control")
    print("=" * 60)

    from lark_webhook_notify.blocks import markdown, column_set, column

    # Create custom blocks
    custom_column_set = column_set(
        [
            column([markdown("**Custom Left**\nValue 1")], width="auto"),
            column(
                [markdown("**Custom Middle**\nValue 2")], width="weighted", weight=2
            ),
            column([markdown("**Custom Right**\nValue 3")], width="auto"),
        ]
    )

    template = (
        CardBuilder()
        .header("Mixed-Level Template", status="info", color="blue")
        .metadata("Example", "Using raw blocks")
        # Use high-level helpers
        .markdown("### Section 1: High-Level Helpers")
        .columns()
        .column("Standard", "Column 1")
        .column("Standard", "Column 2")
        .end_columns()
        # Mix in low-level blocks
        .markdown("### Section 2: Custom Blocks")
        .add_block(custom_column_set)
        .add_block(markdown("*This is a custom markdown block*"))
        # Back to high-level helpers
        .collapsible("More Details", "Additional information here", expanded=False)
        .build()
    )

    print("Template with mixed-level blocks created!")
    return template


def example_6_workflow_templates():
    """Example 6: Using pre-built workflow templates."""
    print("\n" + "=" * 60)
    print("Example 6: Workflow Templates")
    print("=" * 60)

    # Network submission start
    template1 = WorkflowTemplates.network_submission_start(
        network_set_name="experiment-networks-2024",
        network_type="dynamic",
        group="research-team",
        prefix="s3://networks/experiment/",
        expected_count=100,
        metadata={"Experiment ID": "EXP-2024-001", "Topology": "Fat-Tree"},
    )
    print("✓ Network submission start template created")

    # Network submission complete
    template2 = WorkflowTemplates.network_submission_complete(
        network_set_name="experiment-networks-2024",
        submitted_count=100,
        group="research-team",
        prefix="s3://networks/experiment/",
        duration="2 minutes",
    )
    print("✓ Network submission complete template created")

    # Task submission start
    template3 = WorkflowTemplates.job_submission_start(
        job_title="evaluation-tasks-2024",
        desc="Evaluation task set for experiment networks",
        group="research-team",
        prefix="s3://tasks/evaluation/",
        msg="Submitting 500 tasks (100 networks × 5 iterations)\nConfig: standard-config-v2\nEstimated duration: 10 minutes",
        metadata={
            "network_set_name": "experiment-networks-2024",
            "iterations": 5,
            "config_name": "standard-config-v2",
        },
    )
    print("✓ Task submission start template created")

    # Task submission complete (matches StartTaskTemplate structure)
    template3_5 = WorkflowTemplates.job_submission_complete(
        job_title="evaluation-tasks-2024",
        submitted_count=500,
        desc="Evaluation task set for experiment networks",
        group="research-team",
        prefix="s3://tasks/evaluation/",
        duration="8 minutes",
        msg="All tasks successfully submitted to the scheduler\n"
        "| Task Type | Count |\n"
        "|:---|---:|\n"
        "| Compute | 400 |\n"
        "| Analysis | 100 |",
    )
    print("✓ Task submission complete template created")

    # Task set progress
    template4 = WorkflowTemplates.task_set_progress(
        task_sets_progress={
            "task-set-1": {"complete": 45, "total": 100},
            "task-set-2": {"complete": 80, "total": 100},
            "task-set-3": {"complete": 100, "total": 100},
        },
        overall_status="running",
    )
    print("✓ Task set progress template created")

    # Result collection complete
    template5 = WorkflowTemplates.result_collection_complete(
        task_set_names=["evaluation-tasks-2024"],
        job_title="evaluation-tasks-2024",
        group="research-team",
        prefix="s3://results/evaluation/",
        msg="Collected 500 results with 25 columns\nDuration: 5 minutes",
    )
    print("✓ Result collection complete template created")

    # Comparison complete with results table
    comparison_table = """| Metric | Baseline | Optimized | Improvement |
|:---|---:|---:|---:|
| Throughput | 1000 | 1153 | +15.3% |
| Latency | 50ms | 42ms | -16.0% |
| Error Rate | 2.1% | 0.3% | -85.7% |"""

    template6 = WorkflowTemplates.comparison_complete(
        comparison_name="baseline_vs_optimized",
        task_set_count=2,
        result_rows=45,
        result_columns=15,
        comparison_table=comparison_table,
    )
    print("✓ Comparison complete template created")

    print(f"\nCreated {7} workflow templates successfully!")
    return [
        template1,
        template2,
        template3,
        template3_5,
        template4,
        template5,
        template6,
    ]


def example_7_job_complete():
    """Example 7: Job completion template."""
    print("\n" + "=" * 60)
    print("Example 7: Job Completion Template")
    print("=" * 60)

    template = WorkflowTemplates.job_complete(
        job_title="evaluation-tasks-2024",
        success=True,
        status=0,
        group="research-team",
        prefix="s3://results/evaluation/",
        desc="Evaluation task set for experiment networks",
        msg="All tasks completed successfully\n"
        "| Metric | Value |\n"
        "|:---|---:|\n"
        "| Total Tasks | 500 |\n"
        "| Successful | 495 |\n"
        "| Failed | 5 |",
        duration="4.5 hours",
    )

    print("Job completion template created!")
    return template


def example_8_real_world_scenario():
    """Example 8: Real-world scenario - Complete workflow notification."""
    print("\n" + "=" * 60)
    print("Example 8: Real-World Complete Workflow")
    print("=" * 60)

    template = (
        create_custom_template()
        .header("Experiment Workflow Complete", status="success", color="green")
        .metadata("Experiment ID", "EXP-2024-001")
        .metadata("Start Time", "2024-11-05 10:00:00")
        .metadata("End Time", "2024-11-05 15:30:00")
        .metadata("Total Duration", "5.5 hours")
        .divider()
        .markdown("## Workflow Stages")
        # Stage 1
        .collapsible(
            "Stage 1: Network Generation",
            "✓ Generated 100 network configurations\n"
            "✓ Validation passed\n"
            "✓ Uploaded to S3\n"
            "⏱ Duration: 15 minutes",
            expanded=False,
        )
        # Stage 2
        .collapsible(
            "Stage 2: Task Submission",
            "✓ Submitted 500 tasks (100 networks × 5 iterations)\n"
            "✓ All tasks accepted by scheduler\n"
            "⏱ Duration: 10 minutes",
            expanded=False,
        )
        # Stage 3
        .collapsible(
            "Stage 3: Task Execution",
            "✓ 495 tasks completed successfully (99%)\n"
            "⚠ 5 tasks failed\n"
            "⏱ Duration: 4.5 hours",
            expanded=False,
        )
        # Stage 4
        .collapsible(
            "Stage 4: Result Collection",
            "✓ Collected 495 result files\n"
            "✓ Generated analysis dataset (495 rows × 28 columns)\n"
            "✓ Uploaded to S3\n"
            "⏱ Duration: 30 minutes",
            expanded=False,
        )
        # Stage 5
        .collapsible(
            "Stage 5: Statistical Analysis",
            "✓ Performed comparative analysis\n"
            "✓ Generated visualizations\n"
            "📊 Key Finding: 15.3% performance improvement observed\n"
            "⏱ Duration: 15 minutes",
            expanded=True,
        )
        .divider()
        .markdown("## Results Summary")
        .columns()
        .column("Success Rate", "99%", width="auto")
        .column("Total Tasks", "500", width="auto")
        .column("Failed Tasks", "5", width="auto")
        .end_columns()
        .columns()
        .column("Group", "research-team", width="auto")
        .column("Results", "s3://results/EXP-2024-001/", width="weighted")
        .end_columns()
        .build()
    )

    print("Complete workflow template created!")
    return template


def main():
    """Run all examples."""
    print("\n🚀 Lark Webhook Notify - CardBuilder Examples\n")

    # Run all examples
    examples = [
        example_1_simple_custom_template,
        example_2_multiple_collapsibles,
        example_3_dynamic_metadata,
        example_4_multiple_column_sets,
        example_5_low_level_blocks,
        example_6_workflow_templates,
        example_7_job_complete,
        example_8_real_world_scenario,
    ]

    templates = []
    for example_func in examples:
        try:
            result = example_func()
            if isinstance(result, list):
                templates.extend(result)
            else:
                templates.append(result)
        except Exception as e:
            print(f"❌ Error in {example_func.__name__}: {e}")

    print("\n" + "=" * 60)
    print(f"✅ Successfully created {len(templates)} templates!")
    print("=" * 60)

    # To actually send these templates, uncomment and configure:
    # notifier = LarkWebhookNotifier(
    #     webhook_url="your-webhook-url",
    #     webhook_secret="your-webhook-secret"
    # )
    # for template in templates:
    #     notifier.send_template(template)

    print(
        "\nℹ️  To send these templates, configure LarkWebhookNotifier with your credentials"
    )


if __name__ == "__main__":
    main()

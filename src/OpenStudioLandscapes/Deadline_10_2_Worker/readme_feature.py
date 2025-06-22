import textwrap
import snakemd


def readme_feature(
        doc: snakemd.Document
) -> snakemd.Document:

    ## Some Specific information

    doc.add_heading(
        text="Instructions",
        level=1,
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            This is an extension Feature for `OpenStudioLandscapes-Deadline-10-2`.
            For more information see the `README.md` there:
            """
        )
    )

    doc.add_unordered_list(
        [
            "[OpenStudioLandscapes-Deadline-10-2](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2)",
        ]
    )

    return doc


if __name__ == '__main__':
    pass

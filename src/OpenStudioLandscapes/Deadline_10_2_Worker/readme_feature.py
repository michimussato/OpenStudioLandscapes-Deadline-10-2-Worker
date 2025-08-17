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

    doc.add_heading(
        text="Known Issues",
        level=2,
    )

    "deadline-rcs-runner-10-2.farm.evil"

    doc.add_heading(
        text="Failed to establish connection to  due to a communication error.",
        level=3,
    )

    doc.add_block(
        block=snakemd.Code(
            textwrap.dedent(
                """
                deadline-10-2-pulse-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: ERROR: UpdateClient.MaybeSendRequestNow caught an exception: POST http://deadline-rcs-runner-10-2.farm.evil:8888/rcs/v1/update returned "One or more errors occurred. (Name or service not known (deadline-rcs-runner-10-2.farm.evil:8888))" (Deadline.Net.Clients.Http.DeadlineHttpRequestException)
                deadline-10-2-pulse-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: ERROR: DataController threw a configuration exception during initialization: Failed to establish connection to deadline-rcs-runner-10-2.farm.evil:8888 due to a communication error. (Deadline.Configuration.DeadlineConfigException)
                deadline-10-2-pulse-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: Could not connect to Deadline Repository: Failed to establish connection to deadline-rcs-runner-10-2.farm.evil:8888 due to a communication error.
                deadline-10-2-pulse-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: Deadline Pulse will try to connect again in 10 seconds...
                deadline-10-2-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: ERROR: UpdateClient.MaybeSendRequestNow caught an exception: POST http://deadline-rcs-runner-10-2.farm.evil:8888/rcs/v1/update returned "One or more errors occurred. (Name or service not known (deadline-rcs-runner-10-2.farm.evil:8888))" (Deadline.Net.Clients.Http.DeadlineHttpRequestException)
                deadline-10-2-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: ERROR: DataController threw a configuration exception during initialization: Failed to establish connection to deadline-rcs-runner-10-2.farm.evil:8888 due to a communication error. (Deadline.Configuration.DeadlineConfigException)
                deadline-10-2-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: Could not connect to Deadline Repository: Failed to establish connection to deadline-rcs-runner-10-2.farm.evil:8888 due to a communication error.
                deadline-10-2-worker-001--2025-07-24-13-27-17-332a6900a9cf452f9d58fa57d2b6195a: Deadline Worker will try to connect again in 10 seconds...
                """
            )
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            Make sure that the name gets resolved correctly.
            """
        )
    )

    doc.add_block(
        block=snakemd.Code(
            textwrap.dedent(
                """
                $ nslookup deadline-rcs-runner-10-2.farm.evil
                Server:         192.168.1.10
                Address:        192.168.1.10#53
                
                ** server can't find deadline-rcs-runner-10-2.farm.evil: NXDOMAIN
                """
            )
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            And add a DNS record or edit your `hosts` file so that
            `deadline-rcs-runner-10-2.farm.evil` gets resolved correctly,
            as in this example:
            """
        )
    )

    doc.add_block(
        block=snakemd.Code(
            textwrap.dedent(
                """
                $ nslookup deadline-rcs-runner-10-2.farm.evil
                Server:         192.168.1.10
                Address:        192.168.1.10#53
                
                deadline-rcs-runner-10-2.farm.evil      canonical name = lenovo.farm.evil.
                Name:   lenovo.farm.evil
                Address: 192.168.1.50
                """
            )
        )
    )

    return doc


if __name__ == '__main__':
    pass

import logging
import textwrap

from utils import trim_basedir, build_item_schema_link, load_raw_file


class ErrorReporter:
    def __init__(self, pr_comment_filename):
        self._pr_comment_filename = pr_comment_filename

    def report_general_error(self, error, _quit=True):
        logging.error("Reporting general runtime error%s", " and quitting" if _quit else "")

        lines = [
            "❌",
            "",
            "The build script encountered a runtime error which likely requires you to make file changes."
            + " More specific details may be present below:",
            "",
            error,
        ]

        self._write_error_lines(lines, _quit=_quit)

    def report_ajv_errors(self, validation_errors, input_dir, item_schema):
        logging.error("Reporting validation errors in %d file(s) and quitting", len(validation_errors))
        failing_filenames = ", ".join([trim_basedir(error[0], input_dir) for error in validation_errors])
        print(f"The following file(s) failed to validate - please fix them to match the schema: {failing_filenames}")

        lines = [
            "❌",
            "",
            "Some file(s) changed/added in this PR don't adhere to the [item data schema]"
            + f"({build_item_schema_link(item_schema)}). Please fix the errors detailed below for each file:",
            "",
        ]

        for filename, ajv_stderr in validation_errors:

            # trim out first line a-la "../items/belts/Headhunter.yml invalid"
            ajv_errors = "\n".join(ajv_stderr.strip().split("\n")[1:]).split(", ")
            formatted_errors = "\n".join(["Errors:"] + [f"• {err}" for err in ajv_errors])

            lines.extend(
                [
                    f"- `{trim_basedir(filename, input_dir)}`:",
                    "",
                    textwrap.indent(f"```yaml\n{load_raw_file(filename).strip()}\n```", "  "),
                    textwrap.indent(f"```\n{formatted_errors}\n```", "  "),
                    "",
                ]
            )

        self._write_error_lines(lines)

    def _write_error_lines(self, lines, _quit=True):
        self._write_pr_comment_file("\n".join(lines))

        if _quit:
            logging.info("Quitting after PR comment written")
            raise SystemExit(1)

    def _write_pr_comment_file(self, text):
        with open(self._pr_comment_filename, "w", encoding="utf-8") as f:
            f.write(text)
            logging.info(
                "Written pull request comment output to %s (%d lines in total)",
                self._pr_comment_filename,
                len(text.split("\n")),
            )

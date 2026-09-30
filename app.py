import streamlit as st
import ast
import subprocess
import tempfile
import os
import re

st.set_page_config(
    page_title="AI Code Review System",
    page_icon="🤖",
    layout="wide"
)

# =====================================================
# PAGE HEADER
# =====================================================

st.title("🤖 AI-Based Code Review System")

st.write(
    "An intelligent system for analyzing Python code "
    "for syntax, quality, security and improvement opportunities."
)

st.divider()

# =====================================================
# CODE INPUT
# =====================================================

st.subheader("💻 Enter Your Python Code")

code = st.text_area(
    "Paste your Python code below:",
    height=300,
    placeholder="""Example:

def add(a, b):
    return a + b

print(add(10, 20))"""
)

# =====================================================
# AI EXPLANATION ENGINE
# =====================================================

def explain_issue(issue):

    explanations = {

        "C0114":
            "The Python file is missing a module description. "
            "A short docstring explains the purpose of the program.",

        "C0116":
            "The function is missing a docstring. "
            "Adding one makes the function easier to understand.",

        "C0103":
            "A name does not follow normal Python naming conventions. "
            "Use clear and meaningful names.",

        "W0612":
            "A variable was created but its value is not used. "
            "Remove it if it is unnecessary.",

        "W0611":
            "An imported module does not appear to be used. "
            "Remove unused imports.",

        "C0303":
            "There is unnecessary whitespace at the end of a line. "
            "Removing it improves formatting.",

        "C0304":
            "The file is missing a final newline. "
            "Adding one follows standard Python conventions."
    }

    for code_id, explanation in explanations.items():

        if code_id in issue:
            return explanation

    return (
        "The analyzer identified a possible improvement. "
        "Review the reported issue and improve the affected "
        "part of the program."
    )


# =====================================================
# REVIEW BUTTON
# =====================================================

if st.button("🔍 Review Code", use_container_width=True):

    if not code.strip():

        st.warning("Please enter some Python code.")

    else:

        # =================================================
        # VARIABLES
        # =================================================

        syntax_error = False
        quality_output = ""
        security_output = ""

        # =================================================
        # 1. SYNTAX ANALYSIS
        # =================================================

        st.subheader("🔍 Syntax Analysis")

        try:

            ast.parse(code)

            st.success("✅ No syntax errors found!")

        except SyntaxError as error:

            syntax_error = True

            st.error("❌ Syntax Error Detected")

            st.write(f"**Line:** {error.lineno}")
            st.write(f"**Problem:** {error.msg}")

            st.info(
                "💡 Check the syntax around the line mentioned above."
            )

        # =================================================
        # 2. QUALITY ANALYSIS
        # =================================================

        st.subheader("📊 Code Quality Analysis")

        if syntax_error:

            st.warning(
                "Quality analysis skipped because the code "
                "contains a syntax error."
            )

        else:

            temp_file = None

            try:

                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".py",
                    delete=False,
                    encoding="utf-8"
                ) as file:

                    file.write(code)
                    temp_file = file.name

                result = subprocess.run(
                    [
                        "pylint",
                        temp_file,
                        "--disable=all",
                        "--enable=C,W,R",
                        "--score=no"
                    ],
                    capture_output=True,
                    text=True
                )

                quality_output = result.stdout.strip()

                if quality_output:

                    st.warning("⚠️ Code-quality issues found.")

                    st.code(quality_output)

                else:

                    st.success(
                        "✅ No major code-quality issues found!"
                    )

            except Exception as error:

                st.error(f"Quality analysis error: {error}")

            finally:

                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)

        # =================================================
        # 3. SECURITY ANALYSIS
        # =================================================

        st.subheader("🔐 Security Analysis")

        if syntax_error:

            st.warning(
                "Security analysis skipped because the code "
                "contains a syntax error."
            )

        else:

            security_file = None

            try:

                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".py",
                    delete=False,
                    encoding="utf-8"
                ) as file:

                    file.write(code)
                    security_file = file.name

                security_result = subprocess.run(
                    [
                        "bandit",
                        "-q",
                        security_file
                    ],
                    capture_output=True,
                    text=True
                )

                security_output = security_result.stdout.strip()

                if security_output:

                    st.warning(
                        "⚠️ Potential security issues detected."
                    )

                    st.code(security_output)

                else:

                    st.success(
                        "✅ No common security issues detected!"
                    )

            except Exception as error:

                st.error(
                    f"Security analysis error: {error}"
                )

            finally:

                if security_file and os.path.exists(security_file):
                    os.remove(security_file)

        # =================================================
        # 4. CALCULATE SCORES
        # =================================================

        quality_issue_count = 0

        if quality_output:

            for line in quality_output.splitlines():

                if re.search(r"[A-Z]\d{4}:", line):
                    quality_issue_count += 1

        security_issue_count = 0

        if security_output:

            security_issue_count = 1

        if syntax_error:

            syntax_score = 0
            quality_score = 0
            security_score = 0
            overall_score = 40

        else:

            syntax_score = 100

            quality_score = max(
                100 - (quality_issue_count * 10),
                0
            )

            security_score = (
                80 if security_issue_count > 0 else 100
            )

            overall_score = int(
                (syntax_score +
                 quality_score +
                 security_score) / 3
            )

        # =================================================
        # 5. DASHBOARD
        # =================================================

        st.divider()

        st.subheader("📊 Review Dashboard")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🔍 Syntax",
                f"{syntax_score}/100"
            )

        with col2:

            st.metric(
                "📊 Quality",
                f"{quality_score}/100"
            )

        with col3:

            st.metric(
                "🔐 Security",
                f"{security_score}/100"
            )

        st.divider()

        st.metric(
            "🎯 Overall Code Review Score",
            f"{overall_score}/100"
        )

        if overall_score >= 80:

            st.success(
                "🟢 Good code quality! Keep following clean "
                "and secure coding practices."
            )

        elif overall_score >= 60:

            st.warning(
                "🟡 Moderate code quality. Some improvements "
                "are recommended."
            )

        else:

            st.error(
                "🔴 Several improvements are recommended."
            )

        # =================================================
        # 6. AI REVIEW
        # =================================================

        st.divider()

        st.subheader("🤖 AI Review & Suggestions")

        issues = []

        if quality_output:

            for line in quality_output.splitlines():

                if re.search(r"[A-Z]\d{4}:", line):
                    issues.append(line)

        if security_output:

            for line in security_output.splitlines():

                if "Issue:" in line:
                    issues.append(line)

        if not issues:

            st.success(
                "🎉 No major issues were detected!"
            )

            st.info(
                "💡 Your code follows the basic checks "
                "used by this review system."
            )

        else:

            st.write(
                f"**{len(issues)} issue(s) identified.**"
            )

            for number, issue in enumerate(issues, 1):

                with st.expander(
                    f"⚠️ Issue {number}"
                ):

                    st.code(issue)

                    st.write(
                        "🤖 **AI Explanation:**"
                    )

                    st.info(
                        explain_issue(issue)
                    )

                    st.write(
                        "💡 **Recommendation:**"
                    )

                    st.success(
                        "Review the affected code and apply "
                        "the suggested improvement."
                    )

        # =================================================
        # 7. SUBMITTED CODE
        # =================================================

        st.divider()

        st.subheader("📝 Submitted Code")

        st.code(
            code,
            language="python"
        )
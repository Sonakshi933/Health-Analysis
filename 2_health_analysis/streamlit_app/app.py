from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

st.set_page_config(
    page_title="Blood Work Analyzer",
    layout="wide"
)

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

st.markdown("""
<style>
.scroll-box {
    height: 230px;
    overflow-y: auto;
    padding: 12px 16px;
    border: 1px solid #333;
    border-radius: 8px;
    background-color: #1e1e1e;
    font-size: 0.9rem;
    line-height: 1.6;
}

.scroll-box p,
.scroll-box li {
    color: #e0e0e0;
}

.section-label {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 6px;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)


st.title("Blood Work Analyzer")

left_col, right_col = st.columns([1, 1])


# LEFT COLUMN
with left_col:

    st.subheader("Blood Work Report")

    blood_report = st.text_area(
        label="Paste your report below",
        height=500,
        placeholder="Paste your blood work report here...",
        label_visibility="collapsed"
    )

    analyze_clicked = st.button(
        "Analyze",
        type="primary",
        use_container_width=True
    )


# RIGHT COLUMN
with right_col:

    st.subheader("Health Summary")

    health_box = st.empty()

    health_box.markdown(
        '<div class="scroll-box"></div>',
        unsafe_allow_html=True
    )

    st.subheader("Suggested Diet Plan")

    diet_box = st.empty()

    diet_box.markdown(
        '<div class="scroll-box"></div>',
        unsafe_allow_html=True
    )


# ANALYZE BUTTON
if analyze_clicked:

    if not blood_report.strip():

        with left_col:
            st.warning(
                "Please paste a blood work report before analyzing."
            )

    else:

        with st.spinner("Analyzing your blood work..."):

            # Stage 1: Extract and classify blood test values
            extraction_prompt = f"""
You are a medical data extraction assistant.

From the blood report below, extract ALL test values and classify each one as HIGH, LOW, or NORMAL
based on the reference ranges provided in the report.

Format your response as:

- Test Name: value | Status: HIGH/LOW/NORMAL | Reference: range

Blood Report:
{blood_report}
"""

            extraction_response = llm.invoke(
                extraction_prompt
            )

            extracted_values = extraction_response.content


            # Stage 2: Generate health summary and Indian diet plan
            diet_prompt = f"""
You are a clinical nutritionist specializing in Indian dietary habits.

Based on the blood work analysis below, provide two clearly separated sections.

SECTION 1 - HEALTH SUMMARY:

Write 4-5 lines explaining the patient's condition in simple,
easy-to-understand, non-technical language.

SECTION 2 - INDIAN DIET PLAN:

List foods to eat more of and foods to avoid.
Use commonly available Indian foods like dal, sabzi, roti, rice, fruits, vegetables, etc.
Keep the recommendations practical and concise.

Also include a short note that this information is for general educational purposes
and is not a substitute for advice from a qualified healthcare professional.

Blood Work Analysis:
{extracted_values}
"""

            diet_response = llm.invoke(
                diet_prompt
            )

            full_response = diet_response.content


        # Split response into two sections
        if "SECTION 2" in full_response:

            parts = full_response.split(
                "SECTION 2",
                1
            )

            health_summary = (
                parts[0]
                .replace(
                    "SECTION 1 - HEALTH SUMMARY:",
                    ""
                )
                .replace(
                    "SECTION 1",
                    ""
                )
                .strip()
            )

            diet_plan = (
                parts[1]
                .replace(
                    "- INDIAN DIET PLAN:",
                    ""
                )
                .replace(
                    "INDIAN DIET PLAN:",
                    ""
                )
                .strip()
            )

        else:

            health_summary = full_response
            diet_plan = ""


        # Display Health Summary
        health_box.markdown(
            f"""
            <div class="scroll-box">
                {health_summary}
            </div>
            """,
            unsafe_allow_html=True
        )


        # Display Diet Plan
        diet_box.markdown(
            f"""
            <div class="scroll-box">
                {diet_plan if diet_plan else full_response}
            </div>
            """,
            unsafe_allow_html=True
        )
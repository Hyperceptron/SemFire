import os
import sys
from typing import Optional, List
import streamlit as st

# Add the src directory to the Python path
# This is necessary for Streamlit to find the custom modules when run from
# the demo directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.semantic_firewall import SemanticFirewall
# from src.detectors.echo_chamber import EchoChamberDetector # Unused import

# Initialize the SemanticFirewall
# It should load its default detectors
try:
    firewall = SemanticFirewall()
except Exception as e:
    st.error(f"Error initializing SemanticFirewall: {e}")
    firewall = None  # Prevent further errors if initialization fails

st.set_page_config(page_title="A.E.G.I.S. Demo", layout="wide")

st.title("A.E.G.I.S: Active Encoding Guarding Injection Safety")
st.subheader("Interactive Semantic Firewall Demo")
st.markdown("""
    This demo allows you to interact with the `SemanticFirewall` (a key
    component of RADAR) to detect potential manipulative dialogues or harmful
    outputs. Enter a message and optionally provide conversation history to
    see the analysis.
""")

st.sidebar.header("About A.E.G.I.S")
st.sidebar.info("""
    **A.E.G.I.S (Active Encoding Guarding Injection Safety)** is a project
    focused on identifying and mitigating risks associated with advanced AI
    systems.

    The **`SemanticFirewall`** demonstrated here analyzes conversations in
    real-time. It uses various detectors, such as the `EchoChamberDetector`,
    to identify patterns associated with deception or manipulation.
""")
st.sidebar.markdown("---")
st.sidebar.header("Resources")
st.sidebar.markdown("""
    - [**Read the A.E.G.I.S Article on Substack**]\
(https://aptnative.substack.com/p/radar)
    - [**View the Project on GitHub**]\
(https://github.com/josephedward/A.E.G.I.S)
""")

st.header("Analyze Conversation")

current_message = st.text_area("Enter the current message:", height=100, key="current_message_input")
conversation_history_str = st.text_area(
    "Enter conversation history (one message per line, oldest first):",
    height=150,
    key="conversation_history_input"
)

if st.button("Analyze Message", key="analyze_button"):
    if not firewall:
        st.error("SemanticFirewall is not available due to an initialization error.")
    elif not current_message.strip():
        st.warning("Please enter a message to analyze.")
    else:
        history_list: Optional[List[str]] = None
        if conversation_history_str.strip():
            history_list = [
                msg.strip() for msg in conversation_history_str.split('\n')
                if msg.strip()
            ]

        with st.spinner("Analyzing..."):
            try:
                analysis_results = firewall.analyze_conversation(
                    current_message=current_message,
                    conversation_history=history_list
                )

                st.subheader("Analysis Results")
                st.write("The `SemanticFirewall` produced the following "
                         "analysis:")
                st.json(analysis_results)

                # Display spotlighting details for each detector if available
                st.subheader("Spotlight Analysis")
                for detector_name, details in analysis_results.items():
                    if isinstance(details, dict) and "spotlight" in details and details.get("spotlight"):
                        with st.expander(f"Spotlight Details from {detector_name}"):
                            spotlight_data = details["spotlight"]
                            if spotlight_data.get("highlighted_text"):
                                st.markdown("**Highlighted Text:**")
                                for text in spotlight_data["highlighted_text"]:
                                    st.warning(f"> {text}")
                            if spotlight_data.get("triggered_rules"):
                                st.markdown("**Triggered Rules:**")
                                st.json(spotlight_data["triggered_rules"])
                            if spotlight_data.get("explanation"):
                                st.markdown("**Explanation:**")
                                st.info(spotlight_data["explanation"])

                # Display details from EchoChamberDetector, including LLM analysis
                if "EchoChamberDetector" in analysis_results and isinstance(analysis_results.get("EchoChamberDetector"), dict):
                    with st.expander("Echo Chamber Detector Details"):
                        ecd_details = analysis_results["EchoChamberDetector"]
                        llm_status = ecd_details.get("llm_status", "status_not_available")
                        llm_analysis = ecd_details.get("llm_analysis", "analysis_not_available")
                        llm_model_name_display = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

                        status_map = {
                            "llm_model_not_loaded": f"Local LLM: Model Not Loaded ({llm_model_name_display})",
                            "llm_analysis_pending": "Local LLM: Analysis Pending...",
                            "llm_analysis_success": "Local LLM: Analysis Successful",
                            "llm_analysis_error": "Local LLM: Error During Analysis",
                            "status_not_available": "Local LLM: Status Not Available"
                        }
                        status_msg = status_map.get(llm_status, f"Local LLM: {llm_status.replace('_', ' ').title()}")

                        if llm_status == "llm_analysis_success":
                            st.success(status_msg)
                        elif llm_status in ["llm_model_not_loaded", "llm_analysis_error", "status_not_available"]:
                            st.warning(status_msg)
                        else:
                            st.info(status_msg)

                        st.markdown("**Local LLM Analysis Output:**")
                        st.text_area("LLM Output", value=llm_analysis, height=200, disabled=True, key="llm_output_display_area")
                        st.write("Echo Chamber Score:", ecd_details.get("echo_chamber_score"))
                        st.write("Classification:", ecd_details.get("classification"))
                        if ecd_details.get("detected_indicators"):
                            st.write("Detected Indicators:")
                            st.json(ecd_details.get("detected_indicators"))

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

st.markdown("---")
st.markdown(
    "For more information, refer to the project's README and documentation."
)

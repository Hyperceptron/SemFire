import streamlit as st
import sys
import os
from typing import Optional, List

# Add the src directory to the Python path
# This is necessary for Streamlit to find the custom modules when run from the demo directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.semantic_firewall import SemanticFirewall
# Assuming EchoChamberDetector is a primary detector used by SemanticFirewall or for direct use
from src.detectors.rule_based import EchoChamberDetector

# Initialize the SemanticFirewall
# It should load its default detectors, including EchoChamberDetector
try:
    firewall = SemanticFirewall()
except Exception as e:
    st.error(f"Error initializing SemanticFirewall: {e}")
    firewall = None # Prevent further errors if initialization fails

st.set_page_config(page_title="R.A.D.A.R. Demo", layout="wide")

st.title("RADAR: Recognizing Agentic Deception and Alignment Risk")
st.subheader("Interactive Semantic Firewall Demo")
st.markdown("""
    This demo allows you to interact with the `SemanticFirewall` (a key component of RADAR) to detect
    potential manipulative dialogues or harmful outputs.
    Enter a message and optionally provide conversation history to see the analysis.
""")

st.sidebar.header("About R.A.D.A.R.")
st.sidebar.info("""
    **RADAR (Recognizing Agentic Deception and Alignment Risk)** is a project focused on identifying and mitigating risks associated with advanced AI systems.
    
    The **`SemanticFirewall`** demonstrated here analyzes conversations in real-time. It uses various detectors, such as the `EchoChamberDetector`, to identify patterns associated with deception or manipulation.
""")
st.sidebar.markdown("---")
st.sidebar.header("Resources")
st.sidebar.markdown("""
    - [**Read the R.A.D.A.R. Article on Substack**](https://aptnative.substack.com/p/radar)
    - [**View the Project on GitHub**](https://github.com/josephedward/R.A.D.A.R.)
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
            history_list = [msg.strip() for msg in conversation_history_str.split('\n') if msg.strip()]

        with st.spinner("Analyzing..."):
            try:
                analysis_results = firewall.analyze_conversation(
                    current_message=current_message,
                    conversation_history=history_list
                )
                
                st.subheader("Analysis Results")
                st.write("The `SemanticFirewall` produced the following analysis:")
                st.json(analysis_results)

                # Optionally, display results from a specific detector if desired
                if "EchoChamberDetector" in analysis_results.get("details", {}):
                    st.subheader("Echo Chamber Detector Details")
                    ecd_details = analysis_results["details"]["EchoChamberDetector"]
                    
                    # Display raw JSON for all details from the detector
                    # st.json(ecd_details) # Uncomment if you want to see all raw details

                    # More prominent display for LLM status and analysis
                    llm_status = ecd_details.get("llm_status", "status_not_available")
                    llm_analysis = ecd_details.get("llm_analysis", "analysis_not_available")
                    
                    # Attempt to get LLM model name from firewall/detector if available
                    # This is a bit of a hack as the demo app doesn't directly know the detector's model name
                    # For now, we'll hardcode or omit it if not easily accessible.
                    # A better way would be for the detector to include its model name in its results.
                    llm_model_name_display = "TinyLlama/TinyLlama-1.1B-Chat-v1.0" # Placeholder

                    status_message_map = {
                        "model_not_loaded": f"Local LLM Status: Model Not Loaded ({llm_model_name_display})",
                        "analysis_pending": "Local LLM Status: Analysis Pending...",
                        "analysis_success": "Local LLM Status: Analysis Successful",
                        "analysis_empty_response": "Local LLM Status: Analysis Returned Empty Response",
                        "analysis_error": "Local LLM Status: Error During Analysis",
                        "status_not_available": "Local LLM Status: Not Available in Results"
                    }
                    status_display_message = status_message_map.get(llm_status, f"Local LLM Status: {llm_status.replace('_', ' ').title()}")

                    if llm_status == "analysis_success":
                        st.success(status_display_message)
                    elif llm_status in ["model_not_loaded", "analysis_error", "analysis_empty_response", "status_not_available"]:
                        st.warning(status_display_message)
                    else: # e.g. analysis_pending
                        st.info(status_display_message)
                    
                    st.markdown("**Local LLM Analysis Output:**")
                    st.text_area(
                        "LLM Output", 
                        value=llm_analysis, 
                        height=200, 
                        disabled=True, 
                        key="llm_output_display_area",
                        help="This is the analysis provided by the local LLM. Its quality depends on the model and the input."
                    )
                    # Display other parts of ecd_details if needed, for example, keyword-based results:
                    st.write("Keyword-based detection score:", ecd_details.get("echo_chamber_score"))
                    st.write("Keyword-based classification:", ecd_details.get("classification"))
                    if ecd_details.get("detected_indicators"):
                        st.write("Detected keyword indicators:")
                        st.json(ecd_details.get("detected_indicators"))


            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

st.markdown("---")
st.markdown("For more information, refer to the project's README and documentation.")

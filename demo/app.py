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
                # For example, if EchoChamberDetector is used and its results are distinct:
                if "EchoChamberDetector" in analysis_results.get("details", {}):
                    st.subheader("Echo Chamber Detector Details")
                    st.json(analysis_results["details"]["EchoChamberDetector"])

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

st.markdown("---")
st.markdown("For more information, refer to the project's README and documentation.")
